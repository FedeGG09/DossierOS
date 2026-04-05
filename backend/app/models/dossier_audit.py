import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DossierAuditLog(Base):
    __tablename__ = "dossier_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dossier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False)
    root_dossier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    action: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    changed_by_email: Mapped[str | None] = mapped_column(Text, nullable=True)

    field_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    legal_basis: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)

    source_file_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
