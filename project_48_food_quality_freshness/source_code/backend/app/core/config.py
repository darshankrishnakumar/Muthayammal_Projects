import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 48 | Food Quality & Freshness Detection Platform"
    PROJECT_ID: str = "PROJECT-048"
    PORT: int = 5048
    API_V1_STR: str = "/api"
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/food_freshness.db')}"
    
    CNN_MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/food_freshness_cnn_weights.pt")
    REGRESSOR_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/food_shelflife_regressor_weights.pt")
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/food_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")
    DATASET_PATH: str = os.path.join(BASE_DIR, "data/food_telemetry_6000.csv")

settings = Settings()
