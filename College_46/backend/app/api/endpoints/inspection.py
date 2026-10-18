from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import InspectedPart
from backend.app.ml.inference_engine import mfg_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class PartScanRequest(BaseModel):
    assembly_line: str = "Line-1 SMT PCB Assembly"
    part_type: str = "PCB_BOARD"
    simulate_defect: str = "NONE"

@router.get("/parts")
def get_parts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    parts = db.query(InspectedPart).order_by(InspectedPart.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(parts), "parts": parts}

@router.post("/scan")
async def scan_part(req: PartScanRequest, db: Session = Depends(get_db)):
    mock_img = np.random.uniform(0.4, 0.7, (3, 64, 64)).astype(np.float32)
    res = mfg_engine.inspect_part(mock_img, req.simulate_defect)

    part = InspectedPart(
        part_id=f"PART-2026-{uuid.uuid4().hex[:6].upper()}",
        assembly_line=req.assembly_line,
        part_type=req.part_type,
        inspection_verdict=res["inspection_verdict"],
        defect_type=res["defect_type"],
        severity_score=res["severity_score"],
        defect_area_pct=res["defect_area_pct"],
        actuator_action=res["actuator_action"]
    )
    db.add(part)
    db.commit()
    db.refresh(part)

    await ws_manager.broadcast({"event": "PART_INSPECTED", "data": res})
    return {"part": part, "metrics": res}
