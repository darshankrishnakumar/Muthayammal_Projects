from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class JobOpening(Base):
    __tablename__ = "job_openings"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    title = Column(String(100))
    department = Column(String(50))
    required_skills = Column(Text)
    min_years_experience = Column(Float, default=2.0)
    description = Column(Text)

class CandidateMatch(Base):
    __tablename__ = "candidate_matches"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String(50), unique=True, index=True)
    job_id = Column(String(50), index=True)
    candidate_name = Column(String(100))
    overall_match_score = Column(Float) # 0 to 100
    semantic_similarity = Column(Float)
    skill_coverage_pct = Column(Float)
    experience_fit_score = Column(Float)
    matched_skills = Column(Text)
    missing_skills = Column(Text)
    screening_decision = Column(String(30)) # SHORTLISTED, REVIEW, REJECTED
    timestamp = Column(DateTime, default=datetime.utcnow)
