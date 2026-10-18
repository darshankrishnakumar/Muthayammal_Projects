from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import WeatherForecastRecord
from backend.app.ml.inference_engine import weather_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class WeatherNowcastRequest(BaseModel):
    location_station: str = "Met Station Coastal Radar 01"
    lead_time_hours: int = 3
    temperature_c: float = 29.0
    pressure_hpa: float = 993.5
    wind_kmh: float = 62.0
    humidity_pct: float = 91.0
    radar_reflectivity_dbz: float = 51.5

@router.get("/forecasts")
def get_forecasts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    records = db.query(WeatherForecastRecord).order_by(WeatherForecastRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(records), "records": records}

@router.post("/nowcast")
async def predict_weather(req: WeatherNowcastRequest, db: Session = Depends(get_db)):
    res = weather_engine.forecast_event(
        req.location_station,
        req.lead_time_hours,
        req.temperature_c,
        req.pressure_hpa,
        req.wind_kmh,
        req.humidity_pct,
        req.radar_reflectivity_dbz
    )

    rec = WeatherForecastRecord(
        forecast_id=f"WTH-2026-{uuid.uuid4().hex[:6].upper()}",
        location_station=req.location_station,
        event_class=res["event_class"],
        event_probability=res["event_probability"],
        lead_time_hours=req.lead_time_hours,
        temperature_c=req.temperature_c,
        barometric_pressure_hpa=req.pressure_hpa,
        wind_speed_kmh=req.wind_kmh,
        humidity_pct=req.humidity_pct,
        radar_reflectivity_dbz=req.radar_reflectivity_dbz,
        alert_issued=res["alert_issued"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    await ws_manager.broadcast({"event": "WEATHER_ALERT" if res["alert_issued"] else "WEATHER_UPDATE", "data": res})
    return {"record": rec, "metrics": res}
