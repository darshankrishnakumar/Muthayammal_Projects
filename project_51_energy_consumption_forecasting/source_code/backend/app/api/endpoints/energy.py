import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.app.db.session import get_db
from backend.app.db.models import EnergyOptimizationPlan, AuditLedger
from backend.app.ml.inference_engine import energy_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class EnergyOptimizeRequest(BaseModel):
    building_facility: str = "Tech Campus Science Complex A"
    facility_archetype: str = "COMMERCIAL_OFFICE_CAMPUS"
    base_load_kw: float = 480.0
    ambient_temp_c: float = 26.5
    relative_humidity_pct: float = 58.0
    tou_tariff_cents_kwh: float = 18.5
    renewable_penetration_pct: float = 35.0
    custom_features: Optional[Dict[str, float]] = None

def plan_to_dict(p: EnergyOptimizationPlan) -> dict:
    return {
        "id": p.id,
        "plan_id": p.plan_id,
        "facility_archetype": p.facility_archetype,
        "building_facility": p.building_facility,
        "ambient_temp_c": p.ambient_temp_c,
        "relative_humidity_pct": p.relative_humidity_pct,
        "base_load_kw": p.base_load_kw,
        "ev_charging_load_kw": p.ev_charging_load_kw,
        "tou_tariff_cents_kwh": p.tou_tariff_cents_kwh,
        "renewable_penetration_pct": p.renewable_penetration_pct,
        "forecasted_peak_kwh": p.forecasted_peak_kwh,
        "optimized_peak_kwh": p.optimized_peak_kwh,
        "peak_shaving_reduction_pct": p.peak_shaving_reduction_pct,
        "estimated_daily_savings_usd": p.estimated_daily_savings_usd,
        "co2_reduction_kg": p.co2_reduction_kg,
        "grid_stress_index": p.grid_stress_index,
        "carbon_intensity_gco2": p.carbon_intensity_gco2,
        "curtailment_risk_prob": p.curtailment_risk_prob,
        "recommended_load_shift_actions": p.recommended_load_shift_actions,
        "evidence_hash": p.evidence_hash,
        "timestamp": p.timestamp.isoformat() if p.timestamp else ""
    }

def audit_to_dict(b: AuditLedger) -> dict:
    return {
        "block_index": b.block_index,
        "timestamp": b.timestamp,
        "event_type": b.event_type,
        "plan_id": b.plan_id,
        "evidence_hash": b.evidence_hash,
        "previous_hash": b.previous_hash,
        "block_hash": b.block_hash
    }

@router.get("/plans")
def get_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    facility_archetype: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(EnergyOptimizationPlan)
    if facility_archetype:
        query = query.filter(EnergyOptimizationPlan.facility_archetype == facility_archetype)

    total = query.count()
    plans = query.order_by(EnergyOptimizationPlan.id.desc()).offset(skip).limit(limit).all()
    return {
        "count": len(plans),
        "total": total,
        "plans": [plan_to_dict(p) for p in plans]
    }

@router.get("/presets")
def get_energy_presets():
    return {
        "presets": [
            {
                "id": "tech_campus",
                "label": "Tech Campus Science Complex A (Commercial Office)",
                "building_facility": "Tech Campus Science Complex A",
                "facility_archetype": "COMMERCIAL_OFFICE_CAMPUS",
                "base_load_kw": 480.0,
                "ambient_temp_c": 26.5,
                "relative_humidity_pct": 58.0,
                "tou_tariff_cents_kwh": 18.5,
                "renewable_penetration_pct": 35.0
            },
            {
                "id": "auto_assembly",
                "label": "Automotive Stamping Assembly 4 (Industrial Plant)",
                "building_facility": "Automotive Stamping Assembly 4",
                "facility_archetype": "INDUSTRIAL_MANUFACTURING_PLANT",
                "base_load_kw": 850.0,
                "ambient_temp_c": 28.0,
                "relative_humidity_pct": 52.0,
                "tou_tariff_cents_kwh": 22.0,
                "renewable_penetration_pct": 24.0
            },
            {
                "id": "cloud_datacenter",
                "label": "Hyperscale Cloud Facility DC-2 (Data Center)",
                "building_facility": "Hyperscale Cloud Facility DC-2",
                "facility_archetype": "DATA_CENTER_HYPERSCALE",
                "base_load_kw": 1200.0,
                "ambient_temp_c": 21.0,
                "relative_humidity_pct": 45.0,
                "tou_tariff_cents_kwh": 14.2,
                "renewable_penetration_pct": 48.0
            },
            {
                "id": "metro_hospital",
                "label": "Metro General Healthcare Complex (Hospital)",
                "building_facility": "Metro General Healthcare Complex",
                "facility_archetype": "MUNICIPAL_HOSPITAL_COMPLEX",
                "base_load_kw": 620.0,
                "ambient_temp_c": 25.0,
                "relative_humidity_pct": 60.0,
                "tou_tariff_cents_kwh": 19.8,
                "renewable_penetration_pct": 30.0
            }
        ]
    }

