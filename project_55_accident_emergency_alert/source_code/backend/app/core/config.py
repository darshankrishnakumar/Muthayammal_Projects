"""
Enterprise Configuration Settings for Project 55.
Uses Pydantic BaseSettings for environment variable management and validation.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 55: AI-Based Accident Detection and Emergency Alert System"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    PORT: int = 5055

    # Base Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    # Database
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')), 'data/project55_enterprise.db')}"
    )

    # ML Inference Settings
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.65
    EVIDENCE_OUTPUT_DIR: str = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')), "data/processed/evidence_snapshots")
    SAMPLE_VIDEOS_DIR: str = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')), "data/sample_videos")
    MODEL_WEIGHTS_PATH: str = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')), "backend/models/temporal_fusion_weights.pt")
    BASELINE_WEIGHTS_PATH: str = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')), "backend/models/crash_severity_weights.pt")

    # Emergency Dispatch
    AUTO_DISPATCH_ENABLED: bool = True
    EMERGENCY_WEBHOOK_URL: str = "https://mock-cad-dispatch.traffic.gov/alerts"

    class Config:
        case_sensitive = True


settings = Settings()
