from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ProcessedDocument(Base):
    __tablename__ = "processed_documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(50), unique=True, index=True)
    document_type = Column(String(50)) # MEDICAL_INTAKE_FORM, HANDWRITTEN_INVOICE, SURVEY_SHEET
    patient_or_client_name = Column(String(100))
    date_field = Column(String(30))
    id_number = Column(String(50))
    total_amount = Column(String(30))
    signature_verified = Column(Boolean, default=True)
    mean_confidence = Column(Float)
    human_review_required = Column(Boolean, default=False)
    extracted_json_payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
