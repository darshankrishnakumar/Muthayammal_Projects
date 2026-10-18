import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, TranslationLog, GestureVocabulary
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

    if db.query(TranslationLog).count() == 0:
        samples = [
            ("HELLO", "Hello, how can I assist you?", 0.96),
            ("PLEASE HELP", "Please, I need help right now.", 0.94),
            ("DOCTOR EMERGENCY", "Emergency, call a doctor immediately.", 0.98),
            ("THANK_YOU", "Thank you very much.", 0.97),
            ("WATER PLEASE", "Could I please have some water?", 0.92)
        ]
        for i, (g, s, c) in enumerate(samples):
            log = TranslationLog(
                session_id=f"SESS-{100+i}",
                gloss_sequence=g,
                spoken_sentence=s,
                confidence=c,
                latency_ms=round(random.uniform(18.0, 32.0), 1),
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(5, 120))
            )
            db.add(log)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
