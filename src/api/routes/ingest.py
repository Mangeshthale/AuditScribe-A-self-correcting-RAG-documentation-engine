import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from api.schemas import IngestPDFResponse, IngestURLResponse
from ingest import ingest_pdf, ingest_url

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/pdf", response_model=IngestPDFResponse)
async def ingest_pdf_route(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        n = ingest_pdf(tmp_path)
        os.unlink(tmp_path)
        return IngestPDFResponse(status="ok", chunks=n, filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url", response_model=IngestURLResponse)
def ingest_url_route(url: str):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL.")
    try:
        n = ingest_url(url)
        return IngestURLResponse(status="ok", chunks=n, url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
