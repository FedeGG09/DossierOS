from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.dossier import Dossier


class VersioningService:
    @staticmethod
    def create_new_version(
        db: Session,
        previous: Dossier,
        new_payload: dict,
        legal_trace: dict | None = None,
        notes: str | None = None,
    ) -> Dossier:
        root_id = previous.root_dossier_id or previous.id

        next_version = (
            db.query(func.max(Dossier.version_number))
            .filter(Dossier.root_dossier_id == root_id)
            .scalar()
            or previous.version_number
        ) + 1

        previous.is_current = False

        new_doc = Dossier(
            user_id=previous.user_id,
            root_dossier_id=root_id,
            previous_version_id=previous.id,
            version_number=next_version,
            is_current=True,
            product_name=previous.product_name,
            active_substance=previous.active_substance,
            dosage_form=previous.dosage_form,
            strength=previous.strength,
            market=previous.market,
            dossier_mode="update",
            status="draft",
            source_file_name=previous.source_file_name,
            source_file_type=previous.source_file_type,
            source_file_hash=previous.source_file_hash,
            extracted_entities=previous.extracted_entities,
            comparison_result=previous.comparison_result,
            legal_trace=legal_trace or previous.legal_trace,
            dossier_payload=new_payload,
            document_metadata=previous.document_metadata,
            notes=notes or previous.notes,
        )

        db.add(new_doc)
        db.flush()
        previous.superseded_by_version_id = new_doc.id
        return new_doc
