import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 51 | Smart Energy Consumption Forecasting & Dynamic Peak Shaving"
    PROJECT_ID: str = "PROJECT-051"
    PORT: int = 5051
    API_V1_STR: str = "/api"
    # BASE_DIR points directly to source_code
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/energy.db')}"
    LSTM_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/multi_horizon_lstm_weights.pt")
    REGRESSOR_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/grid_regressor_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/energy_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")

settings = Settings()
