import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Dossier(Base):
    __tablename__ = "dossiers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    root_dossier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id", ondelete="SET NULL"), nullable=True
    )
    superseded_by_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dossiers.id", ondelete="SET NULL"), nullable=True
    )

    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    product_name: Mapped[str] = mapped_column(Text, nullable=False)
    active_substance: Mapped[str | None] = mapped_column(Text, nullable=True)
    dosage_form: Mapped[str | None] = mapped_column(Text, nullable=True)
    strength: Mapped[str | None] = mapped_column(Text, nullable=True)
    market: Mapped[str] = mapped_column(String(50), nullable=False)
    dossier_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")

    source_file_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_file_hash: Mapped[str | None] = mapped_column(Text, nullable=True)

    extracted_entities: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    comparison_result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    legal_trace: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dossier_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    document_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
