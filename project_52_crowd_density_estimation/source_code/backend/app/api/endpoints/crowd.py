from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
from datetime import datetime
from backend.app.db.session import get_db
from backend.app.db.models import CrowdMonitoringEvent, AuditLedger
from backend.app.ml.inference_engine import crowd_engine, ZONE_PRESETS
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class CrowdAnalyzeRequest(BaseModel):
    zone_name: str = "Central Plaza Concourse"
    simulation_level: str = "moderate"

@router.get("/presets")
def get_presets():
    return {"presets": list(ZONE_PRESETS.values())}

@router.get("/events")
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    zone_name: Optional[str] = None,
    anomaly_only: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CrowdMonitoringEvent)
    if zone_name:
        query = query.filter(CrowdMonitoringEvent.zone_name == zone_name)
    if anomaly_only is not None:
        query = query.filter(CrowdMonitoringEvent.anomaly_detected == anomaly_only)
    
    total = query.count()
    events = query.order_by(CrowdMonitoringEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return {"total": total, "count": len(events), "events": events}

@router.post("/analyze")
async def analyze_crowd_feed(req: CrowdAnalyzeRequest, db: Session = Depends(get_db)):
    res = crowd_engine.analyze_scene(req.zone_name, req.simulation_level)
    event_id = f"CRW-2026-{uuid.uuid4().hex[:6].upper()}"
    now_dt = datetime.utcnow()

    # Recompute payload evidence hash with event_id
    payload_str = f"{event_id}|{res['zone_name']}|{res['archetype']}|{res['estimated_headcount']}|{res['density_level']}|{res['anomaly_detected']}|{res['anomaly_type']}|{res['risk_score']:.4f}|{res['optical_flow_turbulence']:.4f}|{now_dt.isoformat()}"
    ev_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    event = CrowdMonitoringEvent(
        event_id=event_id,
        zone_name=req.zone_name,
        archetype=res["archetype"],
        timestamp=now_dt,
        estimated_headcount=res["estimated_headcount"],
        density_level=res["density_level"],
        anomaly_detected=res["anomaly_detected"],
        anomaly_type=res["anomaly_type"],
        risk_score=res["risk_score"],
        optical_flow_turbulence=res["optical_flow_turbulence"],
        flow_velocity_mps=res["flow_velocity_mps"],
        spatial_divergence=res["spatial_divergence"],
        kinetic_energy_entropy=res["kinetic_energy_entropy"],
        density_ratio_sqm=res["density_ratio_sqm"],
        bottleneck_pressure_psi=res["bottleneck_pressure_psi"],
        directional_coherence=res["directional_coherence"],
        velocity_variance=res["velocity_variance"],
        occlusion_ratio=res["occlusion_ratio"],
        ambient_lighting_lux=res["ambient_lighting_lux"],
        panic_index=res["panic_index"],
        evidence_hash=ev_hash
    )
    db.add(event)
    db.flush()

    # Append to cryptographic audit ledger
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    prev_hash = last_block.block_hash if last_block else "0" * 64
    next_index = (last_block.block_index + 1) if last_block else 0
    event_type = "CROWD_ANOMALY_ALERT" if res["anomaly_detected"] else "CROWD_MONITORING_SCAN"

    block_payload = f"{next_index}|{now_dt.isoformat()}|{event_type}|{event_id}|{ev_hash}|{prev_hash}"
    block_hash = hashlib.sha256(block_payload.encode("utf-8")).hexdigest()

    audit_entry = AuditLedger(
        block_index=next_index,
        timestamp=now_dt.isoformat(),
        event_type=event_type,
        event_id=event_id,
        evidence_hash=ev_hash,
        previous_hash=prev_hash,
        block_hash=block_hash
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(event)

    res["event_id"] = event_id
    res["evidence_hash"] = ev_hash
    res["audit_block_index"] = next_index
    res["block_hash"] = block_hash

    await ws_manager.broadcast({"event": "CROWD_ANOMALY_ALERT" if res["anomaly_detected"] else "CROWD_UPDATE", "data": res})
    return {"event": event, "metrics": res}

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
