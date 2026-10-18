import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 53: Intelligent Railway Track Defect Detection"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./rail_defects.db"
    MODEL_WEIGHTS_PATH: str = os.path.join(os.path.dirname(__file__), "../../../experiments/phase2_model.pt")

    class Config:
        case_sensitive = True

settings = Settings()
