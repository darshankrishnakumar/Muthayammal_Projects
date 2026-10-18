import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project 49 | Healthcare Risk Assessment Platform"
    API_V1_STR: str = "/api"
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'data/healthcare.db')}"
    MODEL_WEIGHTS_PATH: str = os.path.join(BASE_DIR, "experiments/phase2_model.pt")

settings = Settings()
