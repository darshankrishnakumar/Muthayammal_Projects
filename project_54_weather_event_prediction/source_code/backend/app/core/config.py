import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 54: AI Weather Event Nowcasting & Prediction"
    PROJECT_ID: str = "PROJECT-054"
    PORT: int = 5054
    API_V1_STR: str = "/api"

    DATABASE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/weather_nowcast.db"))
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

    MODEL_BIGRU_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/bigru_weather_weights.pt"))
    MODEL_RADAR_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/radar_precip_weights.pt"))
    METADATA_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/model_metadata.json"))
    SCALERS_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/weather_scalers.json"))

    class Config:
        case_sensitive = True

settings = Settings()
