from pydantic import BaseModel
from typing import Optional

class AuditRequest(BaseModel):
    query: str

class AuditResponse(BaseModel):
    report: str
    faithfulness: float
    answer_relevancy: float
    latency: float

class IngestPDFResponse(BaseModel):
    status: str
    chunks: int
    filename: str

class IngestURLResponse(BaseModel):
    status: str
    chunks: int
    url: str
