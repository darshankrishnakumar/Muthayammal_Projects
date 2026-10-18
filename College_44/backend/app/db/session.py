import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, JobOpening, CandidateMatch
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
    if db.query(JobOpening).count() == 0:
        jobs = [
            JobOpening(
                job_id="JOB-AI-LEAD",
                title="Senior AI / ML Research Engineer",
                department="AI Research Labs",
                required_skills="PyTorch, Transformers, Computer Vision, Docker, FastAPI, Python",
                min_years_experience=4.0,
                description="Lead deep learning model architecture development and production deployment."
            ),
            JobOpening(
                job_id="JOB-CLOUD-DEV",
                title="Full Stack Cloud Developer",
                department="Enterprise Platform",
                required_skills="React, Node.js, TypeScript, PostgreSQL, AWS, Kubernetes",
                min_years_experience=3.0,
                description="Build scalable microservices and responsive frontends for cloud analytics."
            )
        ]
        db.add_all(jobs)
        db.commit()

    if db.query(CandidateMatch).count() == 0:
        candidates = [
            ("JOB-AI-LEAD", "Sarah Connor", 94.2, 0.95, 92.0, 96.0, "PyTorch, Transformers, Python, FastAPI", "Docker", "SHORTLISTED"),
            ("JOB-AI-LEAD", "James Wilson", 82.5, 0.84, 80.0, 85.0, "Python, Computer Vision, PyTorch", "Transformers, Docker", "REVIEW"),
            ("JOB-AI-LEAD", "Elena Rostova", 58.0, 0.60, 50.0, 65.0, "Python, SQL", "PyTorch, Transformers, FastAPI", "REJECTED"),
        ]
        for jid, name, score, sem, scov, exp, msk, miss, dec in candidates:
            db.add(CandidateMatch(
                match_id=f"MAT-2026-{random.randint(100, 999)}",
                job_id=jid,
                candidate_name=name,
                overall_match_score=score,
                semantic_similarity=sem,
                skill_coverage_pct=scov,
                experience_fit_score=exp,
                matched_skills=msk,
                missing_skills=miss,
                screening_decision=dec,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
            ))
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
