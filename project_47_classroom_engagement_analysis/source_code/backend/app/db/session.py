import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, EngagementSnapshot
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(EngagementSnapshot).count() == 0:
        recs = [
            ("MAINTAIN_CURRENT_PACE", 88.5, 85.0, 5.0, 8.0, 2.0),
            ("TRIGGER_INTERACTIVE_POLL", 64.2, 55.0, 20.0, 18.0, 7.0),
            ("TAKE_2_MIN_REFRESHER_BREAK", 48.0, 38.0, 30.0, 22.0, 10.0),
            ("ASK_CHECKPOINT_QUESTION", 72.0, 68.0, 14.0, 12.0, 6.0)
        ]
        for i, (rec_action, score, att, bored, dist, drowsy) in enumerate(recs):
            db.add(EngagementSnapshot(
                snapshot_id=f"ENG-2026-{100+i}",
                lecture_title="CS-301 Distributed Systems Lecture 8",
                student_count=32,
                mean_engagement_score=score,
                attentive_pct=att,
                bored_pct=bored,
                distracted_pct=dist,
                drowsy_pct=drowsy,
                head_pose_board_focus_pct=round(att * 0.95, 1),
                pedagogical_recommendation=rec_action,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 50))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
