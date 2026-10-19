"""
Pydantic schemas for backend API data validation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator


class GaitRecordCreate(BaseModel):
    child_id: str = Field(..., alias="childId", min_length=1, description="Child identifier")
    age: int = Field(..., ge=1, le=18, description="Child age in years")
    gender: str = Field(..., description="Child gender (e.g. Male/Female)")
    heel_pressure: float = Field(..., alias="heelPressure", gt=0, description="Heel pressure in kPa")
    toe_pressure: float = Field(..., alias="toePressure", gt=0, description="Toe pressure in kPa")
    tilt_angle: float = Field(..., alias="tiltAngle", ge=0, le=90, description="Foot tilt angle in degrees")
    step_duration: float = Field(..., alias="stepDuration", gt=0, le=5, description="Step duration in seconds")
    stride_length: float = Field(..., alias="strideLength", gt=0, le=250, description="Stride length in cm")
    walking_speed: float = Field(..., alias="walkingSpeed", gt=0, le=5, description="Walking speed in m/s")
    gait_class: Optional[str] = Field(default=None, alias="prediction", description="Classification label")
    confidence: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, values: Any) -> Any:
        if isinstance(values, dict):
            mapping = {
                "childId": "child_id",
                "heelPressure": "heel_pressure",
                "toePressure": "toe_pressure",
                "tiltAngle": "tilt_angle",
                "stepDuration": "step_duration",
                "strideLength": "stride_length",
                "walkingSpeed": "walking_speed",
                "prediction": "gait_class",
            }
            for camel, snake in mapping.items():
                if camel in values and snake not in values:
                    values[snake] = values[camel]
                elif snake in values and camel not in values:
                    values[camel] = values[snake]
        return values


class GaitRecordResponse(BaseModel):
    id: str
    child_id: str
    childId: str
    age: int
    gender: str
    heel_pressure: float
    heelPressure: float
    toe_pressure: float
    toePressure: float
    tilt_angle: float
    tiltAngle: float
    step_duration: float
    stepDuration: float
    stride_length: float
    strideLength: float
    walking_speed: float
    walkingSpeed: float
    gait_class: str
    prediction: str
    confidence: Optional[float] = None
    created_at: str
    date: str


class PredictionResultResponse(BaseModel):
    prediction: str
    confidence: Optional[float] = None
    assessmentId: str
    recommendations: Optional[List[str]] = Field(default_factory=list)
    record: Dict[str, Any]
    disclaimer: str = (
        "This application is a college-level machine learning prototype intended for "
        "educational and decision-support purposes. It does not replace professional "
        "medical diagnosis, clinical assessment, or treatment."
    )


class CSVImportResponse(BaseModel):
    status: str
    imported_count: int
    errors: List[str]
    dataset_file: str
