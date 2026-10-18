import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, Student, AttendanceRecord
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
    if db.query(Student).count() == 0:
        roster = [
            ("STU-101", "Alex Chen", "Computer Science", 4),
            ("STU-102", "Priya Sharma", "Artificial Intelligence", 3),
            ("STU-103", "David Miller", "Software Engineering", 4),
            ("STU-104", "Sophia Rossi", "Data Science", 3),
            ("STU-105", "Marcus Johnson", "Computer Engineering", 2),
        ]
        for sid, name, dept, yr in roster:
            db.add(Student(student_id=sid, full_name=name, department=dept, year=yr))
        db.commit()

    if db.query(AttendanceRecord).count() == 0:
        names = [("STU-101", "Alex Chen"), ("STU-102", "Priya Sharma"), ("STU-103", "David Miller")]
        for i, (sid, name) in enumerate(names):
            rec = AttendanceRecord(
                record_id=f"ATT-2026-{100+i}",
                student_id=sid,
                full_name=name,
                course_code="CS-401",
                liveness_status="REAL",
                anti_spoof_confidence=round(random.uniform(0.95, 0.99), 3),
                face_match_confidence=round(random.uniform(0.94, 0.98), 3),
                status="PRESENT",
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 10))
            )
            db.add(rec)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
