"""
FastAPI ML Service for Child Gait Prediction.
Exposes /health and /predict endpoints.
"""

import os
import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

# Ensure src modules are resolvable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.predict import GaitPredictor

app = FastAPI(
    title="Child Gait Prediction ML API",
    description="College-level Machine Learning service predicting pediatric gait patterns.",
    version="1.0.0",
)

# Enable CORS for the React/TanStack frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = GaitPredictor()

MEDICAL_DISCLAIMER = (
    "This application is a college-level machine learning prototype intended for "
    "educational and decision-support purposes. It does not replace professional "
    "medical diagnosis, clinical assessment, or treatment."
)


class GaitPredictionRequest(BaseModel):
    # Support both snake_case and camelCase
    child_id: Optional[str] = Field(default=None, alias="childId")
    age: Optional[float] = None
    gender: Optional[str] = None
    heel_pressure: float = Field(..., alias="heelPressure", description="Heel pressure in kPa")
    toe_pressure: float = Field(..., alias="toePressure", description="Toe pressure in kPa")
    tilt_angle: float = Field(..., alias="tiltAngle", description="Foot tilt angle in degrees")
    step_duration: float = Field(..., alias="stepDuration", description="Step duration in seconds")
    stride_length: float = Field(..., alias="strideLength", description="Stride length in cm")
    walking_speed: float = Field(..., alias="walkingSpeed", description="Walking speed in m/s")

    @model_validator(mode="before")
    @classmethod
    def populate_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Normalize keys to snake_case if passed as camelCase
            mapping = {
                "heelPressure": "heel_pressure",
                "toePressure": "toe_pressure",
                "tiltAngle": "tilt_angle",
                "stepDuration": "step_duration",
                "strideLength": "stride_length",
                "walkingSpeed": "walking_speed",
                "childId": "child_id",
            }
            for camel, snake in mapping.items():
                if camel in values and snake not in values:
                    values[snake] = values[camel]
                elif snake in values and camel not in values:
                    values[camel] = values[snake]
        return values


class GaitPredictionResponse(BaseModel):
    prediction: str
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    disclaimer: str = MEDICAL_DISCLAIMER


@app.get("/")
def root():
    return {
        "service": "Child Gait Prediction ML API",
        "status": "online",
        "model_loaded": predictor.is_ready,
        "disclaimer": MEDICAL_DISCLAIMER,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": predictor.is_ready,
    }


@app.post("/predict", response_model=GaitPredictionResponse)
def predict_gait(req: GaitPredictionRequest):
    if not predictor.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Model has not been trained yet. Please provide the real dataset "
                "and execute the training pipeline before requesting predictions."
            ),
        )

    # Convert request to dictionary
    input_dict = {
        "heel_pressure": req.heel_pressure,
        "toe_pressure": req.toe_pressure,
        "tilt_angle": req.tilt_angle,
        "step_duration": req.step_duration,
        "stride_length": req.stride_length,
        "walking_speed": req.walking_speed,
    }

    try:
        res = predictor.predict(input_dict)
        return GaitPredictionResponse(
            prediction=res["prediction"],
            confidence=res.get("confidence"),
            probabilities=res.get("probabilities"),
            disclaimer=MEDICAL_DISCLAIMER,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
