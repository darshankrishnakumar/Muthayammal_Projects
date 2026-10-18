import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, ProcessedDocument
from datetime import datetime, timedelta
import random
import json

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
    if db.query(ProcessedDocument).count() == 0:
        docs = [
            ("MEDICAL_INTAKE_FORM", "Dr. Jonathan Hayes", "2026-10-12", "MED-8842", "$350.00", True, 0.962, False),
            ("HANDWRITTEN_INVOICE", "Global Supplies Ltd", "2026-10-10", "INV-1094", "$1,450.00", True, 0.884, False),
            ("SURVEY_SHEET", "Anonymous Respondent #42", "2026-10-08", "SURV-77", "N/A", False, 0.642, True),
        ]
        for dtype, name, dt, idn, amt, sig, conf, rev in docs:
            payload = {"client_name": name, "date": dt, "id": idn, "amount": amt, "signature": sig}
            db.add(ProcessedDocument(
                doc_id=f"DOC-2026-{random.randint(100, 999)}",
                document_type=dtype,
                patient_or_client_name=name,
                date_field=dt,
                id_number=idn,
                total_amount=amt,
                signature_verified=sig,
                mean_confidence=conf,
                human_review_required=rev,
                extracted_json_payload=json.dumps(payload),
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
