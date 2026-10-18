import os
import sys
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Ensure source_code is on path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.inference_engine import AirfareInferenceEngine
from database.database import init_db, log_prediction, get_recent_predictions, get_analytics

# Initialize Database
init_db()

# Initialize ML Engine
inference_engine = AirfareInferenceEngine()

app = FastAPI(
    title="Project 01: Airfare Price Prediction Using LSTM Machine Learning Techniques",
    description="Production Machine Learning & Deep Learning Inference System for Airline Ticket Pricing",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

class FlightPredictionRequest(BaseModel):
    airline: str = Field(..., example="IndiGo")
    source: str = Field(..., example="Banglore")
    destination: str = Field(..., example="Delhi")
    journey_date: str = Field(..., example="2026-11-20")
    dep_time: str = Field(..., example="10:00")
    arrival_time: str = Field(..., example="12:45")
    total_stops: int = Field(0, ge=0, le=4, example=0)

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Airfare Price Prediction API",
        "timestamp": time.time(),
        "lstm_model_loaded": inference_engine.lstm_model is not None,
        "rf_model_loaded": inference_engine.rf_model is not None
    }

@app.post("/api/predict")
def predict_flight(request: FlightPredictionRequest):
    start_time = time.time()
    try:
        prediction = inference_engine.predict_flight_fare(
            airline=request.airline,
            source=request.source,
            destination=request.destination,
            journey_date=request.journey_date,
            dep_time=request.dep_time,
            arrival_time=request.arrival_time,
            total_stops=request.total_stops
        )
        
        # Log to SQLite
        record_id = log_prediction(
            airline=request.airline,
            source=request.source,
            destination=request.destination,
            journey_date=request.journey_date,
            dep_time=request.dep_time,
            arrival_time=request.arrival_time,
            duration_mins=prediction['duration_mins'],
            total_stops=request.total_stops,
            predicted_price_lstm=prediction['predicted_price_lstm'],
            predicted_price_rf=prediction['predicted_price_rf'],
            recommended_fare=prediction['recommended_fare'],
            confidence_score=0.92
        )
        
        latency_ms = (time.time() - start_time) * 1000
        prediction['record_id'] = record_id
        prediction['latency_ms'] = round(latency_ms, 2)
        prediction['route'] = f"{request.source} → {request.destination}"
        return prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/history")
def get_history(limit: int = 15):
    return get_recent_predictions(limit=limit)

@app.get("/api/analytics")
def get_analytics_endpoint():
    return get_analytics()

@app.get("/api/metrics")
def get_metrics_endpoint():
    return inference_engine.metrics

@app.get("/api/options")
def get_options():
    return {
        "airlines": [
            "IndiGo", "Air India", "Jet Airways", "SpiceJet",
            "Multiple carriers", "Vistara", "Air Asia", "GoAir"
        ],
        "sources": ["Banglore", "Chennai", "Delhi", "Kolkata", "Mumbai"],
        "destinations": ["Banglore", "Cochin", "Delhi", "Hyderabad", "Kolkata"],
        "stops": [
            {"label": "Non-Stop (Direct)", "value": 0},
            {"label": "1 Stop", "value": 1},
            {"label": "2 Stops", "value": 2},
            {"label": "3 Stops", "value": 3}
        ]
    }

# Serve Frontend
@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=False)
