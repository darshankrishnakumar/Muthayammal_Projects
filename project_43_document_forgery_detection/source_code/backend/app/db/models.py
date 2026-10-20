from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentAudit(Base):
    __tablename__ = "document_audits"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(50), unique=True, index=True)
    document_title = Column(String(120))
    document_type = Column(String(50)) # INVOICE, IDENTITY_CARD, ACADEMIC_CERTIFICATE, CONTRACT
    forgery_verdict = Column(String(20)) # AUTHENTIC, SUSPICIOUS, FORGED
    forgery_type = Column(String(50)) # NONE, COPY_MOVE, SPLICING, TEXT_ERASURE
    forgery_probability = Column(Float)
    tampered_area_pct = Column(Float)
    ela_anomaly_score = Column(Float)
    spectral_dct_noise = Column(Float, nullable=True)
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class InspectionTemplate(Base):
    __tablename__ = "inspection_templates"
    id = Column(Integer, primary_key=True, index=True)
    template_code = Column(String(32), unique=True, index=True)
    template_name = Column(String(100), nullable=False)
    document_category = Column(String(50), nullable=False)
    allowed_compression_variance = Column(Float, default=0.08)
    baseline_dpi = Column(Integer, default=300)
    is_active = Column(Boolean, default=True)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
