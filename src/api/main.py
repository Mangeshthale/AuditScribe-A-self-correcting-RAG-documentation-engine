# src/api.py
import math
import time
import tempfile
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from main import run_sentinel
from ingest import ingest_pdf, ingest_url

app = FastAPI(title="AuditScribe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuditRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []


def safe_float(val) -> float:
    """Convert nan/inf to 0.0 — Python's nan is not valid JSON."""
    try:
        f = float(val)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else round(f, 4)
    except Exception:
        return 0.0


@app.post("/audit/run")
async def audit_run(req: AuditRequest):
    try:
        start = time.time()
        report, scores, suggestions, source = run_sentinel(req.query, req.history)
        latency = round(time.time() - start, 2)

        report_text = str(report.raw if hasattr(report, "raw") else report)

        return {
            "report":           report_text,
            "faithfulness":     safe_float(scores.get("faithfulness", 0.0)),
            "answer_relevancy": safe_float(scores.get("answer_relevancy", 0.0)),
            "latency":          latency,
            "suggestions":      suggestions,
            "source":           source,   # "docs" or "web"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/pdf")
async def ingest_pdf_route(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        n = ingest_pdf(tmp_path)
        os.unlink(tmp_path)
        return {"chunks": n, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/url")
async def ingest_url_route(url: str):
    try:
        n = ingest_url(url)
        return {"chunks": n, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
