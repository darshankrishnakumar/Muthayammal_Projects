import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 46 | Automated Product Defect Detection Platform"
    API_V1_STR: str = "/api"
    PORT: int = 5046
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/manufacturing.db')}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")
    REGRESSOR_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/manufacturing_defect_regressor_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/manufacturing_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")
    DATASET_PATH: str = os.path.join(BASE_DIR, "data/manufacturing_telemetry_6000.csv")

settings = Settings()
