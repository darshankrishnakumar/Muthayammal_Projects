from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentAudit(Base):
    __tablename__ = "document_audits"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(50), unique=True, index=True)
    document_title = Column(String(100))
    document_type = Column(String(50)) # INVOICE, IDENTITY_CARD, ACADEMIC_CERTIFICATE, CONTRACT
    forgery_verdict = Column(String(20)) # AUTHENTIC, SUSPICIOUS, FORGED
    forgery_type = Column(String(50)) # NONE, COPY_MOVE, SPLICING, TEXT_ERASURE
    forgery_probability = Column(Float)
    tampered_area_pct = Column(Float)
    ela_anomaly_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
