from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ProcessedDocument(Base):
    __tablename__ = "processed_documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(50), unique=True, index=True)
    document_type = Column(String(50))
    patient_or_client_name = Column(String(100))
    primary_diagnosis_or_purpose = Column(String(100))
    date_field = Column(String(30))
    id_number = Column(String(50))
    total_amount = Column(String(30))
    contrast_ratio = Column(Float)
    stroke_variance = Column(Float)
    background_snr = Column(Float)
    quality_score = Column(Float)
    lexical_confidence = Column(Float)
    character_error_rate = Column(Float)
    word_error_rate = Column(Float)
    signature_verified = Column(Boolean, default=True)
    human_review_required = Column(Boolean, default=False)
    evidence_hash = Column(String(64))
    extracted_json_payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    block_index = Column(Integer, primary_key=True)
    timestamp = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    doc_id = Column(String(50), nullable=False)
    evidence_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), nullable=False)
