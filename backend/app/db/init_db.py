from app.db.base import Base
from app.db.session import engine

# Importar modelos para registrar metadata
from app.models import Dossier, DossierAuditLog, ReglaUE  # noqa: F401


def create_all_tables():
    Base.metadata.create_all(bind=engine)
