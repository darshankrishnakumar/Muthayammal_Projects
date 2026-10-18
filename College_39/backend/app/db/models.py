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
    timestamp = Column(DateTime, default=datetime.utcnow)

class GestureVocabulary(Base):
    __tablename__ = "vocabulary"
    id = Column(Integer, primary_key=True, index=True)
    sign_label = Column(String(50), unique=True)
    category = Column(String(50)) # GREETING, COURTESY, EMERGENCY, MEDICAL, DAILY
    description = Column(String(200))
