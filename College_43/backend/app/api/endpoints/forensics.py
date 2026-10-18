from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import DocumentAudit
from backend.app.ml.inference_engine import forgery_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class DocumentAuditRequest(BaseModel):
    document_title: str = "Commercial Tax Invoice #9841"
    document_type: str = "INVOICE"
    simulate_forgery: bool = True

@router.get("/audits")
def get_audits(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    audits = db.query(DocumentAudit).order_by(DocumentAudit.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(audits), "audits": audits}

@router.post("/analyze")
async def analyze_document(req: DocumentAuditRequest, db: Session = Depends(get_db)):
    mock_doc = np.random.uniform(0.3, 0.8, (3, 64, 64)).astype(np.float32)
    res = forgery_engine.audit_document(mock_doc, req.simulate_forgery)

    audit = DocumentAudit(
        audit_id=f"AUD-2026-{uuid.uuid4().hex[:6].upper()}",
        document_title=req.document_title,
        document_type=req.document_type,
        forgery_verdict=res["forgery_verdict"],
        forgery_type=res["forgery_type"],
        forgery_probability=res["forgery_probability"],
        tampered_area_pct=res["tampered_area_pct"],
        ela_anomaly_score=res["ela_anomaly_score"]
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    await ws_manager.broadcast({"event": "DOCUMENT_AUDITED", "data": res})
    return {"audit": audit, "metrics": res}
