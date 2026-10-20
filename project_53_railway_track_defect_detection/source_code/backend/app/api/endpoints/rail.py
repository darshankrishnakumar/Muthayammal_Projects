from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
from datetime import datetime
from backend.app.db.session import get_db
from backend.app.db.models import RailwayDefectRecord, AuditLedger
from backend.app.ml.inference_engine import rail_engine, SEGMENT_PRESETS
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class RailInspectRequest(BaseModel):
    chainage_km: str = "KM 144.200"
    track_segment: str = "Line 1 Main Westbound"
    simulated_condition: str = "crack"

@router.get("/presets")
def get_presets():
    return {"presets": list(SEGMENT_PRESETS.values())}

@router.get("/defects")
def get_defects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    track_segment: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RailwayDefectRecord)
    if track_segment:
        query = query.filter(RailwayDefectRecord.track_segment == track_segment)
    if severity:
        query = query.filter(RailwayDefectRecord.severity == severity)

    total = query.count()
    records = query.order_by(RailwayDefectRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"total": total, "count": len(records), "records": records}

@router.post("/inspect")
async def inspect_rail(req: RailInspectRequest, db: Session = Depends(get_db)):
    res = rail_engine.inspect_frame(req.chainage_km, req.track_segment, req.simulated_condition)
    rec_id = f"RAL-2026-{uuid.uuid4().hex[:6].upper()}"
    now_dt = datetime.utcnow()

    # Recompute payload evidence hash with unique rec_id
    payload_str = f"{rec_id}|{req.chainage_km}|{req.track_segment}|{res['defect_type']}|{res['severity']}|{res['confidence']:.4f}|{res['affected_area_px']}|{res['track_quality_index']:.2f}|{res['speed_restriction_kmh']:.1f}|{res['derailment_risk']:.4f}|{now_dt.isoformat()}"
    ev_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    rec = RailwayDefectRecord(
        record_id=rec_id,
        chainage_km=req.chainage_km,
        chainage_numeric_km=res["chainage_numeric_km"],
        track_segment=req.track_segment,
        archetype=res["archetype"],
        timestamp=now_dt,
        defect_type=res["defect_type"],
        severity=res["severity"],
        confidence=res["confidence"],
        affected_area_px=res["affected_area_px"],
        status="Urgent Remediation" if res["severity"] == "Critical" else ("Scheduled Remediation" if res["severity"] == "Moderate" else "Nominal Monitored"),
        recommended_action=res["recommended_action"],
        cant_deficiency_mm=res["cant_deficiency_mm"],
        gauge_deviation_mm=res["gauge_deviation_mm"],
        vertical_profile_roughness=1.8,
        alignment_deviation_mm=1.5,
        sleeper_ballast_void_depth=res["sleeper_ballast_void_depth"],
        rail_temperature_c=28.5,
        fastener_torque_loss_pct=65.0 if res["defect_type"] == "Missing Fastener / Clip" else 12.0,
        vibration_acceleration_g=res["vibration_acceleration_g"],
        axle_load_tons=22.5,
        acoustic_emission_db=75.0,
        track_curvature_rad=0.008,
        track_quality_index=res["track_quality_index"],
        speed_restriction_kmh=res["speed_restriction_kmh"],
        derailment_risk=res["derailment_risk"],
        evidence_hash=ev_hash
    )
    db.add(rec)
    db.flush()

    # Append to cryptographic audit ledger
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    prev_hash = last_block.block_hash if last_block else "0" * 64
    next_index = (last_block.block_index + 1) if last_block else 0
    event_type = "RAIL_CRITICAL_DEFECT_ALERT" if res["severity"] == "Critical" else ("RAIL_DEFECT_DETECTED" if res["severity"] != "None" else "RAIL_NOMINAL_INSPECTION")

    block_payload = f"{next_index}|{now_dt.isoformat()}|{event_type}|{rec_id}|{ev_hash}|{prev_hash}"
    block_hash = hashlib.sha256(block_payload.encode("utf-8")).hexdigest()

    audit_entry = AuditLedger(
        block_index=next_index,
        timestamp=now_dt.isoformat(),
        event_type=event_type,
        record_id=rec_id,
        evidence_hash=ev_hash,
        previous_hash=prev_hash,
        block_hash=block_hash
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(rec)

    res["record_id"] = rec_id
    res["evidence_hash"] = ev_hash
    res["audit_block_index"] = next_index
    res["block_hash"] = block_hash

    await ws_manager.broadcast({"event": "RAIL_DEFECT_DETECTED", "data": res})
    return {"record": rec, "metrics": res}

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).limit(limit).all()
    # Verify chain integrity
    all_blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).all()
    chain_valid = True
    for i in range(1, len(all_blocks)):
        if all_blocks[i].previous_hash != all_blocks[i-1].block_hash:
            chain_valid = False
            break

    return {
        "chain_valid": chain_valid,
        "total_blocks": len(all_blocks),
        "genesis_block_hash": all_blocks[0].block_hash if all_blocks else None,
        "latest_block_hash": all_blocks[-1].block_hash if all_blocks else None,
        "blocks": blocks
    }
