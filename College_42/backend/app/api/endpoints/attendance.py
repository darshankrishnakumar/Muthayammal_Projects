from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import numpy as np
import uuid
from backend.app.db.session import get_db
from backend.app.db.models import AttendanceRecord, Student
from backend.app.ml.inference_engine import attendance_engine
from backend.app.core.websocket_manager import ws_manager

router = APIRouter()

class FaceVerifyRequest(BaseModel):
    student_index: int = 0
    simulate_spoof_attack: bool = False
    course_code: str = "CS-401"

@router.get("/logs")
def get_logs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    logs = db.query(AttendanceRecord).order_by(AttendanceRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return {"count": len(logs), "records": logs}

@router.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return {"count": len(students), "students": students}

@router.post("/verify")
async def verify_attendance(req: FaceVerifyRequest, db: Session = Depends(get_db)):
    mock_face = np.random.uniform(0.3, 0.8, (3, 64, 64)).astype(np.float32)
    res = attendance_engine.verify_face(mock_face, req.student_index, req.simulate_spoof_attack)

    rec = AttendanceRecord(
        record_id=f"ATT-2026-{uuid.uuid4().hex[:6].upper()}",
        student_id=res["student_id"],
        full_name=res["full_name"],
        course_code=req.course_code,
        liveness_status=res["liveness_status"],
        anti_spoof_confidence=res["anti_spoof_confidence"],
        face_match_confidence=res["face_match_confidence"],
        status=res["status"]
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    await ws_manager.broadcast({"event": "ATTENDANCE_LOGGED", "data": res})
    return {"record": rec, "metrics": res}
