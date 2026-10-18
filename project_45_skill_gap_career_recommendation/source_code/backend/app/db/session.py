import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, CareerRole, UpskillingRoadmap
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(CareerRole).count() == 0:
        roles = [
            CareerRole(role_id="ROLE-AI", role_title="AI / ML Engineer", required_competencies="Python, PyTorch, Deep Learning, MLOps, Docker, Transformers", avg_salary_usd=145000, market_growth_rate="VERY_HIGH"),
            CareerRole(role_id="ROLE-CLOUD", role_title="Cloud DevOps Architect", required_competencies="Kubernetes, AWS, Terraform, CI/CD, Docker, Linux", avg_salary_usd=150000, market_growth_rate="HIGH"),
            CareerRole(role_id="ROLE-DATA", role_title="Data Scientist", required_competencies="Python, SQL, Machine Learning, Statistics, Tableau, Pandas", avg_salary_usd=130000, market_growth_rate="HIGH"),
            CareerRole(role_id="ROLE-CYBER", role_title="Cybersecurity Analyst", required_competencies="Network Security, Ethical Hacking, SIEM, Cryptography, Linux", avg_salary_usd=125000, market_growth_rate="VERY_HIGH")
        ]
        db.add_all(roles)
        db.commit()

    if db.query(UpskillingRoadmap).count() == 0:
        db.add(UpskillingRoadmap(
            roadmap_id="RMAP-2026-01",
            user_name="Jordan Bell",
            target_role="AI / ML Engineer",
            readiness_score=78.5,
            gap_score=21.5,
            missing_skills="Transformers, MLOps",
            recommended_courses="HuggingFace NLP Specialization, DeepLearning.AI MLOps",
            recommended_projects="Deploy LLM Chatbot on Kubernetes",
            estimated_weeks_to_readiness=8,
            timestamp=datetime.utcnow() - timedelta(days=2)
        ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
