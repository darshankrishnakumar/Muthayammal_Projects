"""
Multi-Cue Kinematic and Motion Anomaly Extractor for Project 55.
Extracts 5 physical cues from consecutive video frames:
1. Trajectory deviation
2. Sudden deceleration
3. Abnormal orientation (rollover / spin / cross-lane)
4. Collision motion patterns (optical flow convergence / bounding box proximity)
5. Post-collision immobility
"""

import math
import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional, Any


class TrackedObject:
    """Maintains kinematic state and trajectory history for a tracked vehicle."""
    def __init__(self, track_id: int, bbox: List[float], speed: float = 0.0, angle: float = 0.0):
        self.track_id = track_id
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.cx = (bbox[0] + bbox[2]) / 2.0
        self.cy = (bbox[1] + bbox[3]) / 2.0
        self.speed = speed
        self.angle = angle
        self.immobile_frames = 0
        self.history_centroids: List[Tuple[float, float]] = [(self.cx, self.cy)]
        self.history_speeds: List[float] = [speed]
        self.history_angles: List[float] = [angle]
        self.history_decelerations: List[float] = [0.0]

    def update(
        self,
        bbox: List[float],
        dt: float = 0.04,
        detected_angle: Optional[float] = None,
        detected_speed: Optional[float] = None,
        detected_decel: Optional[float] = None
    ):
        new_cx = (bbox[0] + bbox[2]) / 2.0
        new_cy = (bbox[1] + bbox[3]) / 2.0
        dx = new_cx - self.cx
        dy = new_cy - self.cy
        distance_px = math.hypot(dx, dy)

        # Teleport / boundary re-entry check: avoid spurious velocity/deceleration spikes
        if distance_px > 80.0:
            self.history_centroids = [(new_cx, new_cy)]
            self.history_speeds = [self.speed]
            self.history_angles = [detected_angle if detected_angle is not None else self.angle]
            self.history_decelerations = [0.0]
            self.cx = new_cx
            self.cy = new_cy
            self.bbox = bbox
            return

        # Deceleration and Speed calculation: use tracker/metadata value if provided, else compute
        if detected_decel is not None:
            decel = detected_decel
            instant_speed = detected_speed if detected_speed is not None else (distance_px / max(1e-4, dt))
        else:
            instant_speed = distance_px / max(1e-4, dt)
            prev_speed = self.speed
            decel = max(0.0, (prev_speed - instant_speed) / max(1e-4, dt))

        # Heading angle calculation
        if detected_angle is not None:
            heading = detected_angle
        elif distance_px > 2.0:
            heading = math.degrees(math.atan2(dx, -dy)) % 360.0
        else:
            heading = self.angle

        # Immobility update (threshold in px/s)
        if instant_speed < 8.0:
            self.immobile_frames += 1
        else:
            self.immobile_frames = 0

        self.bbox = bbox
        self.cx = new_cx
        self.cy = new_cy
        self.speed = instant_speed
        self.angle = heading

        self.history_centroids.append((new_cx, new_cy))
        self.history_speeds.append(instant_speed)
        self.history_angles.append(heading)
        self.history_decelerations.append(decel)

        if len(self.history_centroids) > 50:
            self.history_centroids.pop(0)
            self.history_speeds.pop(0)
            self.history_angles.pop(0)
            self.history_decelerations.pop(0)


