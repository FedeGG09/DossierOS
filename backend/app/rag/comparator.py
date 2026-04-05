from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.regla_ue import ReglaUE
from app.rag.prompts import SYSTEM_PROMPT
from app.rag.retriever import NormativeRetriever
from app.schemas.comparison import ComparisonResponse, Discrepancy, ExtractedEntity, RuleCitation
from app.services.embeddings import EmbeddingProvider
from app.services.groq_client import GroqClient
from app.services.parser import extract_entities


def _as_entity_models(entities) -> list[ExtractedEntity]:
    return [
        ExtractedEntity(
            entity_type=e.entity_type,
            value=e.value,
            normalized_value=e.normalized_value,
            evidence=e.evidence,
        )
        for e in entities
    ]


class DossierComparator:
    def __init__(self, db: Session, embedding_provider: EmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider
        self.retriever = NormativeRetriever(db, embedding_provider)
        self.llm = GroqClient()

    def compare(self, product_name: str, market: str, dossier_text: str | None, dossier_payload: dict | None = None) -> ComparisonResponse:
        dossier_payload = dossier_payload or {}
        text = dossier_text or str(dossier_payload)

        extracted = extract_entities(text)
        extracted_models = _as_entity_models(extracted)

        query_text = f"{product_name} {market} {text[:4000]}"
        rules = self.retriever.fetch_relevant_rules(query_text=query_text, market=market, limit=10)

        deterministic_discrepancies = self._deterministic_check(extracted, rules)
        llm_assessment = self._llm_refine(product_name, market, text, rules, extracted_models, deterministic_discrepancies)
        merged = self._merge_findings(deterministic_discrepancies, llm_assessment.get("findings", []))

        traceability = {
            "retrieval_strategy": "pgvector_cosine + metadata_filters",
            "market": market,
            "rules_used": [
                {
                    "regulation_code": r.regulation_code,
                    "article_ref": r.article_ref,
                    "article_title": r.article_title,
                    "rule_type": r.rule_type,
                    "source_url": r.source_url,
                }
                for r in rules
            ],
        }

        return ComparisonResponse(
            status=llm_assessment.get("status", "ok"),
            market=market,
            product_name=product_name,
            mode="correct",
            extracted_entities=extracted_models,
            relevant_rules_count=len(rules),
            discrepancies=merged,
            traceability=traceability,
            raw_assessment=llm_assessment,
        )

    def _deterministic_check(self, entities, rules: list[ReglaUE]) -> list[Discrepancy]:
        findings: list[Discrepancy] = []

        excipients = [e for e in entities if e.entity_type == "excipient"]
        dosages = [e for e in entities if e.entity_type == "dosage"]
        packaging = [e for e in entities if e.entity_type == "packaging_material"]

        for exc in excipients:
            for rule in rules:
                forbidden = rule.prohibited_terms or []
                joined = " ".join([str(x).lower() for x in forbidden])
                if exc.value.lower() in joined or (exc.normalized_value and exc.normalized_value in joined):
                    findings.append(
                        Discrepancy(
                            field="excipient",
                            current_value=exc.value,
                            expected_value="No debe incluir excipientes prohibidos para el mercado objetivo.",
                            severity="high",
                            reason=f"Excipient detectado en conflicto con la regla {rule.article_ref}.",
                            citations=[RuleCitation(
                                regulation_code=rule.regulation_code,
                                article_ref=rule.article_ref,
                                article_title=rule.article_title,
                                source_url=rule.source_url,
                            )],
                            recommendation=f"Eliminar o sustituir '{exc.value}' y validar reformulación.",
                            evidence=exc.evidence,
                        )
                    )

        for d in dosages:
            for rule in rules:
                if rule.numeric_limit is not None:
                    findings.append(
                        Discrepancy(
                            field="dosage",
                            current_value=d.value,
                            expected_value=f"<= {rule.numeric_limit} {rule.unit or ''}".strip(),
                            severity="medium",
                            reason=f"Se requiere contraste formal con el límite indicado en {rule.article_ref}.",
                            citations=[RuleCitation(
                                regulation_code=rule.regulation_code,
                                article_ref=rule.article_ref,
                                article_title=rule.article_title,
                                source_url=rule.source_url,
                            )],
                            recommendation="Verificar la dosis declarada con el texto normativo vigente y ajustar la etiqueta/dossier.",
                            evidence=d.evidence,
                        )
                    )

        for p in packaging:
            for rule in rules:
                if rule.rule_type == "packaging":
                    findings.append(
                        Discrepancy(
                            field="packaging_material",
                            current_value=p.value,
                            expected_value="Material compatible con la norma aplicable del mercado objetivo.",
                            severity="medium",
                            reason=f"El material de empaque debe validarse contra {rule.article_ref}.",
                            citations=[RuleCitation(
                                regulation_code=rule.regulation_code,
                                article_ref=rule.article_ref,
                                article_title=rule.article_title,
                                source_url=rule.source_url,
                            )],
                            recommendation="Confirmar compatibilidad regulatoria y evidencia de estabilidad / contacto.",
                            evidence=p.evidence,
                        )
                    )

        return findings

    def _llm_refine(self, product_name: str, market: str, text: str, rules: list[ReglaUE], extracted_entities: list[ExtractedEntity], deterministic_findings: list[Discrepancy]) -> dict:
        rule_context = [
            {
                "regulation_code": r.regulation_code,
                "article_ref": r.article_ref,
                "article_title": r.article_title,
                "rule_type": r.rule_type,
                "text_content": r.text_content[:1200],
                "source_url": r.source_url,
            }
            for r in rules
        ]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Producto: {product_name}
Mercado: {market}

Texto del dossier:
{text[:12000]}

Entidades extraídas:
{[e.model_dump() for e in extracted_entities]}

Hallazgos determinísticos:
{[d.model_dump() for d in deterministic_findings]}

Normativa relevante:
{rule_context}

Tarea:
1) Detecta discrepancias normativas.
2) Para cada hallazgo, cita el artículo específico.
3) Responde solo JSON con estructura:
{{
  "status": "ok|needs_review|blocked",
  "summary": "...",
  "findings": [
    {{
      "field": "...",
      "issue": "...",
      "recommendation": "...",
      "severity": "low|medium|high|critical",
      "citations": [
        {{
          "regulation_code": "...",
          "article_ref": "...",
          "article_title": "...",
          "source_url": "..."
        }}
      ],
      "evidence": "..."
    }}
  ],
  "requires_human_review": false
}}
""",
            },
        ]
        return self.llm.chat_json(messages, temperature=0.0, max_tokens=2500)

    def _merge_findings(self, deterministic: list[Discrepancy], llm_findings: list[dict]) -> list[Discrepancy]:
        merged: list[Discrepancy] = []

        def key_of_item(item):
            if isinstance(item, Discrepancy):
                return (item.field, item.reason[:120])
            return (item.get("field"), (item.get("issue", "") or item.get("reason", ""))[:120])

        seen = set()
        for d in deterministic:
            k = key_of_item(d)
            if k not in seen:
                seen.add(k)
                merged.append(d)

        for item in llm_findings or []:
            k = key_of_item(item)
            if k in seen:
                continue
            seen.add(k)
            citations = [RuleCitation(**c) for c in item.get("citations", []) if isinstance(c, dict)]
            merged.append(
                Discrepancy(
                    field=item.get("field", "unknown"),
                    current_value=item.get("current_value"),
                    expected_value=item.get("expected_value"),
                    severity=item.get("severity", "medium"),
                    reason=item.get("issue") or item.get("reason") or "Hallazgo regulatorio.",
                    citations=citations,
                    recommendation=item.get("recommendation", ""),
                    evidence=item.get("evidence"),
                )
            )
        return merged
