from pydantic import BaseModel, Field


class ComparisonRequest(BaseModel):
    dossier_id: str | None = None
    product_name: str
    market: str = "EU"
    dossier_text: str | None = None
    dossier_payload: dict = Field(default_factory=dict)


class ExtractedEntity(BaseModel):
    entity_type: str
    value: str
    normalized_value: str | None = None
    evidence: str | None = None


class RuleCitation(BaseModel):
    regulation_code: str
    article_ref: str
    article_title: str | None = None
    source_url: str | None = None


class Discrepancy(BaseModel):
    field: str
    current_value: str | None = None
    expected_value: str | None = None
    severity: str = "medium"
    reason: str
    citations: list[RuleCitation] = Field(default_factory=list)
    recommendation: str
    evidence: str | None = None


class ComparisonResponse(BaseModel):
    status: str
    market: str
    product_name: str
    mode: str
    extracted_entities: list[ExtractedEntity]
    relevant_rules_count: int
    discrepancies: list[Discrepancy]
    traceability: dict
    raw_assessment: dict | None = None


class CompareVersionRequest(BaseModel):
    dossier_text: str | None = None
    dossier_payload: dict = Field(default_factory=dict)
