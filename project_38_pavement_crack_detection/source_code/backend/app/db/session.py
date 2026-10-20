import os
import hashlib
from datetime import datetime, timezone, timedelta
import random
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.models import Base, CrackIncident, MaintenanceWorkOrder, AuditLedger

db_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_audit_entry(db: Session, action: str, details: str) -> str:
    last_entry = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    prev_hash = last_entry.record_hash if last_entry else "0" * 64

    ts = datetime.now(timezone.utc).isoformat()
    raw_str = f"{action}|{details}|{ts}|{prev_hash}"
    record_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    entry = AuditLedger(
        timestamp=ts,
        action=action,
        details=details,
        prev_hash=prev_hash,
        record_hash=record_hash
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return record_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Genesis block for audit ledger if empty
    if db.query(AuditLedger).count() == 0:
        prev_zero = "0" * 64
        ts = datetime.now(timezone.utc).isoformat()
        raw = f"GENESIS|SYSTEM_INIT|{ts}|{prev_zero}"
        g_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        g_entry = AuditLedger(
            timestamp=ts,
            action="GENESIS_INITIALIZATION",
            details="Pavement distress infrastructure database initialized in WAL mode",
            prev_hash=prev_zero,
            record_hash=g_hash
        )
        db.add(g_entry)
        db.commit()

    if db.query(CrackIncident).count() == 0:
        roads = [
            ("Interstate 80 Westbound", 120.0),
            ("State Route 17 Mile 22", 65.0),
            ("Broadway Boulevard", 45.0),
            ("El Camino Real Sector 4", 50.0),
            ("Pacific Coast Highway", 70.0),
            ("Tech Corridor Expressway", 90.0)
        ]
        types = ["ALLIGATOR", "LONGITUDINAL", "TRANSVERSE", "BLOCK", "EDGE_CRACKING", "POTHOLE_DISTRESS"]
        sevs = [
            ("LOW", 85.0, "ROUTINE_MONITOR_AND_CRACK_SEALING", 450.0, "MONITOR"),
            ("MEDIUM", 62.0, "PREVENTIVE_SURFACE_OVERLAY_OR_SLURRY_SEAL", 1850.0, "SCHEDULED"),
            ("HIGH", 38.0, "FULL_DEPTH_MILL_AND_FILL_RECONSTRUCTION", 5400.0, "URGENT")
        ]

        for i in range(15):
            road_name, _ = random.choice(roads)
            sev_lvl, pci_base, rec, cost, priority = random.choice(sevs)
            c_type = random.choice(types)
            pci = round(pci_base + random.uniform(-4.0, 4.0), 1)
            inc_id = f"CRK-2026-{100+i}"

            inc = CrackIncident(
                incident_id=inc_id,
                road_name=road_name,
                chainage_km=round(random.uniform(5.0, 85.0), 2),
                crack_type=c_type,
                severity_level=sev_lvl,
                mean_width_mm=round(random.uniform(1.5, 9.0) if sev_lvl != "LOW" else random.uniform(0.6, 2.0), 2),
                total_length_cm=round(random.uniform(20.0, 220.0), 1),
                density_percentage=round(random.uniform(3.0, 26.0), 1),
                pci_score=pci,
                recommendation=rec,
                timestamp=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 20))
            )
            db.add(inc)

            if sev_lvl in ["MEDIUM", "HIGH"]:
                order = MaintenanceWorkOrder(
                    order_id=f"WO-2026-{400+i}",
                    incident_id=inc_id,
                    road_name=road_name,
                    chainage_km=inc.chainage_km,
                    treatment_type=rec,
                    estimated_cost_usd=cost,
                    priority_tier=priority,
                    status="DISPATCHED",
                    created_at=datetime.now(timezone.utc)
                )
                db.add(order)

        db.commit()
        log_audit_entry(db, "INITIAL_DISTRESS_SEEDING", "Seeded 15 verified pavement survey calibration records")

    db.close()

if __name__ == "__main__":
    init_db()
    print("Pavement crack database initialized successfully in WAL mode.")
