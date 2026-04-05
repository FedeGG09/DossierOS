from sqlalchemy.orm import Session

from app.models.regla_ue import ReglaUE
from app.services.embeddings import get_embedding_provider


class ReindexService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding = get_embedding_provider()

    def reindex_all(self):
        rules = self.db.query(ReglaUE).all()
        for rule in rules:
            rule.embedding = self.embedding.embed(rule.text_content)
        self.db.commit()

    def reindex_updated(self):
        rules = self.db.query(ReglaUE).filter(ReglaUE.embedding.is_(None)).all()
        for rule in rules:
            rule.embedding = self.embedding.embed(rule.text_content)
        self.db.commit()
