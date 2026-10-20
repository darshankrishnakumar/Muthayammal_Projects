"""
Accident Severity, Priority, and Location Estimator for Project 55.
Evaluates physical impact evidence, vehicle rollover, count of involved vehicles,
deceleration peak, and post-collision immobility to calculate emergency dispatch priority.
Includes deep multi-task regression neural network.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List

class CrashSeverityAndDispatchNeuralNet(nn.Module):
    """
    Model 2: Deep Multi-Task Crash Severity, Delta-V, and Emergency Dispatch Regressor.
    Ingests 12-dimensional kinematic impact telemetry:
    [deceleration_g, orientation_yaw_deg, trajectory_deviation_m, impact_force_kn,
     delta_v_kph, post_impact_immobility_sec, actual_speed_kph, speed_limit_kph,
     vehicles_involved, road_friction_coeff, visibility_m, ambient_lux].
    Predicts Severity Score (0-100), Delta-V (km/h), Casualty Risk (0.0-1.0),
    Required EMS Units (0-10), and 4-class Priority Logits (P1-Critical, P2-High, P3-Medium, P4-Low).
    """
    def __init__(self, input_dim: int = 12):
        super().__init__()
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.10),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True)
        )
        self.head_severity = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_deltav = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_risk = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_units = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_priority = nn.Linear(32, 4) # P1, P2, P3, P4

    def forward(self, x: torch.Tensor):
        feat = self.feature_net(x)
        severity = self.head_severity(feat) * 100.0   # 0-100 severity index
        deltav = self.head_deltav(feat) * 120.0       # 0-120 km/h delta-v
        risk = self.head_risk(feat)                   # 0.0 - 1.0 probability
        units = self.head_units(feat) * 10.0          # 0-10 dispatch units
        priority_logits = self.head_priority(feat)
        return {
            "severity_score": severity,
            "delta_v_kph": deltav,
            "casualty_risk": risk,
            "required_ems_units": units,
            "priority_logits": priority_logits
        }

class SeverityEstimator:
    """
    Computes calibrated accident severity, response priority (P1-P4),
    and recommended emergency dispatch units from visual and kinematic evidence.
    """

    @staticmethod
    def estimate_severity(
        multi_cues: Dict[str, Any],
        vehicles_count: int,
        camera_meta: Dict[str, Any],
        confidence: float
    ) -> Dict[str, Any]:
        decel_score = float(multi_cues.get("deceleration_score", 0.0))
        orient_score = float(multi_cues.get("orientation_score", 0.0))
        collision_score = float(multi_cues.get("collision_score", 0.0))
        immobility_score = float(multi_cues.get("immobility_score", 0.0))
        traj_score = float(multi_cues.get("trajectory_score", 0.0))

        impact_pts = (decel_score * 0.5 + collision_score * 0.5) * 40.0
        rollover_detected = orient_score >= 0.55
        orientation_pts = orient_score * 25.0
        vehicle_pts = min(15.0, (vehicles_count - 1) * 7.5) if vehicles_count > 1 else 0.0
        immobility_pts = immobility_score * 20.0

        raw_severity_score = impact_pts + orientation_pts + vehicle_pts + immobility_pts
        calibrated_score = round(float(raw_severity_score * (0.5 + 0.5 * confidence)), 1)
        calibrated_score = max(5.0, min(100.0, calibrated_score))

        if calibrated_score >= 75.0 or rollover_detected:
            severity = "Critical"
            priority = "P1-Critical"
            recommended_dispatch = ["Emergency Medical Services (EMS)", "Fire & Heavy Extrication", "State Highway Patrol"]
            expected_response_time = "< 5 minutes"
        elif calibrated_score >= 50.0:
            severity = "Severe"
            priority = "P2-High"
            recommended_dispatch = ["Emergency Medical Services (EMS)", "Police Patrol", "Heavy Tow Service"]
            expected_response_time = "< 8 minutes"
        elif calibrated_score >= 30.0:
            severity = "Moderate"
            priority = "P3-Medium"
            recommended_dispatch = ["Police Patrol", "Traffic Tow & Cleanup"]
            expected_response_time = "< 15 minutes"
        else:
            severity = "Minor"
            priority = "P4-Low"
            recommended_dispatch = ["Traffic Management Support", "Incident Response Vehicle"]
            expected_response_time = "< 25 minutes"

        factors = []
        if decel_score > 0.4:
            factors.append("Sudden high deceleration shock")
        if rollover_detected:
            factors.append("Vehicle rollover / abnormal angular displacement")
        elif orient_score > 0.3:
            factors.append("Vehicle spinout / cross-lane skew")
        if vehicles_count >= 2:
            factors.append(f"Multi-vehicle impact involving {vehicles_count} vehicles")
        if immobility_score > 0.5:
            factors.append("Persistent post-collision immobility in active roadway")
        if traj_score > 0.5:
            factors.append("Acute trajectory departure")

        rationale = "; ".join(factors) if factors else "Kinematic anomaly signature detected."

        cam_id = camera_meta.get("camera_id", "CAM-UNKNOWN")
        roadway = camera_meta.get("roadway", "Highway 101 Corridor")
        lat = camera_meta.get("lat", 37.7749)
        lon = camera_meta.get("lon", -122.4194)
        zone = camera_meta.get("zone", "Center Lanes")

        location_estimate = {
            "camera_id": cam_id,
            "roadway_name": roadway,
            "coordinates": {"latitude": lat, "longitude": lon},
            "lane_zone": zone,
            "geohash": camera_meta.get("geohash", "9q8yyk")
        }

        return {
            "severity": severity,
            "priority": priority,
            "severity_score": calibrated_score,
            "rollover_detected": rollover_detected,
            "vehicles_involved": vehicles_count,
            "recommended_dispatch": recommended_dispatch,
            "expected_response_time": expected_response_time,
            "evidence_rationale": rationale,
            "location_estimate": location_estimate
        }
