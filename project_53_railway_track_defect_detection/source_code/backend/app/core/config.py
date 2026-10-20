import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 53: Intelligent Railway Track Defect Detection"
    PROJECT_ID: str = "PROJECT-053"
    PORT: int = 5053
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = os.path.join(BASE_DIR, "data", "rail_defects.db")
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "resunet_rail_weights.pt")
    GEOMETRY_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "rail_geometry_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend", "models", "rail_scalers.json")

    class Config:
        case_sensitive = True

settings = Settings()
