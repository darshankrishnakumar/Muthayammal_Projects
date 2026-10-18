from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CareerRole(Base):
    __tablename__ = "career_roles"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(50), unique=True, index=True)
    role_title = Column(String(100))
    required_competencies = Column(Text)
    avg_salary_usd = Column(Integer)
    market_growth_rate = Column(String(20)) # HIGH, VERY_HIGH, MODERATE

class UpskillingRoadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(String(50), unique=True, index=True)
    user_name = Column(String(100))
    target_role = Column(String(100))
    readiness_score = Column(Float) # 0 to 100
    gap_score = Column(Float) # 0 to 100
    missing_skills = Column(Text)
    recommended_courses = Column(Text)
    recommended_projects = Column(Text)
    estimated_weeks_to_readiness = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
