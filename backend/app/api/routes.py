from __future__ import annotations

import io
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Request, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.deps.auth import get_current_claims, get_current_user_id, get_rls_db, require_admin
from app.jobs.reindex import ReindexService
from app.models.dossier import Dossier
from app.rag.agent import DossierAgent
from app.rag.comparator import DossierComparator
from app.schemas.agent import AgentDecision
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.schemas.dossier import DossierCreateRequest, DossierResponse
from app.services.audit import AuditService
from app.services.ema_ingestion import EMAIngestionService
from app.services.embeddings import get_embedding_provider
from app.services.versioning import VersioningService

router = APIRouter(prefix="/api/v1", tags=["qualipharma"])


def _read_upload(file: UploadFile) -> str:
    content = file.file.read()

    lower = file.filename.lower()
    if lower.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if len(text.strip()) < 50:
                from app.services.ocr import OCRService
                text = OCRService.extract_text(content)
            return text
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"No se pudo leer el PDF: {exc}")

    if lower.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"No se pudo leer el DOCX: {exc}")

    return content.decode("utf-8", errors="ignore")


@router.get("/health")
def health():
    return {"status": "ok", "service": "qualipharma-backend"}


@router.post("/agent/decision", response_model=AgentDecision)
def decide_action(payload: dict):
    user_input = payload.get("user_input", "")
    dossier_context = payload.get("dossier_context", {})
    agent = DossierAgent()
    return agent.decide(user_input=user_input, dossier_context=dossier_context)


@router.post("/dossiers/create", response_model=DossierResponse)
def create_dossier(
    payload: DossierCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    claims: dict = Depends(get_current_claims),
    db: Session = Depends(get_rls_db),
):
    embedding_provider = get_embedding_provider()
    comparator = DossierComparator(db, embedding_provider)

    comparison = comparator.compare(
        product_name=payload.product_name,
        market=payload.market,
        dossier_text=str(payload.dossier_payload),
        dossier_payload=payload.dossier_payload,
    )

    new_dossier = Dossier(
        user_id=user_id,
        product_name=payload.product_name,
        active_substance=payload.active_substance,
        dosage_form=payload.dosage_form,
        strength=payload.strength,
        market=payload.market,
        dossier_mode="create",
        status="draft",
        source_file_name=payload.source_file_name,
        source_file_type=payload.source_file_type,
        extracted_entities={"entities": [e.model_dump() for e in comparison.extracted_entities]},
        comparison_result=comparison.model_dump(),
        legal_trace=comparison.traceability,
        dossier_payload=payload.dossier_payload,
        document_metadata={"user_id": str(user_id), "email": claims.get("email")},
        notes=payload.notes,
    )

    db.add(new_dossier)
    db.flush()

    AuditService.log_change(
        db=db,
        dossier_id=new_dossier.id,
        root_dossier_id=new_dossier.root_dossier_id or new_dossier.id,
        action="create",
        changed_by=user_id,
        changed_by_email=claims.get("email"),
        note="Initial dossier creation",
        legal_basis=comparison.traceability,
    )

    db.commit()
    db.refresh(new_dossier)
    return new_dossier


@router.post("/dossiers/compare", response_model=ComparisonResponse)
def compare_dossier(
    payload: ComparisonRequest,
    db: Session = Depends(get_rls_db),
):
    if not payload.dossier_text and not payload.dossier_payload:
        raise HTTPException(status_code=400, detail="Se requiere dossier_text o dossier_payload.")

    embedding_provider = get_embedding_provider()
    comparator = DossierComparator(db, embedding_provider)

    return comparator.compare(
        product_name=payload.product_name,
        market=payload.market,
        dossier_text=payload.dossier_text,
        dossier_payload=payload.dossier_payload,
    )


@router.post("/dossiers/compare-upload", response_model=ComparisonResponse)
async def compare_upload(
    product_name: str,
    market: str = "EU",
    file: UploadFile = File(...),
    db: Session = Depends(get_rls_db),
):
    dossier_text = _read_upload(file)
    embedding_provider = get_embedding_provider()
    comparator = DossierComparator(db, embedding_provider)

    return comparator.compare(
        product_name=product_name,
        market=market,
        dossier_text=dossier_text,
        dossier_payload={"file_name": file.filename},
    )


@router.post("/dossiers/{dossier_id}/version", response_model=dict)
def create_version(
    dossier_id: str,
    payload: dict,
    user_id: UUID = Depends(get_current_user_id),
    claims: dict = Depends(get_current_claims),
    db: Session = Depends(get_rls_db),
):
    previous = db.get(Dossier, dossier_id)
    if not previous:
        raise HTTPException(status_code=404, detail="Dossier not found")
    if previous.user_id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    new_version = VersioningService.create_new_version(
        db=db,
        previous=previous,
        new_payload=payload,
        notes="Version created from regulatory update",
    )

    AuditService.log_change(
        db=db,
        dossier_id=new_version.id,
        root_dossier_id=new_version.root_dossier_id,
        action="version_create",
        changed_by=user_id,
        changed_by_email=claims.get("email"),
        note="New dossier version created",
        legal_basis=new_version.legal_trace,
    )

    db.commit()
    db.refresh(new_version)

    return {
        "status": "ok",
        "dossier_id": str(new_version.id),
        "version_number": new_version.version_number,
        "root_dossier_id": str(new_version.root_dossier_id) if new_version.root_dossier_id else None,
    }


@router.post("/admin/reindex")
def reindex(
    request: Request,
    db: Session = Depends(get_db),
):
    require_admin(request)
    service = ReindexService(db)
    service.reindex_all()
    return {"status": "reindexed"}


@router.post("/admin/ingest-ema")
async def ingest_ema(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    require_admin(request)
    content = file.file.read()
    service = EMAIngestionService(db)
    count = service.ingest_pdf(content, source_url=file.filename)
    return {"inserted_rules": count}
