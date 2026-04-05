from pydantic import BaseModel, Field


class DossierBase(BaseModel):
    product_name: str
    active_substance: str | None = None
    dosage_form: str | None = None
    strength: str | None = None
    market: str = "EU"
    dossier_mode: str = Field(..., description="create | update | correct")
    notes: str | None = None
    dossier_payload: dict = Field(default_factory=dict)


class DossierCreateRequest(DossierBase):
    source_file_name: str | None = None
    source_file_type: str | None = None


class DossierUpdateRequest(DossierBase):
    dossier_id: str
    updated_payload: dict = Field(default_factory=dict)


class DossierResponse(BaseModel):
    id: str
    root_dossier_id: str | None = None
    previous_version_id: str | None = None
    version_number: int
    product_name: str
    market: str
    dossier_mode: str
    status: str
    extracted_entities: dict
    comparison_result: dict
    legal_trace: dict
    dossier_payload: dict

    class Config:
        from_attributes = True
