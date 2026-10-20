from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
from datetime import datetime
from backend.app.db.session import get_db
from backend.app.db.models import WeatherForecastRecord, AuditLedger
from backend.app.ml.inference_engine import weather_engine, STATION_PRESETS
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class WeatherNowcastRequest(BaseModel):
    station_name: str = "Coastal Maritime Radar Station 01"
    lead_time_hours: int = 3
    simulated_condition: str = "severe_storm"

@router.get("/presets")
def get_presets():
    return {"presets": list(STATION_PRESETS.values())}

@router.get("/forecasts")
def get_forecasts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    station_name: Optional[str] = None,
    severity_tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WeatherForecastRecord)
    if station_name:
        query = query.filter(WeatherForecastRecord.station_name == station_name)
    if severity_tier:
        query = query.filter(WeatherForecastRecord.severity_tier == severity_tier)

    total = query.count()
    records = query.order_by(WeatherForecastRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"total": total, "count": len(records), "records": records}

@router.post("/nowcast")
async def predict_weather(req: WeatherNowcastRequest, db: Session = Depends(get_db)):
    res = weather_engine.forecast_event(
        req.station_name,
        req.lead_time_hours,
        req.simulated_condition
    )

    rec_id = f"WTH-2026-{uuid.uuid4().hex[:6].upper()}"
    now_dt = datetime.utcnow()

    # Deterministic evidence hash with rec_id
    payload_str = f"{rec_id}|{req.station_name}|{res['archetype']}|{res['event_class']}|{res['severity_tier']}|{res['confidence']:.4f}|{req.lead_time_hours}|{res['temperature_c']:.1f}|{res['barometric_pressure_hpa']:.1f}|{res['wind_speed_kmh']:.1f}|{res['radar_reflectivity_dbz']:.1f}|{res['precipitation_rate_mmh']:.1f}|{res['severe_weather_risk']:.4f}|{now_dt.isoformat()}"
    ev_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    rec = WeatherForecastRecord(
        record_id=rec_id,
        station_name=req.station_name,
        archetype=res["archetype"],
        timestamp=now_dt,
        event_class=res["event_class"],
        lead_time_hours=req.lead_time_hours,
        alert_issued=res["alert_issued"],
        severity_tier=res["severity_tier"],
        confidence=res["confidence"],
        advisory_directive=res["advisory_directive"],
        temperature_c=res["temperature_c"],
        barometric_pressure_hpa=res["barometric_pressure_hpa"],
        wind_speed_kmh=res["wind_speed_kmh"],
        humidity_pct=res["humidity_pct"],
        radar_reflectivity_dbz=res["radar_reflectivity_dbz"],
        dew_point_c=res["dew_point_c"],
        solar_irradiance_wm2=res["solar_irradiance_wm2"],
        cape_joules=res["cape_joules"],
        lifted_index_c=res["lifted_index_c"],
        wind_gust_kmh=res["wind_gust_kmh"],
        pwat_mm=res["pwat_mm"],
        station_elevation_m=res["station_elevation_m"],
        precipitation_rate_mmh=res["precipitation_rate_mmh"],
        severe_weather_risk=res["severe_weather_risk"],
        nowcasting_accuracy=res["nowcasting_accuracy"],
        evidence_hash=ev_hash
    )
    db.add(rec)
    db.flush()

    # Append to cryptographic audit ledger
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    prev_hash = last_block.block_hash if last_block else "0" * 64
    next_index = (last_block.block_index + 1) if last_block else 0
    event_type = "SEVERE_WEATHER_ALERT" if res["alert_issued"] else "ROUTINE_NOWCAST_UPDATE"

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

    await ws_manager.broadcast({"event": "WEATHER_ALERT" if res["alert_issued"] else "WEATHER_UPDATE", "data": res})
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
