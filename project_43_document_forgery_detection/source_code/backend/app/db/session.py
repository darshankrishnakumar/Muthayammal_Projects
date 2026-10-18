import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, DocumentAudit
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(DocumentAudit).count() == 0:
        docs = [
            ("Commercial Tax Invoice #9841", "INVOICE", "FORGED", "TEXT_ERASURE", 0.94, 8.2),
            ("Driver License National ID #A772", "IDENTITY_CARD", "AUTHENTIC", "NONE", 0.04, 0.0),
            ("Degree Certificate Stanford #2024", "ACADEMIC_CERTIFICATE", "FORGED", "SPLICING", 0.96, 12.5),
            ("Real Estate Agreement Clause 4", "CONTRACT", "SUSPICIOUS", "COPY_MOVE", 0.68, 4.1),
            ("Medical Reimbursement Claim", "INVOICE", "AUTHENTIC", "NONE", 0.08, 0.0),
        ]
        for title, dtype, verd, ftype, prob, area in docs:
            db.add(DocumentAudit(
                audit_id=f"AUD-2026-{random.randint(1000, 9999)}",
                document_title=title,
                document_type=dtype,
                forgery_verdict=verd,
                forgery_type=ftype,
                forgery_probability=prob,
                tampered_area_pct=area,
                ela_anomaly_score=round(prob * 1.05, 3),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
