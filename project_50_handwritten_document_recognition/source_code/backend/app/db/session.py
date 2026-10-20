import os
import hashlib
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, ProcessedDocument, AuditLedger

# Ensure db directory exists
db_file = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_file), exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Check if Genesis Block exists
    genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
    if not genesis:
        genesis_ts = "2026-10-01T00:00:00.000000Z"
        genesis_payload = f"0|{genesis_ts}|GENESIS_BLOCK|GENESIS_DOC|0000000000000000000000000000000000000000000000000000000000000000"
        genesis_hash = hashlib.sha256(genesis_payload.encode()).hexdigest()
        g_block = AuditLedger(
            block_index=0,
            timestamp=genesis_ts,
            event_type="GENESIS_BLOCK",
            doc_id="DOC-GENESIS-0000",
            evidence_hash="0000000000000000000000000000000000000000000000000000000000000000",
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            block_hash=genesis_hash
        )
        db.add(g_block)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