@router.post("/optimize")
async def optimize_energy(req: EnergyOptimizeRequest, db: Session = Depends(get_db)):
    res = energy_engine.forecast_and_optimize(
        building_facility=req.building_facility,
        facility_archetype=req.facility_archetype,
        base_load_kw=req.base_load_kw,
        ambient_temp_c=req.ambient_temp_c,
        relative_humidity_pct=req.relative_humidity_pct,
        tou_tariff_cents_kwh=req.tou_tariff_cents_kwh,
        renewable_penetration_pct=req.renewable_penetration_pct,
        custom_features=req.custom_features
    )

    plan_id = f"PLAN-2026-{uuid.uuid4().hex[:6].upper()}"

    plan = EnergyOptimizationPlan(
        plan_id=plan_id,
        facility_archetype=res["facility_archetype"],
        building_facility=res["building_facility"],
        ambient_temp_c=res["features"]["ambient_temp_c"],
        relative_humidity_pct=res["features"]["relative_humidity_pct"],
        base_load_kw=req.base_load_kw,
        ev_charging_load_kw=req.base_load_kw * 0.15,
        tou_tariff_cents_kwh=res["features"]["tou_tariff_cents_kwh"],
        renewable_penetration_pct=res["features"]["renewable_penetration_pct"],
        forecasted_peak_kwh=res["forecasted_peak_kwh"],
        optimized_peak_kwh=res["optimized_peak_kwh"],
        peak_shaving_reduction_pct=res["peak_shaving_reduction_pct"],
        estimated_daily_savings_usd=res["estimated_daily_savings_usd"],
        co2_reduction_kg=res["co2_reduction_kg"],
        grid_stress_index=res["grid_stress_index"],
        carbon_intensity_gco2=res["carbon_intensity_gco2"],
        curtailment_risk_prob=res["curtailment_risk_prob"],
        recommended_load_shift_actions=res["recommended_load_shift_actions"],
        evidence_hash=res["evidence_hash"],
        extracted_json_payload=json.dumps(res),
        timestamp=datetime.now(timezone.utc)
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Append block to audit ledger
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    prev_hash = last_block.block_hash if last_block else "0000000000000000000000000000000000000000000000000000000000000000"
    b_idx = (last_block.block_index + 1) if last_block else 0
    b_ts = datetime.now(timezone.utc).isoformat()
    ev_type = "PEAK_SHAVING_DISPATCHED" if res["peak_shaving_reduction_pct"] >= 20.0 else "ENERGY_OPTIMIZATION_PLANNED"
    raw_payload = f"{b_idx}|{b_ts}|{ev_type}|{plan_id}|{res['evidence_hash']}|{prev_hash}"
    b_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

    new_block = AuditLedger(
        block_index=b_idx,
        timestamp=b_ts,
        event_type=ev_type,
        plan_id=plan_id,
        evidence_hash=res["evidence_hash"],
        previous_hash=prev_hash,
        block_hash=b_hash
    )
    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    res["block_index"] = b_idx
    res["block_hash"] = b_hash
    res["plan_id"] = plan_id

    try:
        await ws_manager.broadcast({"event": "PLAN_OPTIMIZED", "data": res})
    except Exception:
        pass

    return {
        "plan": plan_to_dict(plan),
        "metrics": res,
        "audit_block": audit_to_dict(new_block)
    }

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    all_blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
    chain_valid = True
    for i in range(1, len(all_blocks)):
        if all_blocks[i].previous_hash != all_blocks[i-1].block_hash:
            chain_valid = False
            break

    return {
        "chain_valid": chain_valid,
        "total_blocks": len(all_blocks),
        "blocks": [audit_to_dict(b) for b in blocks]
    }
