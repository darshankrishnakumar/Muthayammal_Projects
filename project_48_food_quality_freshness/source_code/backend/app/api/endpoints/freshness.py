import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime

from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import FoodBatch, FreshnessAssessment, AuditLedger
from backend.app.ml.inference_engine import freshness_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FreshnessInspectRequest(BaseModel):
    product_name: str = Field(default="Prime Ribeye Beef Cut")
    food_category: str = Field(default="MEAT_POULTRY")
    food_name: Optional[str] = None # Support alias
    simulated_spoilage: Optional[str] = "fresh" # Support UI select
    simulate_spoilage: bool = False
    
    # Optional direct telemetry overrides
    storage_temp_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    storage_duration_hours: Optional[float] = None
    browning_index: Optional[float] = None
    tvbn_mg_per_100g: Optional[float] = None
    ph_level: Optional[float] = None
    ethylene_concentration_ppm: Optional[float] = None
    moisture_content_pct: Optional[float] = None
    bacterial_log_cfu_g: Optional[float] = None
    reflectance_ratio_650_850: Optional[float] = None

def serialize_batch(b: FoodBatch) -> dict:
    return {
        "id": b.id,
        "batch_id": b.batch_id,
        "sample_id": b.batch_id,
        "food_category": b.food_category,
        "product_name": b.product_name,
        "food_name": b.product_name,
        "supplier_origin": b.supplier_origin,
        "storage_facility": b.storage_facility,
        "freshness_score": b.freshness_score,
        "deterioration_stage": b.deterioration_stage,
        "safety_status": b.deterioration_stage.replace("STAGE_1_", "").replace("STAGE_2_", "").replace("STAGE_3_", ""),
        "estimated_shelf_life_hours": b.estimated_shelf_life_hours,
        "remaining_shelf_life_days": b.remaining_shelf_life_days,
        "browning_index": b.browning_index,
        "spoilage_area_pct": b.spoilage_area_pct,
        "microbial_risk_pct": b.microbial_risk_pct,
        "cold_chain_compliance_score": b.cold_chain_compliance_score,
        "recommendation": b.recommendation,
        "advisory_note": f"{b.recommendation.replace('_', ' ')}: {b.remaining_shelf_life_days} days remaining",
        "timestamp": b.timestamp.isoformat() if b.timestamp else None
    }

def serialize_assessment(a: FreshnessAssessment) -> dict:
    return {
        "id": a.id,
        "sample_id": a.sample_id,
        "batch_id": a.batch_id,
        "food_category": a.food_category,
        "product_name": a.product_name,
        "storage_temp_c": a.storage_temp_c,
        "relative_humidity_pct": a.relative_humidity_pct,
        "storage_duration_hours": a.storage_duration_hours,
        "browning_index": a.browning_index,
        "tvbn_mg_per_100g": a.tvbn_mg_per_100g,
        "ph_level": a.ph_level,
        "ethylene_concentration_ppm": a.ethylene_concentration_ppm,
        "moisture_content_pct": a.moisture_content_pct,
        "bacterial_log_cfu_g": a.bacterial_log_cfu_g,
        "reflectance_ratio_650_850": a.reflectance_ratio_650_850,
        "freshness_score": a.freshness_score,
        "deterioration_stage": a.deterioration_stage,
        "estimated_shelf_life_hours": a.estimated_shelf_life_hours,
        "remaining_shelf_life_days": a.remaining_shelf_life_days,
        "spoilage_risk_pct": a.spoilage_risk_pct,
        "microbial_risk_pct": a.microbial_risk_pct,
        "cold_chain_compliance_score": a.cold_chain_compliance_score,
        "advisory_recommendation": a.advisory_recommendation,
        "evidence_hash": a.evidence_hash,
        "timestamp": a.timestamp.isoformat() if a.timestamp else None
    }

