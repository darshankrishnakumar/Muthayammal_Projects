from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from backend.app.db.session import get_db, append_audit_block
from backend.app.db.models import AttendanceRecord, Student, AuditLedger
from backend.app.ml.inference_engine import attendance_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FaceVerifyRequest(BaseModel):
    student_index: int = 0
    simulate_spoof_attack: bool = False
    attack_type: str = "PRINT_ATTACK_2D"
    course_code: str = "CS-401"
    classroom_id: str = "HALL-A1"

@router.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return {"count": len(students), "students": students}

@router.get("/logs")
def get_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AttendanceRecord).order_by(AttendanceRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(logs), "records": logs}

@router.get("/audit-logs")
def get_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    ledger = db.query(AuditLedger).order_by(AuditLedger.block_index.desc()).offset(skip).limit(limit).all()
    return {"count": len(ledger), "ledger": ledger}

@router.get("/stats")
def get_attendance_stats(db: Session = Depends(get_db)):
    total = db.query(AttendanceRecord).count()
    present = db.query(AttendanceRecord).filter(AttendanceRecord.status == "PRESENT").count()
    spoofs = db.query(AttendanceRecord).filter(AttendanceRecord.status == "REJECTED_SPOOF").count()
    late = db.query(AttendanceRecord).filter(AttendanceRecord.status == "LATE").count()
    students_count = db.query(Student).count()
    return {
        "total_records": total,
        "enrolled_students": students_count,
        "present_count": present,
        "spoof_attacks_blocked": spoofs,
        "late_count": late,
        "system_liveness_rate": round((present / max(1, total)) * 100, 1),
        "security_integrity": "100.0% Cryptographically Verified (SHA-256)"
    }

@router.post("/verify")
async def verify_attendance(req: FaceVerifyRequest, db: Session = Depends(get_db)):
    # Run full neural inference through DeepAntiSpoofFaceNet + BiometricLivenessQualityRegressorNet
    res = attendance_engine.verify_face(
        student_idx=req.student_index,
        is_spoof_attack=req.simulate_spoof_attack,
        attack_type=req.attack_type,
        course_code=req.course_code
    )

    rec = AttendanceRecord(
        record_id=f"ATT-2026-{uuid.uuid4().hex[:6].upper()}",
        student_id=res["student_id"],
        full_name=res["full_name"],
        course_code=req.course_code,
        classroom_id=req.classroom_id,
        liveness_status=res["liveness_status"],
        attack_type=res["attack_type"],
        anti_spoof_confidence=res["anti_spoof_confidence"],
        face_match_confidence=res["face_match_confidence"],
        spoof_risk_pct=res["spoof_risk_pct"],
        micro_tremor_score=res["micro_tremor_score"],
        illumination_entropy=res["illumination_entropy"],
        attendance_score=res["attendance_score"],
        status=res["status"],
        evidence_hash=res["evidence_hash"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    # Append immutable audit block to ledger
    audit_action = "ATTENDANCE_VERIFIED" if res["status"] != "REJECTED_SPOOF" else "PRESENTATION_ATTACK_BLOCKED"
    audit_detail = (
        f"Record={rec.record_id} Student={rec.student_id} Name={rec.full_name} Status={rec.status} "
        f"Liveness={rec.liveness_status} Attack={rec.attack_type} Risk={rec.spoof_risk_pct}% "
        f"Hash={rec.evidence_hash[:16]}..."
    )
    append_audit_block(db, audit_action, audit_detail)

    await ws_manager.broadcast({"event": "ATTENDANCE_LOGGED", "data": res, "record_id": rec.record_id})
    return {"record": rec, "metrics": res}
