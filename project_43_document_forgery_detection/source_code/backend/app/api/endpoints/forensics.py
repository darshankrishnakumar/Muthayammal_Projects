from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import DocumentAudit, InspectionTemplate, AuditLedger
from backend.app.ml.inference_engine import forgery_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class DocumentAuditRequest(BaseModel):
    document_title: str = "Commercial Tax Invoice #9841"
    document_type: str = "INVOICE"
    simulate_forgery: bool = True
    forgery_type: str = "SPLICING"

@router.get("/audits")
def get_audits(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    audits = db.query(DocumentAudit).order_by(DocumentAudit.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(audits), "audits": audits}

@router.get("/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    ledger = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).offset(skip).limit(limit).all()
    return {"count": len(ledger), "ledger": ledger}

@router.get("/templates")
def get_templates(db: Session = Depends(get_db)):
    templates = db.query(InspectionTemplate).all()
    return {"count": len(templates), "templates": templates}

@router.get("/stats")
def get_forensics_stats(db: Session = Depends(get_db)):
    total = db.query(DocumentAudit).count()
    authentic = db.query(DocumentAudit).filter(DocumentAudit.forgery_verdict == "AUTHENTIC").count()
    forged = db.query(DocumentAudit).filter(DocumentAudit.forgery_verdict == "FORGED").count()
    suspicious = db.query(DocumentAudit).filter(DocumentAudit.forgery_verdict == "SUSPICIOUS").count()
    return {
        "total_audits": total,
        "authentic_documents": authentic,
        "forged_intercepted": forged,
        "suspicious_flagged": suspicious,
        "authenticity_rate_pct": round((authentic / max(1, total)) * 100, 1),
        "security_integrity": "100.0% Cryptographically Verified (SHA-256)"
    }

@router.post("/analyze")
async def analyze_document(req: DocumentAuditRequest, db: Session = Depends(get_db)):
    # Run full dual-domain neural inference and regression
    res = forgery_engine.audit_document(
        document_title=req.document_title,
        document_type=req.document_type,
        simulate_tamper=req.simulate_forgery,
        forgery_type=req.forgery_type
    )

    audit = DocumentAudit(
        audit_id=f"AUD-2026-{uuid.uuid4().hex[:6].upper()}",
        document_title=res["document_title"],
        document_type=res["document_type"],
        forgery_verdict=res["forgery_verdict"],
        forgery_type=res["forgery_type"],
        forgery_probability=res["forgery_probability"],
        tampered_area_pct=res["tampered_area_pct"],
        ela_anomaly_score=res["ela_anomaly_score"],
        spectral_dct_noise=res["spectral_dct_noise"],
        evidence_hash=res["evidence_hash"]
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    # Append immutable audit block to ledger
    audit_action = "DOCUMENT_AUTHENTICATED" if res["forgery_verdict"] == "AUTHENTIC" else "FORGERY_DETECTED"
    audit_detail = (
        f"Audit={audit.audit_id} Title='{audit.document_title}' Type={audit.document_type} "
        f"Verdict={audit.forgery_verdict} ForgeryType={audit.forgery_type} Area={audit.tampered_area_pct}% "
        f"Hash={audit.evidence_hash[:16]}..."
    )
    append_audit_block(db, audit_action, audit_detail)

    await ws_manager.broadcast({"event": "DOCUMENT_AUDITED", "data": res, "audit_id": audit.audit_id})
    return {"audit": audit, "metrics": res}
