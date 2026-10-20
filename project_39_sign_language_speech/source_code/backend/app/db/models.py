from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class TranslationLog(Base):
    __tablename__ = "translation_logs"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    gloss_sequence = Column(String(100))
    spoken_sentence = Column(Text)
    confidence = Column(Float)
    latency_ms = Column(Float)
    pitch_hz = Column(Float, nullable=True)
    duration_s = Column(Float, nullable=True)
    energy_db = Column(Float, nullable=True)
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class GestureVocabulary(Base):
    __tablename__ = "vocabulary"
    id = Column(Integer, primary_key=True, index=True)
    sign_label = Column(String(50), unique=True)
    category = Column(String(50)) # GREETING, COURTESY, EMERGENCY, MEDICAL, DAILY
    description = Column(String(200))

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
