import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 52: AI Crowd Density Estimation & Anomaly Detection"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./crowd_analytics.db"
    MODEL_WEIGHTS_PATH: str = os.path.join(os.path.dirname(__file__), "../../../experiments/phase2_model.pt")
    ALERT_RISK_THRESHOLD: float = 0.70

    class Config:
        case_sensitive = True

settings = Settings()
