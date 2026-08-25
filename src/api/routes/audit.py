import time
from fastapi import APIRouter, HTTPException
from api.schemas import AuditRequest, AuditResponse
from main import run_sentinel

router = APIRouter(prefix="/audit", tags=["audit"])

@router.post("/run", response_model=AuditResponse)
def run_audit(request: AuditRequest):
    try:
        start = time.time()
        report, scores = run_sentinel(request.query)
        latency = round(time.time() - start, 2)

        report_text = report.raw if hasattr(report, "raw") else str(report)

        return AuditResponse(
            report=report_text,
            faithfulness=float(scores.get("faithfulness", 0.0)),
            answer_relevancy=float(scores.get("answer_relevancy", 0.0)),
            latency=latency,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
