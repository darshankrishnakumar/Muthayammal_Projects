import os
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, JobOpening, CandidateMatch, AuditLedger

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
            "Project 44 AI Resume Screening & ATS Matcher microservice initialized on Port 5044 with SQLite WAL mode"
        )

    # 2. Institutional Job Openings
    if db.query(JobOpening).count() == 0:
        openings = [
            JobOpening(
                job_id="JOB-AI-LEAD",
                title="Senior AI / ML Research Engineer",
                department="AI Research Labs",
                required_skills="PyTorch, Transformers, Computer Vision, Docker, FastAPI, Python",
                min_years_experience=4.0,
                description="Lead deep learning model architecture development, transformer fine-tuning, and production deployment.",
                is_active=True
            ),
            JobOpening(
                job_id="JOB-CLOUD-DEV",
                title="Full Stack Cloud Platform Architect",
                department="Enterprise Platform",
                required_skills="React, Node.js, TypeScript, PostgreSQL, AWS, Kubernetes",
                min_years_experience=3.0,
                description="Build scalable microservices, Kubernetes manifests, and responsive frontends for cloud analytics.",
                is_active=True
            ),
            JobOpening(
                job_id="JOB-DATA-ENG",
                title="Principal Data Systems Specialist",
                department="Big Data Analytics",
                required_skills="Apache Spark, Kafka, Distributed Systems, Python, SQL, Airflow",
                min_years_experience=5.0,
                description="Architect high-throughput streaming pipelines and lakehouse analytics clusters.",
                is_active=True
            ),
            JobOpening(
                job_id="JOB-SEC-OPS",
                title="Cybersecurity DevSecOps Engineer",
                department="Cloud Security & Compliance",
                required_skills="Kubernetes, CI/CD, Rust, Linux Kernel, Terraform, Cryptography",
                min_years_experience=3.5,
                description="Enforce zero-trust architecture, automated vulnerability scanning, and cryptographic audit compliance.",
                is_active=True
            )
        ]
        db.add_all(openings)
        db.commit()
        append_audit_block(db, "OPENINGS_INITIALIZED", "Configured 4 baseline institutional job requisitions across AI, Cloud, Data, and Security")

    # 3. Baseline Screened Candidate Profiles
    if db.query(CandidateMatch).count() == 0:
        candidates = [
            ("JOB-AI-LEAD", "Dr. Sarah Connor", 96.4, 0.965, 100.0, 9.8, 97.2, "PyTorch, Transformers, Computer Vision, Python, FastAPI, Docker", "None", "SHORTLISTED"),
            ("JOB-AI-LEAD", "James Wilson", 82.5, 0.842, 83.3, 7.8, 81.4, "Python, Computer Vision, PyTorch, FastAPI, Docker", "Transformers", "SHORTLISTED"),
            ("JOB-AI-LEAD", "Elena Rostova", 71.8, 0.720, 66.7, 6.2, 70.5, "Python, PyTorch, Docker", "Transformers, FastAPI, Computer Vision", "REVIEW"),
            ("JOB-AI-LEAD", "Marcus Vance", 42.1, 0.415, 33.3, 3.5, 38.0, "Python, SQL", "PyTorch, Transformers, FastAPI, Docker, Computer Vision", "REJECTED"),
            ("JOB-CLOUD-DEV", "Aria Stark", 94.8, 0.940, 100.0, 9.5, 95.0, "React, Node.js, TypeScript, PostgreSQL, AWS, Kubernetes", "None", "SHORTLISTED"),
            ("JOB-CLOUD-DEV", "David Miller", 76.4, 0.765, 83.3, 7.2, 75.8, "React, Node.js, TypeScript, PostgreSQL, AWS", "Kubernetes", "REVIEW"),
            ("JOB-DATA-ENG", "Priya Sharma", 93.2, 0.928, 100.0, 9.2, 94.1, "Apache Spark, Kafka, Distributed Systems, Python, SQL, Airflow", "None", "SHORTLISTED"),
            ("JOB-SEC-OPS", "Alex Thorne", 89.6, 0.892, 83.3, 8.8, 88.5, "Kubernetes, CI/CD, Linux Kernel, Terraform, Cryptography", "Rust", "SHORTLISTED")
        ]
        for i, (jid, name, score, sem, scov, exp, sen, msk, miss, dec) in enumerate(candidates):
            ev_hash = hashlib.sha256(f"{name}|{jid}|{score}|{sem}|{scov}|{exp}|{dec}".encode("utf-8")).hexdigest()
            db.add(CandidateMatch(
                match_id=f"MAT-2026-{100 + i}",
                job_id=jid,
                candidate_name=name,
                overall_match_score=score,
                semantic_similarity=sem,
                skill_coverage_pct=scov,
                experience_fit_score=exp,
                seniority_compatibility=sen,
                matched_skills=msk,
                missing_skills=miss,
                screening_decision=dec,
                evidence_hash=ev_hash,
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 36))
            ))
        db.commit()
        append_audit_block(db, "BASELINE_SCREENING_SEEDED", "Seeded 8 cryptographically verified candidate match records across shortlisting tiers")

    db.close()

if __name__ == "__main__":
    init_db()