@router.get("/batches")
def get_batches(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    batches = db.query(FoodBatch).order_by(FoodBatch.timestamp.desc()).offset(skip).limit(limit).all()
    serialized = [serialize_batch(b) for b in batches]
    return {"count": len(serialized), "batches": serialized, "records": serialized}

@router.get("/records")
def get_records_alias(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint for /api/freshness/records or /api/food/records"""
    return get_batches(skip, limit, db)

@router.get("/assessments")
def get_assessments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    assessments = db.query(FreshnessAssessment).order_by(FreshnessAssessment.timestamp.desc()).offset(skip).limit(limit).all()
    serialized = [serialize_assessment(a) for a in assessments]
    return {"count": len(serialized), "assessments": serialized}

@router.get("/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).offset(skip).limit(limit).all()
    
    # Cryptographic integrity verification
    chain_valid = True
    tamper_details = []
    
    for i in range(len(blocks)):
        curr = blocks[i]
        if i > 0:
            prev = blocks[i - 1]
            if curr.previous_hash != prev.block_hash:
                chain_valid = False
                tamper_details.append(f"Block #{curr.block_index} previous_hash mismatch: expected {prev.block_hash}, got {curr.previous_hash}")

    serialized = [{
        "block_index": b.block_index,
        "previous_hash": b.previous_hash,
        "block_hash": b.block_hash,
        "timestamp": b.timestamp.isoformat() if b.timestamp else None,
        "event_type": b.event_type,
        "evidence_hash": b.evidence_hash
    } for b in blocks]
    
    return {
        "total_blocks": len(serialized),
        "chain_verified": chain_valid,
        "tamper_detected": not chain_valid,
        "tamper_details": tamper_details,
        "blocks": serialized
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(FoodBatch).count()
    assessments_count = db.query(FreshnessAssessment).count()
    fresh_count = db.query(FoodBatch).filter(FoodBatch.deterioration_stage == "STAGE_1_FRESH").count()
    marginal_count = db.query(FoodBatch).filter(FoodBatch.deterioration_stage == "STAGE_2_MARGINAL").count()
    deteriorated_count = db.query(FoodBatch).filter(FoodBatch.deterioration_stage == "STAGE_3_DETERIORATED").count()
    
    all_scores = [b.freshness_score for b in db.query(FoodBatch.freshness_score).all()]
    mean_score = round(float(np.mean(all_scores)), 1) if all_scores else 85.0
    
    all_shelf = [b.remaining_shelf_life_days for b in db.query(FoodBatch.remaining_shelf_life_days).all()]
    mean_shelf = round(float(np.mean(all_shelf)), 1) if all_shelf else 5.2
    
    return {
        "total_batches": total,
        "total_assessments": assessments_count,
        "mean_freshness_index": mean_score,
        "mean_remaining_shelf_days": mean_shelf,
        "stage_breakdown": {
            "STAGE_1_FRESH": fresh_count,
            "STAGE_2_MARGINAL": marginal_count,
            "STAGE_3_DETERIORATED": deteriorated_count
        }
    }

@router.post("/evaluate")
async def evaluate_batch(req: FreshnessInspectRequest, db: Session = Depends(get_db)):
    product = req.product_name or req.food_name or "Prime Ribeye Beef Cut"
    cat = req.food_category
    
    # Infer food category if needed
    if "Beef" in product or "Salmon" in product or "Chicken" in product or "Pork" in product:
        cat = "MEAT_POULTRY"
    elif "Avocado" in product or "Spinach" in product or "Lettuce" in product or "Strawberry" in product:
        cat = "FRESH_PRODUCE"
    elif "Milk" in product or "Cheese" in product or "Cheddar" in product or "Yogurt" in product:
        cat = "DAIRY"
    elif "Sourdough" in product or "Loaf" in product or "Croissant" in product or "Brioche" in product:
        cat = "BAKERY"

    # Spoilage simulation flag
    spoil = req.simulate_spoilage or (req.simulated_spoilage in ["moderate", "spoiled"])
    
    # Synthetic physical image patch (3, 64, 64)
    if spoil:
        mock_food = np.zeros((3, 64, 64), dtype=np.float32)
        mock_food[0] = 0.90 # Browning
        mock_food[1] = 0.10
        mock_food[2] = 0.05
    else:
        mock_food = np.zeros((3, 64, 64), dtype=np.float32)
        mock_food[0] = 0.15 # Minimal oxidation
        mock_food[1] = 0.85 # High fresh pigment
        mock_food[2] = 0.65
        mock_food += np.random.normal(0, 0.02, (3, 64, 64)).astype(np.float32)
        mock_food = np.clip(mock_food, 0.0, 1.0)
        
    telemetry_input = {}
    if req.storage_temp_c is not None: telemetry_input["storage_temp_c"] = req.storage_temp_c
    if req.relative_humidity_pct is not None: telemetry_input["relative_humidity_pct"] = req.relative_humidity_pct
    if req.storage_duration_hours is not None: telemetry_input["storage_duration_hours"] = req.storage_duration_hours
    if req.browning_index is not None: telemetry_input["browning_index"] = req.browning_index
    if req.tvbn_mg_per_100g is not None: telemetry_input["tvbn_mg_per_100g"] = req.tvbn_mg_per_100g
    if req.ph_level is not None: telemetry_input["ph_level"] = req.ph_level
    if req.ethylene_concentration_ppm is not None: telemetry_input["ethylene_concentration_ppm"] = req.ethylene_concentration_ppm
    if req.moisture_content_pct is not None: telemetry_input["moisture_content_pct"] = req.moisture_content_pct
    if req.bacterial_log_cfu_g is not None: telemetry_input["bacterial_log_cfu_g"] = req.bacterial_log_cfu_g
    if req.reflectance_ratio_650_850 is not None: telemetry_input["reflectance_ratio_650_850"] = req.reflectance_ratio_650_850

    # Real PyTorch forward pass via dual engines
    res = freshness_engine.evaluate_item(img_rgb=mock_food, telemetry=telemetry_input, simulate_spoilage=spoil)

    # Persist Batch & Assessment
    b_id = f"FOOD-{uuid.uuid4().hex[:6].upper()}"
    batch = FoodBatch(
        batch_id=b_id,
        food_category=cat,
        product_name=product,
        supplier_origin="Pacific Northwest Agro Hub",
        storage_facility="Cold Storage Bay #1",
        freshness_score=res["freshness_score"],
        deterioration_stage=res["deterioration_stage"],
        estimated_shelf_life_hours=res["estimated_shelf_life_hours"],
        remaining_shelf_life_days=res["remaining_shelf_life_days"],
        browning_index=res["browning_index"],
        spoilage_area_pct=res["spoilage_area_pct"],
        microbial_risk_pct=res["microbial_risk_pct"],
        cold_chain_compliance_score=res["cold_chain_compliance_score"],
        recommendation=res["recommendation"]
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    assessment = FreshnessAssessment(
        sample_id=f"SAMPLE-{b_id}",
        batch_id=b_id,
        food_category=cat,
        product_name=product,
        storage_temp_c=res["storage_temp_c"],
        relative_humidity_pct=res["relative_humidity_pct"],
        storage_duration_hours=telemetry_input.get("storage_duration_hours", 24.0),
        browning_index=res["browning_index"],
        tvbn_mg_per_100g=res["tvbn_mg_per_100g"],
        ph_level=res["ph_level"],
        ethylene_concentration_ppm=res["ethylene_concentration_ppm"],
        moisture_content_pct=telemetry_input.get("moisture_content_pct", 75.0),
        bacterial_log_cfu_g=res["bacterial_log_cfu_g"],
        reflectance_ratio_650_850=telemetry_input.get("reflectance_ratio_650_850", 1.45),
        freshness_score=res["freshness_score"],
        deterioration_stage=res["deterioration_stage"],
        estimated_shelf_life_hours=res["estimated_shelf_life_hours"],
        remaining_shelf_life_days=res["remaining_shelf_life_days"],
        spoilage_risk_pct=res["spoilage_risk_pct"],
        microbial_risk_pct=res["microbial_risk_pct"],
        cold_chain_compliance_score=res["cold_chain_compliance_score"],
        advisory_recommendation=res["recommendation"],
        evidence_hash=res["evidence_hash"]
    )
    db.add(assessment)
    db.commit()

    # Append block to cryptographic audit ledger
    append_audit_block(
        db=db,
        event_type="QUALITY_EVALUATION",
        details={
            "batch_id": b_id,
            "product_name": product,
            "freshness_score": res["freshness_score"],
            "deterioration_stage": res["deterioration_stage"],
            "remaining_shelf_life_days": res["remaining_shelf_life_days"],
            "spoilage_risk_pct": res["spoilage_risk_pct"]
        },
        evidence_hash=res["evidence_hash"]
    )

    batch_dict = serialize_batch(batch)
    
    # Broadcast to WebSocket
    await ws_manager.broadcast({
        "event": "FRESHNESS_INSPECTED",
        "batch": batch_dict,
        "metrics": res
    })

    # Return structure matching both frontend and API contracts
    return {
        "sample_id": b_id,
        "food_name": product,
        "freshness_score": res["freshness_score"],
        "safety_status": res["deterioration_stage"].replace("STAGE_1_", "").replace("STAGE_2_", "").replace("STAGE_3_", ""),
        "remaining_shelf_life_days": res["remaining_shelf_life_days"],
        "advisory_note": res["advisory_note"],
        "batch": batch_dict,
        "metrics": res
    }

@router.post("/inspect")
async def inspect_batch_alias(req: FreshnessInspectRequest, db: Session = Depends(get_db)):
    """Frontend compatibility endpoint for /api/food/inspect or /api/freshness/inspect"""
    return await evaluate_batch(req, db)
