from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import FruitItem
from backend.app.ml.inference_engine import fruit_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FruitInspectionRequest(BaseModel):
    conveyor_lane: int = 1
    defect_sim: str = "NONE"

@router.get("/items")
def get_items(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(FruitItem).order_by(FruitItem.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(items), "items": items}

@router.post("/inspect")
async def inspect_fruit(req: FruitInspectionRequest, db: Session = Depends(get_db)):
    mock_img = np.random.uniform(0.4, 0.9, (3, 64, 64)).astype(np.float32)
    if req.defect_sim != "NONE":
        mock_img[:, 20:35, 20:35] = 0.05

    res = fruit_engine.inspect_fruit(mock_img)
    if req.defect_sim != "NONE":
        res["defect"] = req.defect_sim
        res["grade"] = "GRADE_C_REJECT"
        res["sorting_chute"] = "BIN_3_DISCARD"
        res["defect_area_pct"] = 16.8

    item = FruitItem(
        item_id=f"FRUIT-2026-{uuid.uuid4().hex[:6].upper()}",
        fruit_variety=res["variety"],
        quality_grade=res["grade"],
        defect_type=res["defect"],
        defect_area_pct=res["defect_area_pct"],
        diameter_mm=res["diameter_mm"],
        confidence=res["confidence"],
        sorting_chute=res["sorting_chute"]
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    await ws_manager.broadcast({"event": "FRUIT_GRADED", "data": res})
    return {"item": item, "metrics": res}
