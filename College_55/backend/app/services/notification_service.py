"""
Automated Emergency Notification and Dispatch Service for Project 55.
Formats CAD-compliant payloads, generates annotated visual evidence snapshots,
dispatches multi-channel alerts (Webhook, CAD, SMS, Email), and records audit trails.
"""

import os
import json
import uuid
import datetime
import cv2
import numpy as np
from typing import Dict, Any, List, Optional


class EmergencyNotificationService:
    """
    Manages automated emergency alerting, dispatch payload construction,
    and visual evidence preservation.
    """

    def __init__(self, evidence_dir: str = "data/processed/evidence_snapshots"):
        self.evidence_dir = evidence_dir
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.dispatched_history: List[Dict[str, Any]] = []

    def save_annotated_evidence_snapshot(
        self,
        frame_bgr: np.ndarray,
        incident_id: str,
        confidence: float,
        severity: str,
        priority: str,
        multi_cues: Dict[str, Any],
        location_meta: Dict[str, Any]
    ) -> str:
        """
        Overlays professional HUD metadata, bounding boxes, and timestamp onto frame,
        saving it as permanent visual proof of the detected incident.
        """
        canvas = frame_bgr.copy()
        h, w, _ = canvas.shape

        # Semi-transparent top HUD banner
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, 0), (w, 85), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)

        # Header Title & Severity Badge
        badge_color = (0, 0, 220) if severity == "Critical" else ((0, 140, 255) if severity == "Severe" else (0, 220, 220))
        cv2.rectangle(canvas, (15, 12), (150, 42), badge_color, -1)
        cv2.putText(canvas, f"{priority}", (22, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        cv2.putText(
            canvas,
            f"INCIDENT: {incident_id}",
            (165, 33),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        cv2.putText(
            canvas,
            f"TIME: {now_str} | CONFIDENCE: {confidence*100:.1f}%",
            (15, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (210, 220, 230),
            1
        )

        # Camera & Coordinates
        cam_id = location_meta.get("camera_id", "CAM-01")
        coords = location_meta.get("coordinates", {})
        lat = coords.get("latitude", 37.7749)
        lon = coords.get("longitude", -122.4194)
        cv2.putText(
            canvas,
            f"LOC: {cam_id} ({lat:.4f}, {lon:.4f}) | ZONE: {location_meta.get('lane_zone', 'Main')}",
            (w - 360, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (180, 240, 180),
            1
        )

        # Bottom Cues Bar
        overlay_bot = canvas.copy()
        cv2.rectangle(overlay_bot, (0, h - 35), (w, h), (15, 15, 20), -1)
        cv2.addWeighted(overlay_bot, 0.75, canvas, 0.25, 0, canvas)

        cues_text = (
            f"Cues: Traj={multi_cues.get('trajectory_score', 0):.2f} | "
            f"Decel={multi_cues.get('deceleration_score', 0):.2f} | "
            f"Orient={multi_cues.get('orientation_score', 0):.2f} | "
            f"Collision={multi_cues.get('collision_score', 0):.2f} | "
            f"Immobile={multi_cues.get('immobility_score', 0):.2f}"
        )
        cv2.putText(canvas, cues_text, (15, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)

        filename = f"evidence_{incident_id}_{priority}.jpg"
        filepath = os.path.join(self.evidence_dir, filename)
        cv2.imwrite(filepath, canvas)
        return filepath

    def build_cad_payload(
        self,
        incident_id: str,
        confidence: float,
        severity_info: Dict[str, Any],
        multi_cues: Dict[str, Any],
        evidence_snapshot_path: str
    ) -> Dict[str, Any]:
        """
        Builds standardized Computer-Aided Dispatch (CAD) payload.
        """
        loc = severity_info.get("location_estimate", {})
        coords = loc.get("coordinates", {})

        payload = {
            "cad_version": "2.1",
            "dispatch_incident_id": incident_id,
            "call_type": "MOTOR_VEHICLE_COLLISION_AUTOMATED_CV",
            "priority": severity_info.get("priority", "P2-High"),
            "severity": severity_info.get("severity", "Severe"),
            "confidence_score": round(confidence, 4),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "location": {
                "roadway": loc.get("roadway_name", "Highway Corridor"),
                "camera_id": loc.get("camera_id", "CAM-UNKNOWN"),
                "lane_zone": loc.get("lane_zone", "Center"),
                "latitude": coords.get("latitude", 37.7749),
                "longitude": coords.get("longitude", -122.4194)
            },
            "scene_telemetry": {
                "vehicles_involved": severity_info.get("vehicles_involved", 1),
                "rollover_detected": severity_info.get("rollover_detected", False),
                "rationale": severity_info.get("evidence_rationale", ""),
                "multi_cue_breakdown": {
                    "trajectory_deviation_score": multi_cues.get("trajectory_score", 0.0),
                    "sudden_deceleration_score": multi_cues.get("deceleration_score", 0.0),
                    "abnormal_orientation_score": multi_cues.get("orientation_score", 0.0),
                    "collision_motion_score": multi_cues.get("collision_score", 0.0),
                    "post_collision_immobility_score": multi_cues.get("immobility_score", 0.0)
                }
            },
            "dispatch_recommendation": {
                "units_assigned": severity_info.get("recommended_dispatch", ["EMS", "Police"]),
                "target_arrival_sla": severity_info.get("expected_response_time", "< 8 minutes")
            },
            "evidence": {
                "snapshot_image_url": f"/api/incidents/evidence/{os.path.basename(evidence_snapshot_path)}"
            }
        }
        return payload

    def dispatch_emergency_alert(
        self,
        cad_payload: Dict[str, Any],
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches alerts across chosen channels (CAD, Webhook, SMS, Email).
        """
        if channels is None:
            channels = ["CAD_SYSTEM", "POLICE_WEBHOOK", "EMS_DISPATCH"]

        dispatch_results = []
        for ch in channels:
            # Emulate real-world carrier / CAD API transmission
            dispatch_entry = {
                "dispatch_id": f"DSP-{uuid.uuid4().hex[:8].upper()}",
                "channel": ch,
                "status": "DELIVERED",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "response_code": 200,
                "recipient": f"CAD_ROUTER_SERVICE@{ch.lower()}.gov"
            }
            dispatch_results.append(dispatch_entry)

        record = {
            "incident_id": cad_payload["dispatch_incident_id"],
            "dispatches": dispatch_results,
            "payload": cad_payload
        }
        self.dispatched_history.append(record)
        return record
