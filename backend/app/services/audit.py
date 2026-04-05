from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.dossier_audit import DossierAuditLog


class AuditService:
    @staticmethod
    def log_change(
        db: Session,
        dossier_id,
        root_dossier_id,
        action: str,
        changed_by=None,
        changed_by_email: str | None = None,
        field_name: str | None = None,
        old_value=None,
        new_value=None,
        legal_basis: list | dict | None = None,
        source_file_name: str | None = None,
        source_version: int | None = None,
        note: str | None = None,
    ):
        row = DossierAuditLog(
            dossier_id=dossier_id,
            root_dossier_id=root_dossier_id,
            action=action,
            changed_by=changed_by,
            changed_by_email=changed_by_email,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            legal_basis=legal_basis or [],
            source_file_name=source_file_name,
            source_version=source_version,
            note=note,
        )
        db.add(row)
        return row
