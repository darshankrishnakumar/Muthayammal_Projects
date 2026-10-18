from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import FireIncident
from backend.app.ml.inference_engine import fire_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FireDetectionRequest(BaseModel):
    zone_name: str = "Warehouse Sector B Chemical Storage"
    camera_id: str = "CCTV-ZONE-02"
    simulate_flame: bool = True
    simulate_smoke: bool = False

@router.get("/")
def list_incidents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(FireIncident).order_by(FireIncident.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(items), "incidents": items}

@router.post("/analyze")
async def analyze_stream(req: FireDetectionRequest, db: Session = Depends(get_db)):
    mock_img = np.random.uniform(0.1, 0.4, (3, 64, 64)).astype(np.float32)
    flicker = np.random.uniform(0, 0.2, (8,)).astype(np.float32)

    if req.simulate_flame and req.simulate_smoke:
        mock_img[0, 20:45, 20:45] = 0.95
        flicker[3] = 0.95
    elif req.simulate_flame:
        mock_img[0, 25:35, 25:35] = 0.95
        flicker[3] = 0.90
    elif req.simulate_smoke:
        mock_img[:, 20:40, 20:40] = 0.60
        flicker[1] = 0.40

    res = fire_engine.inspect_surveillance(mock_img, flicker)

    if res["is_emergency"]:
        inc = FireIncident(
            incident_id=f"FIRE-2026-{uuid.uuid4().hex[:6].upper()}",
            zone_name=req.zone_name,
            camera_id=req.camera_id,
            hazard_type=res["hazard_type"],
            severity_tier=res["severity_tier"],
            confidence=res["confidence"],
            flicker_frequency_hz=res["flicker_hz"],
            plume_expansion_rate=2.4,
            dispatch_status="DISPATCHED"
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        res["incident_id"] = inc.incident_id
        await ws_manager.broadcast({"event": "FIRE_ALARM_DISPATCH", "data": res})

    return res
