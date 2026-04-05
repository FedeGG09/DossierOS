from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    action: str = Field(..., description="create | update | correct")
    confidence: float = Field(..., ge=0, le=1)
    reason: str
    requires_human_review: bool = False
    target_dossier_id: str | None = None
    market: str | None = None
    product_name: str | None = None
    notes: str | None = None
