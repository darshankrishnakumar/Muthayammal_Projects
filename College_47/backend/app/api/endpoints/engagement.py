from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import EngagementSnapshot
from backend.app.ml.inference_engine import classroom_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class EngagementAnalyzeRequest(BaseModel):
    lecture_title: str = "CS-301 Distributed Systems Lecture 8"
    student_count: int = 32
    attentive_pct: float = 75.0
    bored_pct: float = 12.0
    distracted_pct: float = 8.0
    drowsy_pct: float = 5.0

@router.get("/timeline")
def get_timeline(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    snapshots = db.query(EngagementSnapshot).order_by(EngagementSnapshot.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(snapshots), "snapshots": snapshots}

@router.post("/analyze")
async def analyze_engagement(req: EngagementAnalyzeRequest, db: Session = Depends(get_db)):
    res = classroom_engine.evaluate_classroom(req.attentive_pct, req.bored_pct, req.distracted_pct, req.drowsy_pct)

    snap = EngagementSnapshot(
        snapshot_id=f"ENG-2026-{uuid.uuid4().hex[:6].upper()}",
        lecture_title=req.lecture_title,
        student_count=req.student_count,
        mean_engagement_score=res["mean_engagement_score"],
        attentive_pct=res["attentive_pct"],
        bored_pct=res["bored_pct"],
        distracted_pct=res["distracted_pct"],
        drowsy_pct=res["drowsy_pct"],
        head_pose_board_focus_pct=res["head_pose_board_focus_pct"],
        pedagogical_recommendation=res["pedagogical_recommendation"]
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)

    await ws_manager.broadcast({"event": "ENGAGEMENT_UPDATE", "data": res})
    return {"snapshot": snap, "metrics": res}
