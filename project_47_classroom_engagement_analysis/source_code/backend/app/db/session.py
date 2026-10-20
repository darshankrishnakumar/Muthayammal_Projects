import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, ClassroomSession, EngagementSnapshot, AuditLedger

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
            "Project 47 Classroom Engagement Analytics Platform initialized on Port 5047 with SQLite WAL mode and Multimodal Attention Fusion Net"
        )

    # 2. Seed Classroom Sessions
    if db.query(ClassroomSession).count() == 0:
        sessions = [
            ClassroomSession(
                session_id="SESS-CS301",
                course_code="CS-301",
                course_name="Distributed Systems & Cloud Computing",
                instructor_name="Dr. Alan Turing",
                classroom_id="Auditorium-A101",
                is_active=True
            ),
            ClassroomSession(
                session_id="SESS-MATH210",
                course_code="MATH-210",
                course_name="Multivariable Calculus & Differential Forms",
                instructor_name="Prof. Emmy Noether",
                classroom_id="Hall-B204",
                is_active=True
            ),
            ClassroomSession(
                session_id="SESS-AI405",
                course_code="AI-405",
                course_name="Deep Learning & Neural Representations",
                instructor_name="Dr. Geoffrey Hinton",
                classroom_id="Lab-C310",
                is_active=True
            ),
            ClassroomSession(
                session_id="SESS-BIO108",
                course_code="BIO-108",
                course_name="Molecular Genetics & Cellular Dynamics",
                instructor_name="Prof. Rosalind Franklin",
                classroom_id="Lecture-D402",
                is_active=True
            )
        ]
        db.add_all(sessions)
        db.commit()
        append_audit_block(db, "SEEDED_SESSIONS", "Seeded 4 academic lecture courses and active monitoring stations")

    # 3. Seed Engagement Snapshots
    if db.query(EngagementSnapshot).count() == 0:
        seed_snapshots = [
            ("ENG-2026-00101", "SESS-CS301", "Distributed Systems: Consensus Protocols", 34, 88.5, 84.0, 6.0, 7.5, 2.5, 89.0, 8, "MAINTAIN_CURRENT_PACE", 3.2, 5.0, 88.0),
            ("ENG-2026-00102", "SESS-CS301", "Distributed Systems: Byzantine Fault Tolerance", 34, 64.2, 58.0, 18.0, 17.0, 7.0, 62.0, 3, "ASK_CHECKPOINT_QUESTION", 12.5, 38.0, 64.0),
            ("ENG-2026-00103", "SESS-MATH210", "Stokes Theorem & Surface Integrals", 28, 92.0, 89.0, 4.0, 5.0, 2.0, 93.0, 10, "MAINTAIN_CURRENT_PACE", 2.0, 4.0, 92.0),
            ("ENG-2026-00104", "SESS-MATH210", "Differential Forms in R^n", 28, 48.0, 42.0, 26.0, 22.0, 10.0, 45.0, 1, "TRIGGER_INTERACTIVE_POLL", 22.0, 68.0, 42.0),
            ("ENG-2026-00105", "SESS-AI405", "Transformer Attention & QKV Projections", 42, 94.5, 91.0, 3.0, 4.5, 1.5, 95.0, 12, "MAINTAIN_CURRENT_PACE", 1.5, 3.0, 94.0),
            ("ENG-2026-00106", "SESS-AI405", "Backpropagation Through Time & Vanishing Gradients", 42, 34.0, 28.0, 32.0, 24.0, 16.0, 30.0, 0, "TAKE_2_MIN_REFRESHER_BREAK", 68.0, 88.0, 24.0),
            ("ENG-2026-00107", "SESS-BIO108", "CRISPR-Cas9 Gene Editing Mechanisms", 36, 82.0, 78.0, 9.0, 10.0, 3.0, 81.0, 6, "MAINTAIN_CURRENT_PACE", 4.5, 8.0, 80.0),
            ("ENG-2026-00108", "SESS-BIO108", "Polymerase Chain Reaction Thermocycling", 36, 68.5, 62.0, 16.0, 15.0, 7.0, 65.0, 4, "ASK_CHECKPOINT_QUESTION", 14.0, 42.0, 66.0)
        ]

        for s_id, sess_id, title, students, score, att, bored, dist, drowsy, focus, hands, act, d_risk, urg, part in seed_snapshots:
            ev_hash = hashlib.sha256(f"{s_id}:{sess_id}:{score}:{att}:{bored}:{dist}:{drowsy}:{act}".encode("utf-8")).hexdigest()
            db.add(EngagementSnapshot(
                snapshot_id=s_id,
                session_id=sess_id,
                lecture_title=title,
                student_count=students,
                mean_engagement_score=score,
                attentive_pct=att,
                bored_pct=bored,
                distracted_pct=dist,
                drowsy_pct=drowsy,
                head_pose_board_focus_pct=focus,
                hand_raise_count=hands,
                pedagogical_recommendation=act,
                drowsiness_risk_score=d_risk,
                intervention_urgency_index=urg,
                participation_rate_forecast=part,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 120))
            ))
        db.commit()
        append_audit_block(db, "SEEDED_SNAPSHOTS", "Seeded 8 multimodal engagement calibration snapshots with SHA-256 evidence hashes")

    db.close()

if __name__ == "__main__":
    init_db()
