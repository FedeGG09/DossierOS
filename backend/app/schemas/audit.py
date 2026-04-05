from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    dossier_id: str
    root_dossier_id: str | None = None
    action: str
    changed_by: str | None = None
    changed_by_email: str | None = None
    field_name: str | None = None
    old_value: dict | None = None
    new_value: dict | None = None
    legal_basis: dict
    source_file_name: str | None = None
    source_version: int | None = None
    note: str | None = None
    created_at: str
