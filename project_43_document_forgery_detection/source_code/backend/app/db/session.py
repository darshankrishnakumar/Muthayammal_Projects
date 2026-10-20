import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, DocumentAudit, InspectionTemplate, AuditLedger

db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def compute_block_hash(action: str, details: str, timestamp: str, prev_hash: str) -> str:
    payload = f"{action}|{details}|{timestamp}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db: Session, action_type: str, details: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    ts = datetime.utcnow().isoformat() + "Z"
    if last_block is None:
        idx = 0
        prev_hash = "0" * 64
    else:
        idx = last_block.block_index + 1
        prev_hash = last_block.current_hash
    cur_hash = compute_block_hash(action_type, details, ts, prev_hash)
    entry = AuditLedger(
        block_index=idx,
        timestamp=ts,
        action_type=action_type,
        details=details,
        previous_hash=prev_hash,
        current_hash=cur_hash
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "AI-Based Document Forgery Detection Microservice initialized on Port 5043 with SQLite WAL mode"
        )

    # 2. Forensic Inspection Templates
    if db.query(InspectionTemplate).count() == 0:
        templates = [
            InspectionTemplate(template_code="TMPL-INV-01", template_name="Commercial Tax & VAT Invoice Standard", document_category="INVOICE", allowed_compression_variance=0.06, baseline_dpi=300),
            InspectionTemplate(template_code="TMPL-ID-02", template_name="National Driving License & Passport Standard", document_category="IDENTITY_CARD", allowed_compression_variance=0.04, baseline_dpi=600),
            InspectionTemplate(template_code="TMPL-CERT-03", template_name="University Degree & Diploma Parchment", document_category="ACADEMIC_CERTIFICATE", allowed_compression_variance=0.05, baseline_dpi=400),
            InspectionTemplate(template_code="TMPL-CONT-04", template_name="Legal Non-Disclosure & Employment Contract", document_category="CONTRACT", allowed_compression_variance=0.08, baseline_dpi=300)
        ]
        db.add_all(templates)
        db.commit()
        append_audit_block(db, "TEMPLATES_INITIALIZED", "Configured 4 institutional document forensic inspection templates")

    # 3. Baseline Verified Audits
    if db.query(DocumentAudit).count() == 0:
        samples = [
            ("Commercial Tax Invoice #9841", "INVOICE", "FORGED", "TEXT_ERASURE", 0.942, 11.4, 7.85, 0.82),
            ("Driver License National ID #A772", "IDENTITY_CARD", "AUTHENTIC", "NONE", 0.045, 0.0, 0.35, 0.08),
            ("Degree Certificate Stanford #2024", "ACADEMIC_CERTIFICATE", "FORGED", "SPLICING", 0.965, 24.8, 9.12, 0.91),
            ("Real Estate Agreement Clause 4", "CONTRACT", "FORGED", "COPY_MOVE", 0.885, 14.2, 6.94, 0.74),
            ("Medical Reimbursement Claim #510", "INVOICE", "AUTHENTIC", "NONE", 0.062, 0.0, 0.42, 0.11),
            ("Employment Contract NDA Schedule", "CONTRACT", "AUTHENTIC", "NONE", 0.055, 0.0, 0.38, 0.09),
            ("Export Customs Declaration Form", "INVOICE", "FORGED", "TEXT_ERASURE", 0.918, 9.6, 7.22, 0.78),
            ("Academic Transcript Honors Board", "ACADEMIC_CERTIFICATE", "AUTHENTIC", "NONE", 0.071, 0.0, 0.49, 0.14)
        ]
        for i, (title, dtype, verd, ftype, prob, area, ela, dct) in enumerate(samples):
            ev_hash = hashlib.sha256(f"{title}|{dtype}|{verd}|{ftype}|{prob}|{area}|{ela}".encode()).hexdigest()
            rec = DocumentAudit(
                audit_id=f"AUD-2026-{1000 + i}",
                document_title=title,
                document_type=dtype,
                forgery_verdict=verd,
                forgery_type=ftype,
                forgery_probability=prob,
                tampered_area_pct=area,
                ela_anomaly_score=ela,
                spectral_dct_noise=dct,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=(8 - i) * 20)
            )
            db.add(rec)
        db.commit()
        append_audit_block(db, "BASELINE_AUDITS_LOGGED", "Logged 8 initial forensic document tampering and authenticity audit records")

    db.close()

if __name__ == "__main__":
    init_db()
