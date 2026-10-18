from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)
    full_name = Column(String(100))
    department = Column(String(50))
    year = Column(Integer, default=3)
    registered_photo = Column(String(200), default="avatar.jpg")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(50), unique=True, index=True)
    student_id = Column(String(50), index=True)
    full_name = Column(String(100))
    course_code = Column(String(30), default="CS-401")
    liveness_status = Column(String(20)) # REAL, SPOOF_DETECTED
    anti_spoof_confidence = Column(Float)
    face_match_confidence = Column(Float)
    status = Column(String(20), default="PRESENT") # PRESENT, REJECTED_SPOOF, LATE
    timestamp = Column(DateTime, default=datetime.utcnow)
