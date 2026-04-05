from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.regla_ue import ReglaUE
from app.services.embeddings import EmbeddingProvider


class NormativeRetriever:
    def __init__(self, db: Session, embedding_provider: EmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider

    def fetch_relevant_rules(
        self,
        query_text: str,
        market: str = "EU",
        rule_type: str | None = None,
        limit: int = 8,
    ) -> list[ReglaUE]:
        query_vec = self.embedding_provider.embed(query_text)

        stmt = select(ReglaUE).where(ReglaUE.status == "active").where(ReglaUE.embedding.is_not(None))

        if market:
            stmt = stmt.where(ReglaUE.market.in_([market, "EU"]))
        if rule_type:
            stmt = stmt.where(ReglaUE.rule_type == rule_type)

        stmt = stmt.order_by(ReglaUE.embedding.cosine_distance(query_vec)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def fetch_by_metadata(
        self,
        market: str = "EU",
        rule_type: str | None = None,
        scope_tag: str | None = None,
        limit: int = 10,
    ) -> list[ReglaUE]:
        stmt = select(ReglaUE).where(ReglaUE.status == "active").where(ReglaUE.embedding.is_not(None))

        if market:
            stmt = stmt.where(ReglaUE.market.in_([market, "EU"]))
        if rule_type:
            stmt = stmt.where(ReglaUE.rule_type == rule_type)
        if scope_tag:
            stmt = stmt.where(ReglaUE.scope_tags.contains([scope_tag]))

        stmt = stmt.order_by(desc(ReglaUE.created_at)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
