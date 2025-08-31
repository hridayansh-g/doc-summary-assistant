Doc Summary Assistant: PDF + Image OCR (Tesseract) -> Cohere summary.
Local: uvicorn backend.main:app --reload --port 8000 (open http://localhost:8000)
Deploy: Backend on Render (uses apt.txt), Frontend on Netlify (uses _redirects to proxy /api/* to backend).
