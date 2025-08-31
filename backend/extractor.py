from typing import Tuple
from pypdf import PdfReader
from PIL import Image
import pytesseract
import io

# Allowed image types
ALLOWED_IMG = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}


def is_pdf(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


def is_image(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_IMG)


def extract_pdf_text(file_bytes: bytes) -> Tuple[str, dict]:
    """
    Extract text + tiny metadata from a PDF using pure-Python pypdf.
    Returns: (text, meta_dict)
    """
    meta: dict = {}
    text_parts: list[str] = []

    with io.BytesIO(file_bytes) as fh:
        reader = PdfReader(fh)
        docinfo = reader.metadata or {}
        meta = {
            "title": getattr(docinfo, "title", None),
            "author": getattr(docinfo, "author", None),
            "subject": getattr(docinfo, "subject", None),
        }
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts).strip(), meta


def extract_image_text(image_bytes: bytes) -> str:
    """
    OCR an image to text using Tesseract via pytesseract.
    Returns plain text. Raises a helpful error if Tesseract is missing.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            # Normalize mode for better OCR
            im = im.convert("RGB")
            # psm 6 = assume a single uniform block of text (good default)
            return pytesseract.image_to_string(im, lang="eng", config="--psm 6").strip()
    except pytesseract.pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR engine not found. Install it first (macOS: 'brew install tesseract')."
        )