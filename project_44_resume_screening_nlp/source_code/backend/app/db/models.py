from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class JobOpening(Base):
    __tablename__ = "job_openings"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    title = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False)
    required_skills = Column(Text, nullable=False)
    min_years_experience = Column(Float, default=2.0)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

class CandidateMatch(Base):
    __tablename__ = "candidate_matches"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), unique=True, index=True)
    job_id = Column(String(50), index=True)
    candidate_name = Column(String(100), nullable=False)
    overall_match_score = Column(Float, nullable=False) # 0 to 100
    semantic_similarity = Column(Float, nullable=False) # 0 to 1
    skill_coverage_pct = Column(Float, nullable=False) # 0 to 100
    experience_fit_score = Column(Float, nullable=False) # 0 to 10
    seniority_compatibility = Column(Float, nullable=True) # 0 to 100
    matched_skills = Column(Text, nullable=False)
    missing_skills = Column(Text, nullable=False)
    screening_decision = Column(String(30), nullable=False) # SHORTLISTED, REVIEW, REJECTED
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
