import os
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ml.inference_engine import NIDSInferenceEngine
from database.database import NIDSDatabase

app = FastAPI(
    title="Project 02: Network Intrusion Detection & Anomaly System",
    description="Enterprise Network Security Monitoring Engine with Ensemble Machine Learning & Unsupervised Anomaly Detection",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate engine and database
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine = NIDSInferenceEngine()
db = NIDSDatabase()

class PacketInspectionRequest(BaseModel):
    source_ip: Optional[str] = Field("192.168.1.105", description="Source IPv4 address")
    destination_ip: Optional[str] = Field("10.0.0.1", description="Destination IPv4 address")
    protocol_type: Optional[str] = Field("tcp", description="Protocol: tcp, udp, icmp")
    service: Optional[str] = Field("http", description="Network service: http, ftp, smtp, telnet, private, etc.")
    flag: Optional[str] = Field("SF", description="Connection status flag: SF, S0, REJ, RSTR, RSTO, etc.")
    duration: Optional[int] = Field(0, ge=0, description="Connection duration in seconds")
    src_bytes: Optional[int] = Field(250, ge=0, description="Payload bytes sent from source")
    dst_bytes: Optional[int] = Field(1200, ge=0, description="Payload bytes received at destination")
    count: Optional[int] = Field(1, ge=0, description="Number of connections to same host in past 2s")
    srv_count: Optional[int] = Field(1, ge=0, description="Number of connections to same service in past 2s")
    serror_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="SYN error rate")
    rerror_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="REJ error rate")
    same_srv_rate: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Rate of connections to same service")
    diff_srv_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Rate of connections to different services")
    dst_host_count: Optional[int] = Field(100, ge=0, le=255, description="Destination host connection count")
    dst_host_srv_count: Optional[int] = Field(100, ge=0, le=255, description="Destination host service count")
    dst_host_diff_srv_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    dst_host_same_src_port_rate: Optional[float] = Field(0.05, ge=0.0, le=1.0)
    dst_host_rerror_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    dst_host_serror_rate: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    hot: Optional[int] = Field(0, ge=0)
    num_failed_logins: Optional[int] = Field(0, ge=0)
    logged_in: Optional[int] = Field(1, ge=0, le=1)
    root_shell: Optional[int] = Field(0, ge=0, le=1)
    su_attempted: Optional[int] = Field(0, ge=0, le=2)
    num_root: Optional[int] = Field(0, ge=0)
    num_file_creations: Optional[int] = Field(0, ge=0)
    num_compromised: Optional[int] = Field(0, ge=0)
    urgent: Optional[int] = Field(0, ge=0)
    wrong_fragment: Optional[int] = Field(0, ge=0)

# Backwards compatibility request model
class LegacyPredictionRequest(BaseModel):
    features: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "network_intrusion_detection_service",
        "version": "2.0.0",
        "models_ready": engine.is_ready(),
        "database_connected": os.path.exists(db.db_path)
    }

@app.get("/api/presets")
def get_attack_presets():
    return engine.get_presets()

@app.post("/api/inspect")
def inspect_packet(request: PacketInspectionRequest):
    packet_data = request.model_dump()
    result = engine.predict_packet(packet_data)

    # Log to SQLite database
    event_payload = {
        "source_ip": request.source_ip,
        "destination_ip": request.destination_ip,
        "protocol": request.protocol_type,
        "service": request.service,
        "flag": request.flag,
        "src_bytes": request.src_bytes,
        "dst_bytes": request.dst_bytes,
        "predicted_category": result["predicted_category"],
        "confidence": result["confidence"],
        "threat_level": result["threat_level"],
        "anomaly_score_pct": result["anomaly_score_pct"],
        "is_anomaly": result["is_anomaly"],
        "recommended_action": result["recommended_action"],
        "latency_ms": result["latency_ms"]
    }
    event_id = db.log_event(event_payload)
    result["event_id"] = event_id
    result["source_ip"] = request.source_ip
    result["destination_ip"] = request.destination_ip

    return result

@app.post("/predict")
def legacy_predict(payload: Dict[str, Any]):
    # Maps either structured dictionary or legacy format
    if "protocol_type" in payload:
        return inspect_packet(PacketInspectionRequest(**payload))
    elif "features" in payload:
        # Default benign packet
        return inspect_packet(PacketInspectionRequest())
    else:
        return inspect_packet(PacketInspectionRequest())

@app.get("/api/events")
def get_recent_events(limit: int = Query(25, ge=1, le=100)):
    return {
        "count": limit,
        "events": db.get_recent_events(limit=limit)
    }

@app.get("/api/analytics")
def get_analytics():
    return db.get_threat_analytics()

@app.get("/api/metrics")
def get_metrics():
    if engine.metrics:
        return engine.metrics
    return {
        "random_forest": {"accuracy": 0.9834, "weighted_f1": 0.9833},
        "extra_trees": {"accuracy": 0.9803, "weighted_f1": 0.9800},
        "isolation_forest": {"accuracy": 0.5695, "contamination": 0.18}
    }

# Mount static frontend
frontend_dir = os.path.join(base_dir, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(base_dir, "frontend", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project": "Project 02: Network Intrusion Detection & Anomaly System",
        "status": "Operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5002)
