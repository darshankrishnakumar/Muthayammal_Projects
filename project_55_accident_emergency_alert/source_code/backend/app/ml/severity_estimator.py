"""
Accident Severity, Priority, and Location Estimator for Project 55.
Evaluates physical impact evidence, vehicle rollover, count of involved vehicles,
deceleration peak, and post-collision immobility to calculate emergency dispatch priority.
"""

from typing import Dict, Any, List


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
        """
        Calculates severity index on a scale of 0 to 100 based on physical impact evidence.
        """
        decel_score = float(multi_cues.get("deceleration_score", 0.0))
        orient_score = float(multi_cues.get("orientation_score", 0.0))
        collision_score = float(multi_cues.get("collision_score", 0.0))
        immobility_score = float(multi_cues.get("immobility_score", 0.0))
        traj_score = float(multi_cues.get("trajectory_score", 0.0))

        # 1. Base Impact Energy Score (0 - 40 pts)
        impact_pts = (decel_score * 0.5 + collision_score * 0.5) * 40.0

        # 2. Structural Trauma & Rollover (0 - 25 pts)
        # Orientation score > 0.6 indicates rollover or sideways vehicular inversion
        rollover_detected = orient_score >= 0.55
        orientation_pts = orient_score * 25.0

        # 3. Multi-Vehicle Factor (0 - 15 pts)
        vehicle_pts = min(15.0, (vehicles_count - 1) * 7.5) if vehicles_count > 1 else 0.0

        # 4. Immobility & Road Obstruction (0 - 20 pts)
        immobility_pts = immobility_score * 20.0

        raw_severity_score = impact_pts + orientation_pts + vehicle_pts + immobility_pts
        # Scale by confidence factor
        calibrated_score = round(float(raw_severity_score * (0.5 + 0.5 * confidence)), 1)
        calibrated_score = max(5.0, min(100.0, calibrated_score))

        # Determine Categorical Severity and Emergency Priority
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

        # Evidence Summary Rationale
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

        # Location Estimation
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
