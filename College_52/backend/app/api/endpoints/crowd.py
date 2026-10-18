from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import CrowdMonitoringEvent
from backend.app.ml.inference_engine import crowd_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CrowdAnalyzeRequest(BaseModel):
    zone_name: str = "Central Plaza Concourse"
    simulation_level: str = "moderate"

@router.get("/events")
def get_events(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    events = db.query(CrowdMonitoringEvent).order_by(CrowdMonitoringEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(events), "events": events}

@router.post("/analyze")
async def analyze_crowd_feed(req: CrowdAnalyzeRequest, db: Session = Depends(get_db)):
    res = crowd_engine.analyze_scene(req.zone_name, req.simulation_level)

    event = CrowdMonitoringEvent(
        event_id=f"CRW-2026-{uuid.uuid4().hex[:6].upper()}",
        zone_name=req.zone_name,
        estimated_headcount=res["estimated_headcount"],
        density_level=res["density_level"],
        anomaly_detected=res["anomaly_detected"],
        anomaly_type=res["anomaly_type"],
        risk_score=res["risk_score"],
        optical_flow_turbulence=res["optical_flow_turbulence"]
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    await ws_manager.broadcast({"event": "CROWD_ANOMALY_ALERT" if res["anomaly_detected"] else "CROWD_UPDATE", "data": res})
    return {"event": event, "metrics": res}
