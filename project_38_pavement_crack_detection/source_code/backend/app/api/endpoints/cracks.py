from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import CrackIncident
from backend.app.ml.inference_engine import pavement_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class InspectionRequest(BaseModel):
    road_name: str = "State Route 17 Westbound"
    chainage_km: float = 34.5
    surface_condition: str = "ASPHALT_WEARING_COURSE"

@router.get("/")
def list_incidents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    incidents = db.query(CrackIncident).order_by(CrackIncident.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(incidents), "incidents": incidents}

@router.post("/analyze")
async def analyze_crack(req: InspectionRequest, db: Session = Depends(get_db)):
    # Mock visual patch 3x64x64
    mock_patch = np.random.uniform(0.2, 0.8, (3, 64, 64)).astype(np.float32)
    # Simulate dark crack trace
    mock_patch[:, 20:30, 15:45] = 0.05
    
    metrics = pavement_engine.analyze_pavement_image(mock_patch)
    
    incident = CrackIncident(
        incident_id=f"CRK-2026-{uuid.uuid4().hex[:6].upper()}",
        road_name=req.road_name,
        chainage_km=req.chainage_km,
        crack_type=metrics["crack_type"],
        severity_level=metrics["severity_level"],
        mean_width_mm=metrics["mean_width_mm"],
        total_length_cm=metrics["total_length_cm"],
        density_percentage=metrics["density_percentage"],
        pci_score=metrics["pci_score"],
        recommendation=metrics["recommendation"]
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    resp = {"incident": incident, "metrics": metrics}
    await ws_manager.broadcast({"event": "NEW_CRACK_DETECTED", "data": metrics})
    return resp
