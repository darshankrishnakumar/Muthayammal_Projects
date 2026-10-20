import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 52: AI Crowd Density Estimation & Anomaly Detection"
    PROJECT_ID: str = "PROJECT-052"
    PORT: int = 5052
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = os.path.join(BASE_DIR, "data", "crowd_analytics.db")
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "csrnet_crowd_weights.pt")
    RISK_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "crowd_risk_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "crowd_scalers.json")
    ALERT_RISK_THRESHOLD: float = 0.70

    class Config:
        case_sensitive = True

settings = Settings()
