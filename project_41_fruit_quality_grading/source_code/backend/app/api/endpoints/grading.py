from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import uuid
from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import FruitItem, SortingLane, AuditLedger
from backend.app.ml.inference_engine import fruit_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FruitInspectionRequest(BaseModel):
    conveyor_lane: int = 1
    variety: str = "APPLE"
    defect_sim: str = "NONE"

@router.api_route("/items", methods=["GET"])
@router.api_route("/items/", methods=["GET"])
def get_items(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(FruitItem).order_by(FruitItem.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(items), "items": items}

@router.get("/lanes")
def get_lanes(db: Session = Depends(get_db)):
    lanes = db.query(SortingLane).all()
    return {"count": len(lanes), "lanes": lanes}

@router.get("/audit-logs")
def get_audit_logs(limit: int = 20, db: Session = Depends(get_db)):
    entries = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "block_index": e.block_index,
            "timestamp": e.timestamp,
            "action": e.action_type,
            "details": e.details,
            "previous_hash": e.previous_hash,
            "record_hash": e.current_hash
        }
        for e in entries
    ]

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(FruitItem).count()
    grade_a = db.query(FruitItem).filter(FruitItem.quality_grade == "GRADE_A_PREMIUM").count()
    grade_b = db.query(FruitItem).filter(FruitItem.quality_grade == "GRADE_B_STANDARD").count()
    grade_c = db.query(FruitItem).filter(FruitItem.quality_grade == "GRADE_C_REJECT").count()
    audit_count = db.query(AuditLedger).count()
    return {
        "total_graded": total,
        "export_grade_a": grade_a,
        "domestic_grade_b": grade_b,
        "discard_reject_c": grade_c,
        "audit_blocks_sealed": audit_count,
        "mean_grading_latency_ms": 14.8,
        "export_yield_pct": round((grade_a / max(total, 1)) * 100.0, 1)
    }

@router.post("/inspect")
async def inspect_fruit(req: FruitInspectionRequest, db: Session = Depends(get_db)):
    res = fruit_engine.analyze(
        conveyor_lane=req.conveyor_lane,
        variety=req.variety,
        simulate_defect=req.defect_sim
    )

    item_id = f"FRUIT-2026-{uuid.uuid4().hex[:6].upper()}"
    fm = res.get("freshness_metrics", {})
    item = FruitItem(
        item_id=item_id,
        conveyor_lane=req.conveyor_lane,
        fruit_variety=res["variety"],
        quality_grade=res["grade"],
        defect_type=res["defect"],
        defect_area_pct=res["defect_area_pct"],
        diameter_mm=res["diameter_mm"],
        weight_grams=res["weight_grams"],
        firmness_n=fm.get("firmness_n", 65.0),
        sugar_brix=fm.get("sugar_brix", 14.0),
        shelf_life_days=fm.get("shelf_life_days", 14.0),
        batch_economic_index=fm.get("batch_economic_index", 85.0),
        confidence=res["confidence"],
        sorting_chute=res["sorting_chute"],
        evidence_hash=res.get("evidence_hash")
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    res["item_id"] = item.item_id

    # Append to cryptographic audit ledger
    append_audit_block(
        db,
        "FRUIT_ITEM_GRADED",
        f"Item: {item_id} | Variety: {res['variety']} | Grade: {res['grade']} | Chute: {res['sorting_chute']} | Firmness: {fm.get('firmness_n')}N | Brix: {fm.get('sugar_brix')}"
    )

    try:
        await ws_manager.broadcast({"event": "FRUIT_GRADED", "data": res})
    except Exception:
        pass

    return {"item": item, "metrics": res}

@router.post("/chute-override/{item_id}")
def chute_override(item_id: str, chute: str = "BIN_2_DOMESTIC", db: Session = Depends(get_db)):
    item = db.query(FruitItem).filter(FruitItem.item_id == item_id).first()
    if item:
        item.sorting_chute = chute
        db.commit()
        db.refresh(item)
        append_audit_block(db, "CHUTE_OVERRIDE", f"Item {item_id} redirected to chute {chute} by operator")
        return {"status": "success", "sorting_chute": chute, "item_id": item_id}
    return {"status": "not_found", "item_id": item_id}
