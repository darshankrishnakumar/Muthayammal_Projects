from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import FoodBatch
from backend.app.ml.inference_engine import freshness_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FreshnessInspectRequest(BaseModel):
    product_name: str = "Prime Ribeye Beef Cut"
    food_category: str = "MEAT_POULTRY"
    simulate_spoilage: bool = False

@router.get("/batches")
def get_batches(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    batches = db.query(FoodBatch).order_by(FoodBatch.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(batches), "batches": batches}

@router.post("/evaluate")
async def evaluate_batch(req: FreshnessInspectRequest, db: Session = Depends(get_db)):
    mock_food = np.random.uniform(0.4, 0.8, (3, 64, 64)).astype(np.float32)
    res = freshness_engine.evaluate_item(mock_food, req.simulate_spoilage)

    batch = FoodBatch(
        batch_id=f"FOOD-2026-{uuid.uuid4().hex[:6].upper()}",
        food_category=req.food_category,
        product_name=req.product_name,
        freshness_score=res["freshness_score"],
        deterioration_stage=res["deterioration_stage"],
        estimated_shelf_life_hours=res["estimated_shelf_life_hours"],
        browning_index=res["browning_index"],
        spoilage_area_pct=res["spoilage_area_pct"],
        recommendation=res["recommendation"]
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    await ws_manager.broadcast({"event": "FRESHNESS_INSPECTED", "data": res})
    return {"batch": batch, "metrics": res}
