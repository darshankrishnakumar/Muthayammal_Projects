import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 47 | Classroom Engagement Analytics Platform"
    API_V1_STR: str = "/api"
    PORT: int = 5047
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/classroom.db')}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")
    REGRESSOR_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/classroom_attention_regressor_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/classroom_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")
    DATASET_PATH: str = os.path.join(BASE_DIR, "data/classroom_telemetry_6000.csv")

settings = Settings()