class MultiCueFeatureExtractor:
    """
    Computes normalized multi-cue feature scores from video frames and vehicle tracks.
    """

    def __init__(self, fps: float = 25.0):
        self.fps = fps
        self.dt = 1.0 / max(1.0, fps)
        self.tracks: Dict[int, TrackedObject] = {}
        self.prev_gray: Optional[np.ndarray] = None

    def compute_optical_flow_intensity(self, frame_bgr: np.ndarray) -> float:
        """Computes average Farneback optical flow magnitude between consecutive frames."""
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        if self.prev_gray is None or self.prev_gray.shape != gray.shape:
            self.prev_gray = gray
            return 0.0

        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray, None,
            pyr_scale=0.5, levels=2, winsize=15, iterations=2, poly_n=5, poly_sigma=1.1, flags=0
        )
        self.prev_gray = gray
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        # Return 95th percentile flow magnitude to capture local shockwave without noise
        p95 = float(np.percentile(magnitude, 95))
        return min(1.0, p95 / 25.0)

    def extract_cues(
        self,
        frame_bgr: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extracts the 5 distinct accident cues:
        1. trajectory_score: Trajectory deviation and curvature anomaly
        2. deceleration_score: Sudden velocity drop anomaly
        3. orientation_score: Abnormal vehicle roll/pitch/yaw anomaly
        4. collision_score: Proximity vector convergence & optical flow shock
        5. immobility_score: Post-collision persistent stationary state
        """
        # Match detections to existing tracks or create new
        current_tracked_ids = set()
        for det in detections:
            v_id = det.get("vehicle_id", det.get("track_id", 0))
            box = det.get("box", [0, 0, 10, 10])
            angle = det.get("angle", None)
            if v_id in self.tracks:
                self.tracks[v_id].update(
                    box,
                    dt=self.dt,
                    detected_angle=angle,
                    detected_speed=det.get("speed"),
                    detected_decel=det.get("deceleration")
                )
            else:
                self.tracks[v_id] = TrackedObject(v_id, box, speed=det.get("speed", 0.0), angle=angle or 0.0)
            current_tracked_ids.add(v_id)

        # 1. Trajectory Deviation Score
        trajectory_scores = []
        for t_id, track in self.tracks.items():
            if len(track.history_centroids) >= 6:
                # Measure variance from linear extrapolation
                pts = np.array(track.history_centroids[-6:])
                x, y = pts[:, 0], pts[:, 1]
                # Direction changes
                dx = np.diff(x)
                dy = np.diff(y)
                angles = np.arctan2(dy, dx)
                angle_diffs = np.abs(np.diff(angles))
                max_dev = float(np.max(angle_diffs)) if len(angle_diffs) > 0 else 0.0
                trajectory_scores.append(min(1.0, max_dev / (math.pi / 2)))
            else:
                trajectory_scores.append(0.0)
        trajectory_score = max(trajectory_scores) if trajectory_scores else 0.0

        # 2. Sudden Deceleration Score
        decel_scores = []
        for t_id, track in self.tracks.items():
            recent_decel = max(track.history_decelerations[-5:]) if track.history_decelerations else 0.0
            # Normalize: deceleration > 120 px/s^2 represents sharp emergency impact
            norm_decel = min(1.0, recent_decel / 120.0)
            decel_scores.append(norm_decel)
        deceleration_score = max(decel_scores) if decel_scores else 0.0

        # 3. Abnormal Vehicle Orientation Score
        orient_scores = []
        for t_id, track in self.tracks.items():
            # If angle deviates significantly from normal roadway axis (0 or 180 degrees)
            angle = track.angle % 360.0
            dev_from_axis = min(abs(angle - 0.0), abs(angle - 180.0), abs(angle - 360.0))
            # Rapid angle change rate in last 4 frames
            if len(track.history_angles) >= 4:
                d_ang = abs(track.history_angles[-1] - track.history_angles[-4])
                if d_ang > 180:
                    d_ang = 360 - d_ang
            else:
                d_ang = 0.0

            angle_score = min(1.0, (dev_from_axis / 60.0) * 0.6 + (d_ang / 45.0) * 0.4)
            orient_scores.append(angle_score)
        orientation_score = max(orient_scores) if orient_scores else 0.0

        # 4. Collision Motion Pattern Score (Proximity + Optical Flow)
        optical_flow_shock = self.compute_optical_flow_intensity(frame_bgr)
        min_inter_dist = 9999.0
        active_vehicles = list(self.tracks.values())
        for i in range(len(active_vehicles)):
            for j in range(i + 1, len(active_vehicles)):
                dist = math.hypot(
                    active_vehicles[i].cx - active_vehicles[j].cx,
                    active_vehicles[i].cy - active_vehicles[j].cy
                )
                if dist < min_inter_dist:
                    min_inter_dist = dist

        # Distance < 50 px indicates physical contact / overlap
        proximity_shock = max(0.0, 1.0 - (min_inter_dist / 60.0)) if min_inter_dist < 60.0 else 0.0
        collision_score = float(np.clip(0.6 * proximity_shock + 0.4 * optical_flow_shock, 0.0, 1.0))

        # 5. Post-Collision Immobility Score
        immobility_scores = []
        for t_id, track in self.tracks.items():
            immobile_sec = track.immobile_frames * self.dt
            # Sustained immobility over 2 seconds in roadway -> score = 1.0
            norm_immobile = min(1.0, immobile_sec / 2.0)
            immobility_scores.append(norm_immobile)
        immobility_score = max(immobility_scores) if immobility_scores else 0.0

        # Composite multi-cue feature vector
        cues_vector = np.array([
            trajectory_score,
            deceleration_score,
            orientation_score,
            collision_score,
            immobility_score
        ], dtype=np.float32)

        return {
            "trajectory_score": round(float(trajectory_score), 3),
            "deceleration_score": round(float(deceleration_score), 3),
            "orientation_score": round(float(orientation_score), 3),
            "collision_score": round(float(collision_score), 3),
            "immobility_score": round(float(immobility_score), 3),
            "cues_vector": cues_vector,
            "optical_flow_intensity": round(float(optical_flow_shock), 3),
            "active_tracks_count": len(self.tracks)
        }
