"""
Emergency Alert and CAD Dispatch Service Unit Tests.
"""

import os
import unittest
import numpy as np
from backend.app.services.notification_service import EmergencyNotificationService


class TestEmergencyNotificationService(unittest.TestCase):

    def setUp(self):
        self.service = EmergencyNotificationService(evidence_dir="data/processed/evidence_snapshots")
        self.frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.incident_id = "INC-TEST-001"
        self.multi_cues = {
            "trajectory_score": 0.82,
            "deceleration_score": 0.91,
            "orientation_score": 0.65,
            "collision_score": 0.94,
            "immobility_score": 0.88
        }
        self.location_meta = {
            "camera_id": "CAM-TEST",
            "roadway_name": "I-80 Bridge Approach",
            "lane_zone": "Deck 1",
            "coordinates": {"latitude": 37.7983, "longitude": -122.3778}
        }

    def test_save_evidence_snapshot(self):
        snapshot_path = self.service.save_annotated_evidence_snapshot(
            frame_bgr=self.frame,
            incident_id=self.incident_id,
            confidence=0.97,
            severity="Critical",
            priority="P1-Critical",
            multi_cues=self.multi_cues,
            location_meta=self.location_meta
        )
        self.assertTrue(os.path.exists(snapshot_path))

    def test_cad_payload_generation(self):
        severity_info = {
            "severity": "Critical",
            "priority": "P1-Critical",
            "vehicles_involved": 2,
            "rollover_detected": True,
            "evidence_rationale": "Severe rollover impact",
            "recommended_dispatch": ["EMS", "Fire Rescue"],
            "expected_response_time": "< 5 minutes",
            "location_estimate": self.location_meta
        }
        cad = self.service.build_cad_payload(
            incident_id=self.incident_id,
            confidence=0.97,
            severity_info=severity_info,
            multi_cues=self.multi_cues,
            evidence_snapshot_path="data/processed/evidence_snapshots/sample.jpg"
        )
        self.assertEqual(cad["dispatch_incident_id"], self.incident_id)
        self.assertEqual(cad["priority"], "P1-Critical")
        self.assertIn("scene_telemetry", cad)
        self.assertTrue(cad["scene_telemetry"]["rollover_detected"])

    def test_multi_channel_dispatch(self):
        cad = {
            "dispatch_incident_id": self.incident_id,
            "priority": "P1-Critical"
        }
        dispatch_record = self.service.dispatch_emergency_alert(cad, channels=["CAD_SYSTEM", "EMS_DISPATCH"])
        self.assertEqual(len(dispatch_record["dispatches"]), 2)
        self.assertEqual(dispatch_record["dispatches"][0]["status"], "DELIVERED")


if __name__ == "__main__":
    unittest.main()
