# backend/main.py
# FastAPI app that serves both:
# - API (POST /api/summarize)
# - Static frontend (mounted at "/")

from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from extractor import (
    extract_pdf_text,
    is_pdf,
    is_image,
    extract_image_text,   # <-- NEW: OCR for images
)
from summarizer import summarize_text  # Cohere (text-only)

app = FastAPI(title="Doc Summary Assistant", version="1.0")

# Path: repo_root/frontend (sibling of backend/)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# CORS (safe to keep even for same-origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
#        API
# ---------------------
@app.post("/api/summarize")
async def summarize(file: UploadFile = File(...), length: str = Form("medium")):
    """
    Accepts a PDF or image file.
    - PDF: extract text via pypdf, then summarize via Cohere.
    - Image: OCR via Tesseract (pytesseract), then summarize via Cohere.
    """
    try:
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file")

        name = (file.filename or "").lower()

        # PDF → extract → summarize
        if is_pdf(name):
            text, meta = extract_pdf_text(data)
            if not text.strip():
                return {"summary": "No readable text found.", "meta": meta}
            return {"summary": summarize_text(text, length), "meta": meta}

        # Image → OCR → summarize
        if is_image(name):
            try:
                text = extract_image_text(data)
            except RuntimeError as ocr_err:
                # Typically "Tesseract not found" type errors
                return JSONResponse({"error": str(ocr_err)}, status_code=500)

            if not text.strip():
                return {
                    "summary": "No readable text detected in the image.",
                    "meta": {"source": "image-ocr"},
                }
            return {"summary": summarize_text(text, length), "meta": {"source": "image-ocr"}}

        raise HTTPException(status_code=400, detail="Only PDF or image files allowed")

    except HTTPException:
        raise
    except Exception as e:
        # neat error that the frontend can show
        return JSONResponse({"error": str(e)}, status_code=500)

# Lightweight health check
@app.get("/health")
def health():
    return {"ok": True, "service": "doc-summary-assistant", "provider": "cohere"}

# ---------------------
#   Static Frontend
# ---------------------
# Serve the frontend at root (index.html, assets, etc.)
# Keep this AFTER the API route definitions so /api/* keeps working.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")