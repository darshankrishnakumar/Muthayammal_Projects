from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)
    full_name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False)
    year = Column(Integer, default=3)
    face_enrolled = Column(Boolean, default=True)
    rfid_tag = Column(String(32), default="RFID-8821")
    registered_photo = Column(String(200), default="avatar.jpg")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(50), unique=True, index=True)
    student_id = Column(String(50), index=True)
    full_name = Column(String(100))
    course_code = Column(String(30), default="CS-401")
    classroom_id = Column(String(30), default="HALL-A1")
    liveness_status = Column(String(30))  # REAL, SPOOF_DETECTED
    attack_type = Column(String(50), default="NONE") # NONE, PRINT_ATTACK_2D, SCREEN_REPLAY_ATTACK, SILICONE_3D_MASK
    anti_spoof_confidence = Column(Float)
    face_match_confidence = Column(Float)
    spoof_risk_pct = Column(Float, nullable=True)
    micro_tremor_score = Column(Float, nullable=True)
    illumination_entropy = Column(Float, nullable=True)
    attendance_score = Column(Float, nullable=True)
    status = Column(String(30), default="PRESENT") # PRESENT, REJECTED_SPOOF, LATE
    evidence_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    action_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
