from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import RailwayDefectRecord
from backend.app.ml.inference_engine import rail_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class RailInspectRequest(BaseModel):
    chainage_km: str = "KM 144.200"
    track_segment: str = "Line 1 Main Westbound"
    simulated_condition: str = "crack"

@router.get("/defects")
def get_defects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    records = db.query(RailwayDefectRecord).order_by(RailwayDefectRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(records), "records": records}

@router.post("/inspect")
async def inspect_rail(req: RailInspectRequest, db: Session = Depends(get_db)):
    res = rail_engine.inspect_frame(req.chainage_km, req.track_segment, req.simulated_condition)

    rec = RailwayDefectRecord(
        record_id=f"RAL-2026-{uuid.uuid4().hex[:6].upper()}",
        chainage_km=req.chainage_km,
        track_segment=req.track_segment,
        defect_type=res["defect_type"],
        severity=res["severity"],
        confidence=res["confidence"],
        affected_area_px=res["affected_area_px"],
        status="Urgent Remediation" if res["severity"] == "Critical" else "Under Review"
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    await ws_manager.broadcast({"event": "RAIL_DEFECT_DETECTED", "data": res})
    return {"record": rec, "metrics": res}
