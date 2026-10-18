"""
SQLAlchemy Relational Database Models for Project 55.
Persists Cameras, Detected Incidents, Dispatch Alerts, and Operator Audit Logs.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    roadway = Column(String(128), default="Highway 101 Corridor")
    latitude = Column(Float, nullable=False, default=37.7749)
    longitude = Column(Float, nullable=False, default=-122.4194)
    zone = Column(String(64), default="Lane 2 (Northbound)")
    status = Column(String(32), default="ONLINE")  # ONLINE, OFFLINE, MAINTENANCE
    stream_url = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    incidents = relationship("Incident", back_populates="camera")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_uuid = Column(String(64), unique=True, index=True, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)

    # Accident Classification & Severity
    confidence = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)  # Minor, Moderate, Severe, Critical
    priority = Column(String(32), nullable=False)  # P1-Critical, P2-High, P3-Medium, P4-Low
    status = Column(String(32), default="New", index=True)  # New, Acknowledged, Dispatched, False Alarm, Resolved

    # Physical Evidence & Visual Artifacts
    vehicles_involved = Column(Integer, default=1)
    rollover_detected = Column(Boolean, default=False)
    rationale = Column(Text, nullable=True)
    multi_cues = Column(JSON, nullable=True)
    snapshot_path = Column(String(256), nullable=True)
    video_clip_path = Column(String(256), nullable=True)

    camera = relationship("Camera", back_populates="incidents")
    dispatches = relationship("DispatchAlert", back_populates="incident", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="incident", cascade="all, delete-orphan")


class DispatchAlert(Base):
    __tablename__ = "dispatch_alerts"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    dispatch_uuid = Column(String(64), unique=True, nullable=False)
    channel = Column(String(64), nullable=False)  # CAD_SYSTEM, POLICE_WEBHOOK, EMS_DISPATCH, SMS
    status = Column(String(32), default="DELIVERED")
    recipient = Column(String(128), nullable=True)
    dispatched_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    response_code = Column(Integer, default=200)
    payload = Column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="dispatches")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    operator_id = Column(String(64), default="SYSTEM_AUTOMATION")
    action = Column(String(64), nullable=False)  # ACKNOWLEDGE, DISPATCH, MARK_FALSE_ALARM, RESOLVE
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    details = Column(Text, nullable=True)

    incident = relationship("Incident", back_populates="audit_logs")
