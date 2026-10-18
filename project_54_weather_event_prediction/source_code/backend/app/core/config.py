import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 54: AI Weather Event Nowcasting & Prediction"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./weather_nowcast.db"
    MODEL_WEIGHTS_PATH: str = os.path.join(os.path.dirname(__file__), "../../../experiments/phase2_model.pt")

    class Config:
        case_sensitive = True

settings = Settings()
