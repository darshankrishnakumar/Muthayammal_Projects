from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ClassroomSession(Base):
    __tablename__ = "classroom_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True)
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(100), nullable=False)
    instructor_name = Column(String(100), nullable=False)
    classroom_id = Column(String(50), default="Auditorium-A101")
    is_active = Column(Boolean, default=True)

class EngagementSnapshot(Base):
    __tablename__ = "engagement_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String(50), unique=True, index=True)
    session_id = Column(String(50), nullable=False)
    lecture_title = Column(String(100), nullable=False)
    student_count = Column(Integer, default=32)
    mean_engagement_score = Column(Float, nullable=False) # 0 to 100
    attentive_pct = Column(Float, nullable=False)
    bored_pct = Column(Float, nullable=False)
    distracted_pct = Column(Float, nullable=False)
    drowsy_pct = Column(Float, nullable=False)
    head_pose_board_focus_pct = Column(Float, default=85.0)
    hand_raise_count = Column(Integer, default=3)
    pedagogical_recommendation = Column(String(100), nullable=False)
    drowsiness_risk_score = Column(Float, default=5.0)
    intervention_urgency_index = Column(Float, default=10.0)
    participation_rate_forecast = Column(Float, default=80.0)
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
