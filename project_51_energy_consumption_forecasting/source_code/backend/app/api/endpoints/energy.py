from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import EnergyOptimizationPlan
from backend.app.ml.inference_engine import energy_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class EnergyOptimizeRequest(BaseModel):
    building_facility: str = "Tech Campus Science Building A"
    base_load_kwh: float = 480.0

@router.get("/plans")
def get_plans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    plans = db.query(EnergyOptimizationPlan).order_by(EnergyOptimizationPlan.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(plans), "plans": plans}

@router.post("/optimize")
async def optimize_energy(req: EnergyOptimizeRequest, db: Session = Depends(get_db)):
    res = energy_engine.forecast_and_optimize(req.building_facility, req.base_load_kwh)

    plan = EnergyOptimizationPlan(
        plan_id=f"NRG-2026-{uuid.uuid4().hex[:6].upper()}",
        building_facility=req.building_facility,
        forecasted_peak_kwh=res["forecasted_peak_kwh"],
        optimized_peak_kwh=res["optimized_peak_kwh"],
        peak_shaving_reduction_pct=res["peak_shaving_reduction_pct"],
        estimated_daily_savings_usd=res["estimated_daily_savings_usd"],
        co2_reduction_kg=res["co2_reduction_kg"],
        recommended_load_shift_actions=res["recommended_load_shift_actions"]
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    await ws_manager.broadcast({"event": "ENERGY_PLAN_GENERATED", "data": res})
    return {"plan": plan, "metrics": res}
