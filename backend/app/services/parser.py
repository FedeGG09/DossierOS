from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ExtractedEntity:
    entity_type: str
    value: str
    normalized_value: str | None = None
    evidence: str | None = None


API_PATTERNS = [
    r"(?:principio activo|sustancia activa|API)\s*[:\-]?\s*([A-Za-zÀ-ÿ0-9 .,'/\-]{2,120})",
    r"(?:active substance)\s*[:\-]?\s*([A-Za-zÀ-ÿ0-9 .,'/\-]{2,120})",
]

DOSAGE_PATTERNS = [
    r"(?:dosis|strength|concentración)\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?\s*(?:mg|g|mcg|µg|ml|mL|IU|UI))",
    r"([0-9]+(?:[.,][0-9]+)?\s*(?:mg|g|mcg|µg|ml|mL|IU|UI)\s*/\s*[0-9]+(?:[.,][0-9]+)?\s*(?:ml|mL))",
]

EXCIPIENT_PATTERNS = [
    r"(?:excipiente[s]?\s*[:\-]?\s*)([A-Za-zÀ-ÿ0-9 ,;()/.-]{2,200})",
]

PACKAGING_PATTERNS = [
    r"(?:envase|empaque|packaging material)\s*[:\-]?\s*([A-Za-zÀ-ÿ0-9 ,;()/.-]{2,200})",
]


def _find(patterns: list[str], text: str, entity_type: str) -> list[ExtractedEntity]:
    results: list[ExtractedEntity] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            value = match.group(1).strip()
            results.append(
                ExtractedEntity(
                    entity_type=entity_type,
                    value=value,
                    normalized_value=value.lower(),
                    evidence=match.group(0).strip(),
                )
            )
    return results


def extract_entities(text: str) -> list[ExtractedEntity]:
    if not text:
        return []
    entities: list[ExtractedEntity] = []
    entities.extend(_find(API_PATTERNS, text, "api"))
    entities.extend(_find(DOSAGE_PATTERNS, text, "dosage"))
    entities.extend(_find(EXCIPIENT_PATTERNS, text, "excipient"))
    entities.extend(_find(PACKAGING_PATTERNS, text, "packaging_material"))

    seen = set()
    deduped: list[ExtractedEntity] = []
    for e in entities:
        key = (e.entity_type, e.normalized_value or e.value.lower())
        if key not in seen:
            seen.add(key)
            deduped.append(e)
    return deduped
