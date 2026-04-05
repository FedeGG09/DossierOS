from pdf2image import convert_from_bytes
import pytesseract


class OCRService:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        images = convert_from_bytes(file_bytes)
        texts = []
        for img in images:
            texts.append(pytesseract.image_to_string(img, lang="eng"))
        return "\n".join(texts)
