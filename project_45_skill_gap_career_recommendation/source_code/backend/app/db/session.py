import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, CareerRole, UpskillingRoadmap, AuditLedger

db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def compute_block_hash(action: str, details: str, timestamp: str, prev_hash: str) -> str:
    payload = f"{action}|{details}|{timestamp}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db: Session, action_type: str, details: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    ts = datetime.utcnow().isoformat() + "Z"
    if last_block is None:
        idx = 0
        prev_hash = "0" * 64
    else:
        idx = last_block.block_index + 1
        prev_hash = last_block.current_hash
    cur_hash = compute_block_hash(action_type, details, ts, prev_hash)
    entry = AuditLedger(
        block_index=idx,
        timestamp=ts,
        action_type=action_type,
        details=details,
        previous_hash=prev_hash,
        current_hash=cur_hash
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Genesis audit block
    if db.query(AuditLedger).count() == 0:
        append_audit_block(
            db,
            "SYSTEM_INIT",
            "Project 45 AI Skill-Gap Analysis & Career Path Recommendation Platform initialized on Port 5045 with SQLite WAL mode"
        )

    # 2. Institutional Career Roles
    if db.query(CareerRole).count() == 0:
        roles = [
            CareerRole(
                role_id="ROLE-AI",
                role_title="AI / ML Research & Platform Engineer",
                required_competencies="Python, PyTorch, Deep Learning, MLOps, Docker, Transformers, Kubernetes",
                avg_salary_usd=145000,
                market_growth_rate="VERY_HIGH",
                is_active=True
            ),
            CareerRole(
                role_id="ROLE-CLOUD",
                role_title="Cloud DevOps & Platform Architect",
                required_competencies="Kubernetes, AWS, Terraform, CI/CD, Docker, Linux, Go",
                avg_salary_usd=150000,
                market_growth_rate="HIGH",
                is_active=True
            ),
            CareerRole(
                role_id="ROLE-DATA",
                role_title="Principal Data Scientist & ML Specialist",
                required_competencies="Python, SQL, Machine Learning, Statistics, Tableau, Pandas, Spark",
                avg_salary_usd=130000,
                market_growth_rate="HIGH",
                is_active=True
            ),
            CareerRole(
                role_id="ROLE-CYBER",
                role_title="Cybersecurity DevSecOps & Threat Analyst",
                required_competencies="Network Security, Ethical Hacking, SIEM, Cryptography, Linux, Rust, Zero Trust",
                avg_salary_usd=125000,
                market_growth_rate="VERY_HIGH",
                is_active=True
            )
        ]
        db.add_all(roles)
        db.commit()
        append_audit_block(db, "CAREER_ROLES_INITIALIZED", "Configured 4 institutional target career paths across AI, Cloud, Data, and Cybersecurity")

    # 3. Seeded Verified Upskilling Roadmaps
    if db.query(UpskillingRoadmap).count() == 0:
        seed_roadmaps = [
            ("Jordan Bell", "AI / ML Research & Platform Engineer", 85.7, 14.3, "Transformers", "DeepLearning.AI HuggingFace Specialization", "Fine-Tuning LLaMA-3 for Domain Question Answering", 6, 42.5),
            ("Alex Thorne", "Cloud DevOps & Platform Architect", 71.4, 28.6, "Terraform, Go", "HashiCorp Certified Terraform Associate, Go Microservices", "Infrastructure as Code AWS Multi-AZ Deployment", 10, 55.0),
            ("Sam Chen", "Principal Data Scientist & ML Specialist", 85.7, 14.3, "Spark", "Distributed Computing with Apache Spark", "Real-Time Streaming Feature Store", 6, 38.0),
            ("Riley Vance", "Cybersecurity DevSecOps & Threat Analyst", 57.1, 42.9, "Ethical Hacking, Rust, Zero Trust", "CompTIA Security+ / CEH Bootcamp", "Automated Penetration Testing Framework", 14, 68.0),
            ("Taylor Kim", "AI / ML Research & Platform Engineer", 100.0, 0.0, "None", "Advanced Research Fellowships", "Architectural Scaling of Mixture-of-Experts", 4, 15.0),
            ("Casey Miller", "Cloud DevOps & Platform Architect", 85.7, 14.3, "Kubernetes", "Certified Kubernetes Administrator (CKA)", "Multi-Region Service Mesh Deployment", 6, 48.0),
            ("Morgan Patel", "Principal Data Scientist & ML Specialist", 57.1, 42.9, "Machine Learning, Statistics, Spark", "Stanford Statistical Learning, Coursera ML Specialization", "Customer Churn Predictive Pipeline", 12, 62.0),
            ("Elena Rostova", "Cybersecurity DevSecOps & Threat Analyst", 71.4, 28.6, "SIEM, Cryptography", "Enterprise SIEM Incident Response, Cryptographic Protocols", "Hardware Security Module Key Management", 8, 52.0)
        ]
        for i, (name, role, read, gap, miss, crs, prj, wks, sal) in enumerate(seed_roadmaps):
            ev_hash = hashlib.sha256(f"{name}|{role}|{read}|{gap}|{miss}|{wks}".encode("utf-8")).hexdigest()
            db.add(UpskillingRoadmap(
                roadmap_id=f"RMAP-2026-{100 + i}",
                user_name=name,
                target_role=role,
                readiness_score=read,
                gap_score=gap,
                missing_skills=miss,
                recommended_courses=crs,
                recommended_projects=prj,
                estimated_weeks_to_readiness=wks,
                salary_growth_potential=sal,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
            ))
        db.commit()
        append_audit_block(db, "BASELINE_ROADMAPS_SEEDED", "Seeded 8 cryptographically anchored career trajectory roadmaps across competency readiness tiers")

    db.close()

if __name__ == "__main__":
    init_db()
