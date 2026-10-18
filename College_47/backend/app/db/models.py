from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class EngagementSnapshot(Base):
    __tablename__ = "engagement_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String(50), unique=True, index=True)
    lecture_title = Column(String(100))
    student_count = Column(Integer, default=30)
    mean_engagement_score = Column(Float) # 0 to 100
    attentive_pct = Column(Float)
    bored_pct = Column(Float)
    distracted_pct = Column(Float)
    drowsy_pct = Column(Float)
    head_pose_board_focus_pct = Column(Float)
    pedagogical_recommendation = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
