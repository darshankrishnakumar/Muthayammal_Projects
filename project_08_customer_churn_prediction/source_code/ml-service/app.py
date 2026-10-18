import json
import logging
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("churn-ml-service")

app = FastAPI(
    title="Customer Churn ML Service",
    description="Random Forest ML Inference Service for Telecom Customer Churn",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "churn_pipeline.joblib")
METRICS_PATH = os.path.join(BASE_DIR, "models", "metrics.json")

model_pipeline = None
model_metrics = {}


def load_artifacts():
    global model_pipeline, model_metrics
    if os.path.exists(MODEL_PATH):
        try:
            model_pipeline = joblib.load(MODEL_PATH)
            logger.info("Successfully loaded Random Forest pipeline from %s", MODEL_PATH)
        except Exception as e:
            logger.error("Error loading model pipeline: %s", e)
    else:
        logger.warning("Model file not found at %s. Please run train_model.py first.", MODEL_PATH)

    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                model_metrics = json.load(f)
            logger.info("Loaded model metrics successfully.")
        except Exception as e:
            logger.error("Error loading model metrics: %s", e)


@app.on_event("startup")
def startup_event():
    load_artifacts()


# Also load immediately on import
load_artifacts()


from pydantic import BaseModel, Field, model_validator

class CustomerFeatures(BaseModel):
    gender: str = Field("Male")
    seniorCitizen: int = Field(0)
    partner: str = Field("No")
    dependents: str = Field("No")
    tenure: int = Field(1)
    phoneService: str = Field("Yes")
    multipleLines: str = Field("No")
    internetService: str = Field("Fiber optic")
    onlineSecurity: str = Field("No")
    onlineBackup: str = Field("No")
    deviceProtection: str = Field("No")
    techSupport: str = Field("No")
    streamingTV: str = Field("No")
    streamingMovies: str = Field("No")
    contract: str = Field("Month-to-month")
    paperlessBilling: str = Field("Yes")
    paymentMethod: str = Field("Electronic check")
    monthlyCharges: float = Field(70.0)
    totalCharges: Optional[float] = Field(None)

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key_map = {
                "gender": ["gender", "Gender"],
                "seniorCitizen": ["seniorCitizen", "SeniorCitizen", "seniorcitizen"],
                "partner": ["partner", "Partner"],
                "dependents": ["dependents", "Dependents"],
                "tenure": ["tenure", "tenureMonths", "Tenure", "TenureMonths"],
                "phoneService": ["phoneService", "PhoneService", "phoneservice"],
                "multipleLines": ["multipleLines", "MultipleLines", "multiplelines"],
                "internetService": ["internetService", "InternetService", "internetservice"],
                "onlineSecurity": ["onlineSecurity", "OnlineSecurity", "onlinesecurity"],
                "onlineBackup": ["onlineBackup", "OnlineBackup", "onlinebackup"],
                "deviceProtection": ["deviceProtection", "DeviceProtection", "deviceprotection"],
                "techSupport": ["techSupport", "TechSupport", "techsupport"],
                "streamingTV": ["streamingTV", "StreamingTV", "streamingtv", "streamingTv"],
                "streamingMovies": ["streamingMovies", "StreamingMovies", "streamingmovies"],
                "contract": ["contract", "Contract"],
                "paperlessBilling": ["paperlessBilling", "PaperlessBilling", "paperlessbilling"],
                "paymentMethod": ["paymentMethod", "PaymentMethod", "paymentmethod"],
                "monthlyCharges": ["monthlyCharges", "MonthlyCharges", "monthlycharges"],
                "totalCharges": ["totalCharges", "TotalCharges", "totalcharges"],
            }
            res = {}
            for canonical, variants in key_map.items():
                for var in variants:
                    if var in data and data[var] is not None:
                        res[canonical] = data[var]
                        break
            for k, v in data.items():
                if k not in res:
                    res[k] = v
            return res
        return data

    class Config:
        populate_by_name = True
        extra = "allow"


class PredictionResponse(BaseModel):
    prediction: str
    churnProbability: float
    model: str
    riskLevel: str
    featuresReceived: Dict[str, Any]


@app.get("/health")
def health_check():
    is_loaded = model_pipeline is not None
    return {
        "status": "UP" if is_loaded else "DEGRADED",
        "service": "Customer Churn Python ML Service",
        "modelLoaded": is_loaded,
        "model": "Random Forest Classifier",
        "version": "1.0.0",
    }


@app.get("/metrics")
def get_metrics():
    if not model_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics not found. Run training script first.",
        )
    return model_metrics


@app.post("/predict", response_model=PredictionResponse)
def predict_churn(customer: CustomerFeatures):
    global model_pipeline
    if model_pipeline is None:
        load_artifacts()
        if model_pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model is not available or failed to load.",
            )

    try:
        # Compute totalCharges if absent or 0
        total_charges = customer.totalCharges
        if total_charges is None or total_charges == 0.0:
            total_charges = float(customer.monthlyCharges * max(1, customer.tenure))

        # Format input row for Scikit-learn Pipeline
        input_data = {
            "tenure": [customer.tenure],
            "MonthlyCharges": [float(customer.monthlyCharges)],
            "TotalCharges": [float(total_charges)],
            "gender": [str(customer.gender)],
            "SeniorCitizen": [int(customer.seniorCitizen)],
            "Partner": [str(customer.partner)],
            "Dependents": [str(customer.dependents)],
            "PhoneService": [str(customer.phoneService)],
            "MultipleLines": [str(customer.multipleLines)],
            "InternetService": [str(customer.internetService)],
            "OnlineSecurity": [str(customer.onlineSecurity)],
            "OnlineBackup": [str(customer.onlineBackup)],
            "DeviceProtection": [str(customer.deviceProtection)],
            "TechSupport": [str(customer.techSupport)],
            "StreamingTV": [str(customer.streamingTV)],
            "StreamingMovies": [str(customer.streamingMovies)],
            "Contract": [str(customer.contract)],
            "PaperlessBilling": [str(customer.paperlessBilling)],
            "PaymentMethod": [str(customer.paymentMethod)],
        }

        df_input = pd.DataFrame(input_data)

        # Generate genuine prediction and probabilities
        pred_class = int(model_pipeline.predict(df_input)[0])
        pred_proba = model_pipeline.predict_proba(df_input)[0]

        churn_proba = float(pred_proba[1])
        prediction_label = "Churn" if pred_class == 1 else "No Churn"

        # Explicit risk category thresholds
        if churn_proba >= 0.65:
            risk_level = "High"
        elif churn_proba >= 0.35:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return PredictionResponse(
            prediction=prediction_label,
            churnProbability=round(churn_proba, 4),
            model="Random Forest",
            riskLevel=risk_level,
            featuresReceived={
                "gender": customer.gender,
                "tenure": customer.tenure,
                "monthlyCharges": customer.monthlyCharges,
                "contract": customer.contract,
                "internetService": customer.internetService,
                "paymentMethod": customer.paymentMethod,
            },
        )
    except Exception as e:
        logger.error("Prediction failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction computation failed due to internal error.",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
