from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CareerRole(Base):
    __tablename__ = "career_roles"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(50), unique=True, index=True)
    role_title = Column(String(100), nullable=False)
    required_competencies = Column(Text, nullable=False)
    avg_salary_usd = Column(Integer, default=120000)
    market_growth_rate = Column(String(20), default="HIGH") # VERY_HIGH, HIGH, MODERATE
    is_active = Column(Boolean, default=True)

class UpskillingRoadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(String(50), unique=True, index=True)
    user_name = Column(String(100), nullable=False)
    target_role = Column(String(100), nullable=False)
    readiness_score = Column(Float, nullable=False) # 0 to 100
    gap_score = Column(Float, nullable=False) # 0 to 100
    missing_skills = Column(Text, nullable=False)
    recommended_courses = Column(Text, nullable=False)
    recommended_projects = Column(Text, nullable=False)
    estimated_weeks_to_readiness = Column(Integer, nullable=False)
    salary_growth_potential = Column(Float, nullable=True)
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
