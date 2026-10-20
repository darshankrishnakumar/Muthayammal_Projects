import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 44 | Intelligent Resume Screening & Job Matching System"
    API_V1_STR: str = "/api"
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/resume_matching.db')}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")
    REGRESSOR_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/candidate_competency_regressor_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/resume_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")
    DATASET_PATH: str = os.path.join(BASE_DIR, "data/resume_matching_telemetry_6000.csv")

settings = Settings()
