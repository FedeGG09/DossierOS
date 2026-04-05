import uuid
from sqlalchemy import Date, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.db.base import Base


class ReglaUE(Base):
    __tablename__ = "reglas_ue"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    regulation_code: Mapped[str] = mapped_column(Text, nullable=False)
    regulation_name: Mapped[str] = mapped_column(Text, nullable=False)
    article_ref: Mapped[str] = mapped_column(Text, nullable=False)
    article_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    market: Mapped[str] = mapped_column(String(50), nullable=False, default="EU")
    scope_tags: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    effective_from: Mapped[str | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[str | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    numeric_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prohibited_terms: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    source_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(settings.embedding_dim), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
