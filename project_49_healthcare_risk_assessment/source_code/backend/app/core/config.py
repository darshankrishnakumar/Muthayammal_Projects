import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 49 | Healthcare Risk Assessment Platform"
    PROJECT_ID: str = "PROJECT-049"
    PORT: int = 5049
    API_V1_STR: str = "/api"
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/healthcare.db')}"
    
    RISK_MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/healthcare_risk_net_weights.pt")
    COMORBIDITY_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "backend/models/comorbidity_regressor_weights.pt")
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")
    SCALERS_PATH: str = os.path.join(BASE_DIR, "backend/models/healthcare_scalers.json")
    METADATA_PATH: str = os.path.join(BASE_DIR, "backend/models/model_metadata.json")
    DATASET_PATH: str = os.path.join(BASE_DIR, "data/patient_telemetry_6000.csv")

settings = Settings()
