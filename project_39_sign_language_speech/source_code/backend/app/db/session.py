import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, TranslationLog, GestureVocabulary, AuditLedger

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

    # Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "Sign-Speech Translation Platform initialized on Port 5039 with SQLite WAL persistence"
        )

    # Initial vocabulary
    if db.query(GestureVocabulary).count() == 0:
        vocab = [
            GestureVocabulary(sign_label="HELLO", category="GREETING", description="Open palm waving outward from temple"),
            GestureVocabulary(sign_label="THANK_YOU", category="COURTESY", description="Fingers of flat hand touch chin and move forward"),
            GestureVocabulary(sign_label="PLEASE", category="COURTESY", description="Circular rubbing motion on chest with flat open palm"),
            GestureVocabulary(sign_label="HELP", category="EMERGENCY", description="Thumbs-up closed fist placed upon upward open palm"),
            GestureVocabulary(sign_label="EMERGENCY", category="EMERGENCY", description="Letter E hand shaken rapidly side-to-side"),
            GestureVocabulary(sign_label="DOCTOR", category="MEDICAL", description="Bent fingers of right hand tapping inside left wrist pulse"),
            GestureVocabulary(sign_label="WATER", category="DAILY", description="W-handshape index finger tapping lower lip"),
            GestureVocabulary(sign_label="YES", category="DAILY", description="Fist nodding up and down like a head nod"),
            GestureVocabulary(sign_label="NO", category="DAILY", description="Index and middle finger snap down onto thumb"),
            GestureVocabulary(sign_label="GOODBYE", category="GREETING", description="Open hand fingers waving up and down")
        ]
        db.add_all(vocab)
        db.commit()
        append_audit_block(db, "VOCABULARY_LOADED", f"Initialized 10 standard sign language gesture classes")

    # Initial translation samples
    if db.query(TranslationLog).count() == 0:
        samples = [
            ("HELLO", "Hello, how can I assist you?", 0.96, 185.2, 0.85, 62.4),
            ("PLEASE", "Please assist me with this task.", 0.94, 191.0, 0.95, 58.1),
            ("DOCTOR", "Please call a doctor immediately.", 0.98, 179.5, 1.25, 65.3),
            ("THANK_YOU", "Thank you very much for your help.", 0.97, 174.8, 1.10, 59.8),
            ("WATER", "I would like some drinking water.", 0.92, 169.2, 0.90, 59.2),
            ("HELP", "I need immediate emergency assistance.", 0.99, 222.4, 1.30, 72.5),
            ("EMERGENCY", "This is a critical emergency situation.", 0.98, 246.1, 1.65, 76.8)
        ]
        for i, (g, s, c, p, d, e) in enumerate(samples):
            ev_hash = hashlib.sha256(f"{g}|{s}|{c}".encode()).hexdigest()
            log = TranslationLog(
                session_id=f"SESS-{100+i}",
                gloss_sequence=g,
                spoken_sentence=s,
                confidence=c,
                latency_ms=round(random.uniform(18.0, 32.0), 1),
                pitch_hz=p,
                duration_s=d,
                energy_db=e,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 120))
            )
            db.add(log)
        db.commit()
        append_audit_block(db, "BENCHMARK_TRANSLATIONS_LOADED", "Seeded 7 verified sign language translation records")

    db.close()

if __name__ == "__main__":
    init_db()
