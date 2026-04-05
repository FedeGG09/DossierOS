from __future__ import annotations

import hashlib
import io
import re
from typing import List

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.regla_ue import ReglaUE
from app.services.embeddings import get_embedding_provider
from app.services.ocr import OCRService


class EMAIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding = get_embedding_provider()

    def ingest_pdf(self, file_bytes: bytes, source_url: str = "", use_ocr_fallback: bool = True) -> int:
        text = self._extract_text(file_bytes, use_ocr_fallback=use_ocr_fallback)
        chunks = self._chunk_text(text, size=1200)

        inserted = 0
        for idx, chunk in enumerate(chunks, start=1):
            if not chunk.strip():
                continue
            rule = self._build_rule(chunk, source_url=source_url, chunk_index=idx)
            self.db.add(rule)
            inserted += 1

        self.db.commit()
        return inserted

    def _extract_text(self, file_bytes: bytes, use_ocr_fallback: bool = True) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if use_ocr_fallback and len(full_text.strip()) < 100:
            try:
                return OCRService.extract_text(file_bytes)
            except Exception:
                return full_text
        return full_text

    def _chunk_text(self, text: str, size: int = 1200) -> List[str]:
        return [text[i : i + size] for i in range(0, len(text), size)]

    def _extract_article(self, text: str) -> str:
        match = re.search(r"(Art\.?\s*\d+[\w\(\)]*)", text, flags=re.IGNORECASE)
        return match.group(1) if match else "UNKNOWN"

    def _classify_rule_type(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["excipient", "excipients"]):
            return "excipient"
        if any(k in t for k in ["packaging", "container", "closure", "blister"]):
            return "packaging"
        if any(k in t for k in ["dose", "dosage", "strength", "posology"]):
            return "dosage"
        if any(k in t for k in ["label", "labelling", "package leaflet"]):
            return "labeling"
        if any(k in t for k in ["composition", "qualitative", "quantitative"]):
            return "composition"
        return "general"

    def _build_rule(self, text: str, source_url: str, chunk_index: int) -> ReglaUE:
        hash_ = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return ReglaUE(
            regulation_code="EMA_AUTO",
            regulation_name="EMA Imported Regulation",
            article_ref=self._extract_article(text),
            article_title=None,
            rule_type=self._classify_rule_type(text),
            market="EU",
            source_url=source_url,
            source_hash=hash_,
            title=text[:180],
            text_content=text,
            chunk_content=text,
            source_metadata={"chunk_index": chunk_index, "source_url": source_url},
            embedding=self.embedding.embed(text),
        )
