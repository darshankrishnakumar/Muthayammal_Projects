import os
import json
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.db.models import Base, FoodBatch, FreshnessAssessment, AuditLedger

# Ensure directory exists
db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
os.makedirs(os.path.dirname(os.path.abspath(db_file_path)), exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Enforce SQLite Write-Ahead Logging (WAL) and foreign keys
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

def compute_block_hash(block_index: int, previous_hash: str, timestamp_str: str, event_type: str, details_json: str, evidence_hash: str) -> str:
    payload = f"{block_index}:{previous_hash}:{timestamp_str}:{event_type}:{details_json}:{evidence_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def append_audit_block(db, event_type: str, details: dict, evidence_hash: str) -> AuditLedger:
    last_block = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).first()
    new_index = (last_block.block_index + 1) if last_block else 0
    prev_hash = last_block.block_hash if last_block else "0" * 64
    now = datetime.utcnow()
    details_str = json.dumps(details, sort_keys=True)
    b_hash = compute_block_hash(new_index, prev_hash, now.isoformat(), event_type, details_str, evidence_hash)
    
    block = AuditLedger(
        block_index=new_index,
        previous_hash=prev_hash,
        block_hash=b_hash,
        timestamp=now,
        event_type=event_type,
        details_json=details_str,
        evidence_hash=evidence_hash
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Seed Genesis Block #0 if ledger is empty
    if db.query(AuditLedger).count() == 0:
        genesis_time = datetime.utcnow() - timedelta(days=7)
        genesis_details = json.dumps({"description": "PROJECT-048 Food Freshness & Quality Ledger Genesis Seed", "port": 5048}, sort_keys=True)
        genesis_evidence = hashlib.sha256(b"FOOD_FRESHNESS_GENESIS_SEED_PORT_5048").hexdigest()
        genesis_hash = compute_block_hash(0, "0" * 64, genesis_time.isoformat(), "GENESIS_SEED", genesis_details, genesis_evidence)
        
        genesis_block = AuditLedger(
            block_index=0,
            previous_hash="0" * 64,
            block_hash=genesis_hash,
            timestamp=genesis_time,
            event_type="GENESIS_SEED",
            details_json=genesis_details,
            evidence_hash=genesis_evidence
        )
        db.add(genesis_block)
        db.commit()
        
    # 2. Seed Baseline Batches & Initial Assessments
    if db.query(FoodBatch).count() == 0:
        seed_batches = [
            ("FOOD-BATCH-001", "MEAT_POULTRY", "Prime Ribeye Beef Cut", "Cascadia Angus Farms", "Cold Storage Bay #1", 93.8, "STAGE_1_FRESH", 168.0, 7.0, 1.1, 0.0, 4.2, 98.5, "OPTIMAL_RETAIL_SALE", 2.8, 84.0, 24.0, 8.2, 5.65, 0.05, 74.0, 2.1, 1.55),
            ("FOOD-BATCH-002", "FRESH_PRODUCE", "Organic Baby Spinach", "Salinas Valley Hydroponics", "Hydro-Chamber #2", 64.2, "STAGE_2_MARGINAL", 48.0, 2.0, 7.8, 3.5, 34.0, 82.0, "PRIORITY_DISCOUNT_SALE", 5.2, 92.0, 96.0, 4.8, 6.20, 4.5, 86.0, 4.8, 0.95),
            ("FOOD-BATCH-003", "DAIRY", "Artisan Farm Cheddar Block", "Tillamook Valley Creamery", "Aging Cellar #3", 89.5, "STAGE_1_FRESH", 360.0, 15.0, 0.8, 0.0, 8.5, 96.0, "COLD_STORAGE_INVENTORY", 4.1, 78.0, 72.0, 3.6, 6.45, 0.02, 38.0, 2.6, 1.40),
            ("FOOD-BATCH-004", "BAKERY", "Artisan Sourdough Loaves", "Golden Hearth Artisan Bakery", "Dry Storage Ambient", 41.0, "STAGE_3_DETERIORATED", 0.0, 0.0, 18.5, 12.0, 76.0, 52.0, "DISCARD_COMPOSTING", 12.5, 68.0, 168.0, 5.2, 5.80, 0.15, 28.0, 6.5, 0.45)
        ]
        
        for b_id, cat, name, supplier, facility, score, stage, hours, days, brown, spoil, microb, cold, rec, temp, hum, dur, tvbn, ph, eth, moist, cfu, refl in seed_batches:
            batch = FoodBatch(
                batch_id=b_id,
                food_category=cat,
                product_name=name,
                supplier_origin=supplier,
                storage_facility=facility,
                freshness_score=score,
                deterioration_stage=stage,
                estimated_shelf_life_hours=hours,
                remaining_shelf_life_days=days,
                browning_index=brown,
                spoilage_area_pct=spoil,
                microbial_risk_pct=microb,
                cold_chain_compliance_score=cold,
                recommendation=rec,
                timestamp=datetime.utcnow() - timedelta(hours=int(dur / 4))
            )
            db.add(batch)
            db.commit()
            db.refresh(batch)
            
            # Create corresponding assessment
            evidence = hashlib.sha256(f"{b_id}:{name}:{score}:{stage}:{days}:{temp}:{hum}:{dur}".encode("utf-8")).hexdigest()
            assessment = FreshnessAssessment(
                sample_id=f"SAMPLE-{b_id}",
                batch_id=b_id,
                food_category=cat,
                product_name=name,
                storage_temp_c=temp,
                relative_humidity_pct=hum,
                storage_duration_hours=dur,
                browning_index=brown,
                tvbn_mg_per_100g=tvbn,
                ph_level=ph,
                ethylene_concentration_ppm=eth,
                moisture_content_pct=moist,
                bacterial_log_cfu_g=cfu,
                reflectance_ratio_650_850=refl,
                freshness_score=score,
                deterioration_stage=stage,
                estimated_shelf_life_hours=hours,
                remaining_shelf_life_days=days,
                spoilage_risk_pct=round(100.0 - score, 1),
                microbial_risk_pct=microb,
                cold_chain_compliance_score=cold,
                advisory_recommendation=rec,
                evidence_hash=evidence,
                timestamp=datetime.utcnow() - timedelta(hours=int(dur / 4))
            )
            db.add(assessment)
            db.commit()
            
            # Append audit block
            append_audit_block(
                db=db,
                event_type="BATCH_EVALUATION",
                details={
                    "batch_id": b_id,
                    "product_name": name,
                    "food_category": cat,
                    "freshness_score": score,
                    "deterioration_stage": stage,
                    "remaining_shelf_life_days": days
                },
                evidence_hash=evidence
            )
            
    db.close()

if __name__ == "__main__":
    init_db()
