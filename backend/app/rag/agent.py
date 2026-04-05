from app.rag.prompts import SYSTEM_PROMPT
from app.schemas.agent import AgentDecision
from app.services.groq_client import GroqClient


class DossierAgent:
    def __init__(self):
        self.llm = GroqClient()

    def decide(self, user_input: str, dossier_context: dict | None = None) -> AgentDecision:
        context = dossier_context or {}

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\nClasifica la intención operativa del usuario."},
            {
                "role": "user",
                "content": f"""
Entrada del usuario:
{user_input}

Contexto del dossier existente:
{context}

Debes decidir una sola acción:
- create: generar desde cero
- update: modificar dossier existente
- correct: validar y corregir un dossier subido contra la normativa vigente

Devuelve JSON con:
{{
  "action": "create|update|correct",
  "confidence": 0.0,
  "reason": "..."
}}
""",
            },
        ]

        data = self.llm.chat_json(messages, temperature=0.0, max_tokens=800)

        action = (data.get("action") or "correct").lower()
        if action not in {"create", "update", "correct"}:
            action = "correct"

        try:
            confidence = float(data.get("confidence", 0.5))
        except Exception:
            confidence = 0.5

        return AgentDecision(
            action=action,
            confidence=max(0.0, min(1.0, confidence)),
            reason=data.get("reason", "Clasificación automática basada en el contenido."),
            requires_human_review=bool(data.get("requires_human_review", False)),
            target_dossier_id=data.get("target_dossier_id"),
            market=data.get("market"),
            product_name=data.get("product_name"),
            notes=data.get("notes"),
        )
