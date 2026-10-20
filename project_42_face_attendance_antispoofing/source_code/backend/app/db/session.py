import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, Student, AttendanceRecord, AuditLedger

db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def compute_block_hash(action: str, details: str, timestamp: str, prev_hash: str) -> str:
    payload = f"{action}|{details}|{timestamp}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db: Session, action_type: str, details: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    ts = datetime.utcnow().isoformat() + "Z"
    if last_block is None:
        idx = 0
        prev_hash = "0" * 64
    else:
        idx = last_block.block_index + 1
        prev_hash = last_block.current_hash
    cur_hash = compute_block_hash(action_type, details, ts, prev_hash)
    entry = AuditLedger(
        block_index=idx,
        timestamp=ts,
        action_type=action_type,
        details=details,
        previous_hash=prev_hash,
        current_hash=cur_hash
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "AI-Driven Face Recognition Attendance & Anti-Spoofing Microservice initialized on Port 5042 with SQLite WAL mode"
        )

    # 2. Enrolled Students
    if db.query(Student).count() == 0:
        students = [
            Student(student_id="STU-101", full_name="Alex Chen", department="Computer Science", year=4, face_enrolled=True, rfid_tag="RFID-9901"),
            Student(student_id="STU-102", full_name="Priya Sharma", department="Artificial Intelligence", year=3, face_enrolled=True, rfid_tag="RFID-9902"),
            Student(student_id="STU-103", full_name="David Miller", department="Robotics Engineering", year=4, face_enrolled=True, rfid_tag="RFID-9903"),
            Student(student_id="STU-104", full_name="Sophia Rossi", department="Data Science", year=3, face_enrolled=True, rfid_tag="RFID-9904"),
            Student(student_id="STU-105", full_name="Marcus Johnson", department="Cybersecurity", year=4, face_enrolled=True, rfid_tag="RFID-9905")
        ]
        db.add_all(students)
        db.commit()
        append_audit_block(db, "STUDENT_ROSTER_ENROLLED", "Registered 5 biometric face profiles into institutional roster")

    # 3. Baseline Verified Attendance & Security Events
    if db.query(AttendanceRecord).count() == 0:
        samples = [
            ("STU-101", "Alex Chen", "CS-401", "HALL-A1", "REAL", "NONE", 0.994, 0.985, 1.2, 0.88, 8.4, 98.5, "PRESENT"),
            ("STU-102", "Priya Sharma", "AI-502", "HALL-A1", "REAL", "NONE", 0.991, 0.978, 1.8, 0.84, 8.1, 96.8, "PRESENT"),
            ("STU-103", "David Miller", "ROB-405", "HALL-B2", "SPOOF_DETECTED", "PRINT_ATTACK_2D", 0.988, 0.845, 96.5, 0.05, 3.2, 12.0, "REJECTED_SPOOF"),
            ("STU-104", "Sophia Rossi", "DS-303", "HALL-A1", "REAL", "NONE", 0.989, 0.965, 2.1, 0.79, 7.8, 95.2, "PRESENT"),
            ("STU-105", "Marcus Johnson", "CYB-408", "HALL-C3", "SPOOF_DETECTED", "SCREEN_REPLAY_ATTACK", 0.995, 0.882, 98.2, 0.12, 3.8, 15.5, "REJECTED_SPOOF"),
            ("STU-101", "Alex Chen", "CS-401", "HALL-A1", "REAL", "NONE", 0.986, 0.972, 3.4, 0.75, 7.5, 93.0, "LATE"),
            ("STU-102", "Priya Sharma", "AI-502", "HALL-A1", "REAL", "NONE", 0.992, 0.981, 1.5, 0.86, 8.2, 97.5, "PRESENT"),
            ("STU-104", "Sophia Rossi", "DS-303", "HALL-A1", "SPOOF_DETECTED", "SILICONE_3D_MASK", 0.978, 0.812, 92.4, 0.22, 4.1, 18.0, "REJECTED_SPOOF")
        ]
        for i, (sid, name, course, hall, live, att, sp_conf, fc_conf, s_risk, tremor, ent, score, stat) in enumerate(samples):
            ev_hash = hashlib.sha256(f"{sid}|{name}|{course}|{live}|{att}|{fc_conf}|{s_risk}".encode()).hexdigest()
            rec = AttendanceRecord(
                record_id=f"ATT-2026-{100+i:04d}",
                student_id=sid,
                full_name=name,
                course_code=course,
                classroom_id=hall,
                liveness_status=live,
                attack_type=att,
                anti_spoof_confidence=sp_conf,
                face_match_confidence=fc_conf,
                spoof_risk_pct=s_risk,
                micro_tremor_score=tremor,
                illumination_entropy=ent,
                attendance_score=score,
                status=stat,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=(8 - i) * 15)
            )
            db.add(rec)
        db.commit()
        append_audit_block(db, "BASELINE_ATTENDANCE_LOGGED", "Logged 8 initial verified face verification and anti-spoofing security records")

    db.close()

if __name__ == "__main__":
    init_db()
