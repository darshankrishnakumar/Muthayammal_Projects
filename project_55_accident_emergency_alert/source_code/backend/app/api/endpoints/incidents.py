"""
Incidents API Endpoints for Project 55.
Handles listing, details, operator triage, status transitions, and evidence snapshots.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import Incident, Camera, DispatchAlert, AuditLog

router = APIRouter()


class TriageRequest(BaseModel):
    action: str  # ACKNOWLEDGE, DISPATCH, MARK_FALSE_ALARM, RESOLVE
    operator_id: str = "OPERATOR_01"
    notes: Optional[str] = None
    dispatch_units: Optional[List[str]] = None


@router.get("/")
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (New, Acknowledged, Dispatched, False Alarm, Resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (Critical, Severe, Moderate, Minor)"),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Incident).order_by(Incident.timestamp.desc())
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)

    incidents = query.limit(limit).all()
    results = []
    for inc in incidents:
        cam = inc.camera
        results.append({
            "id": inc.id,
            "incident_uuid": inc.incident_uuid,
            "camera_id": cam.camera_id if cam else "UNKNOWN",
            "camera_name": cam.name if cam else "Roadside Camera",
            "roadway": cam.roadway if cam else "Corridor",
            "timestamp": inc.timestamp.isoformat(),
            "confidence": inc.confidence,
            "severity": inc.severity,
            "priority": inc.priority,
            "status": inc.status,
            "vehicles_involved": inc.vehicles_involved,
            "rollover_detected": inc.rollover_detected,
            "rationale": inc.rationale,
            "multi_cues": inc.multi_cues,
            "evidence_snapshot_url": f"/api/incidents/evidence/{os.path.basename(inc.snapshot_path)}" if inc.snapshot_path else None
        })
    return {"count": len(results), "incidents": results}


@router.get("/{incident_uuid}")
def get_incident_details(incident_uuid: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_uuid == incident_uuid).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    cam = inc.camera
    dispatches = db.query(DispatchAlert).filter(DispatchAlert.incident_id == inc.id).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.incident_id == inc.id).order_by(AuditLog.timestamp.asc()).all()

    return {
        "incident_uuid": inc.incident_uuid,
        "timestamp": inc.timestamp.isoformat(),
        "confidence": inc.confidence,
        "severity": inc.severity,
        "priority": inc.priority,
        "status": inc.status,
        "vehicles_involved": inc.vehicles_involved,
        "rollover_detected": inc.rollover_detected,
        "rationale": inc.rationale,
        "multi_cues": inc.multi_cues,
        "camera": {
            "camera_id": cam.camera_id,
            "name": cam.name,
            "roadway": cam.roadway,
            "latitude": cam.latitude,
            "longitude": cam.longitude,
            "zone": cam.zone
        } if cam else None,
        "evidence_snapshot_url": f"/api/incidents/evidence/{os.path.basename(inc.snapshot_path)}" if inc.snapshot_path else None,
        "dispatches": [
            {
                "dispatch_uuid": d.dispatch_uuid,
                "channel": d.channel,
                "status": d.status,
                "dispatched_at": d.dispatched_at.isoformat(),
                "recipient": d.recipient
            } for d in dispatches
        ],
        "audit_logs": [
            {
                "action": a.action,
                "operator_id": a.operator_id,
                "timestamp": a.timestamp.isoformat(),
                "details": a.details
            } for a in audit_logs
        ]
    }


@router.post("/{incident_uuid}/triage")
def triage_incident(incident_uuid: str, req: TriageRequest, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_uuid == incident_uuid).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    action_map = {
        "ACKNOWLEDGE": "Acknowledged",
        "DISPATCH": "Dispatched",
        "MARK_FALSE_ALARM": "False Alarm",
        "RESOLVE": "Resolved"
    }

    new_status = action_map.get(req.action.upper())
    if not new_status:
        raise HTTPException(status_code=400, detail=f"Invalid triage action: {req.action}")

    inc.status = new_status
    audit = AuditLog(
        incident_id=inc.id,
        operator_id=req.operator_id,
        action=req.action.upper(),
        details=f"Status set to {new_status}. Notes: {req.notes or 'None'}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Incident {incident_uuid} updated to {new_status}",
        "incident_uuid": incident_uuid,
        "new_status": new_status
    }


@router.get("/evidence/{filename}")
def get_evidence_snapshot(filename: str):
    file_path = os.path.join(settings.EVIDENCE_OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        # Fallback check in phase1 samples if requested
        file_path_p1 = os.path.join("experiments/phase1_visual_samples", filename)
        if os.path.exists(file_path_p1):
            return FileResponse(file_path_p1, media_type="image/jpeg")
        raise HTTPException(status_code=404, detail="Evidence snapshot not found")
    return FileResponse(file_path, media_type="image/jpeg")
