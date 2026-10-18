from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import TranslationLog, GestureVocabulary
from backend.app.ml.inference_engine import sign_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class GestureSimulateRequest(BaseModel):
    gesture_index: int = 0
    session_id: str = "LIVE-SESSION-1"

@router.get("/logs")
def get_logs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(TranslationLog).order_by(TranslationLog.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(logs), "logs": logs}

@router.get("/vocabulary")
def get_vocab(db: Session = Depends(get_db)):
    items = db.query(GestureVocabulary).all()
    return {"count": len(items), "vocabulary": items}

@router.post("/predict")
async def predict_gesture(req: GestureSimulateRequest, db: Session = Depends(get_db)):
    # Generate signature landmark sequence (30, 54)
    seq = np.random.normal(0.0, 0.2, (30, 54)).astype(np.float32)
    idx = req.gesture_index % 10
    seq[:, idx*5:(idx+1)*5] += 2.5 # Strong signature
    
    res = sign_engine.translate_sequence(seq)
    
    log = TranslationLog(
        session_id=req.session_id,
        gloss_sequence=res["gloss"],
        spoken_sentence=res["spoken_sentence"],
        confidence=res["confidence"],
        latency_ms=res["latency_ms"]
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    await ws_manager.broadcast({"event": "GESTURE_TRANSLATED", "data": res})
    return res
