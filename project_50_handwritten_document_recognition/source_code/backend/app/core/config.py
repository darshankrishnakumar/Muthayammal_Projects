import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 50 | Intelligent Handwritten Document Processing Platform"
    PROJECT_ID: str = "PROJECT-050"
    PORT: int = 5050
    API_V1_STR: str = "/api"
    # BASE_DIR points directly to source_code
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/idp.db')}"
    CRNN_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/crnn_htr_model_weights.pt")
    SCORER_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/quality_scorer_weights.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/idp_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")

settings = Settings()
