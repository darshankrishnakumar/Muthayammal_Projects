"""
Enterprise Real-Time Multi-Cue Inference Engine for Project 55.
Combines video stream decoding, spatial vehicle tracking, multi-cue feature extraction,
temporal attention deep learning inference, severity estimation, and evidence snapshotting.
"""

import os
import uuid
import datetime
import cv2
import numpy as np
import torch
from typing import Dict, Any, List, Optional, Tuple

from backend.app.core.config import settings
from backend.app.ml.dataset import VideoQualityChecker, preprocess_frame
from backend.app.ml.multi_cue_extractor import MultiCueFeatureExtractor
from backend.app.ml.temporal_fusion_model import MultiCueTemporalFusionModel
from backend.app.ml.severity_estimator import SeverityEstimator
from backend.app.services.notification_service import EmergencyNotificationService


class EnterpriseInferenceEngine:
    """
    High-performance, production inference engine running continuous multi-cue
    accident detection on CCTV and vehicle-camera feeds.
    """

    def __init__(
        self,
        weights_path: str = settings.MODEL_WEIGHTS_PATH,
        window_size: int = 16,
        confidence_threshold: float = settings.DEFAULT_CONFIDENCE_THRESHOLD,
        evidence_dir: str = settings.EVIDENCE_OUTPUT_DIR
    ):
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        self.device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))

        # Initialize Model
        self.model = MultiCueTemporalFusionModel().to(self.device)
        if os.path.exists(weights_path):
            self.model.load_state_dict(torch.load(weights_path, map_location=self.device, weights_only=True))
            print(f"Loaded Phase 2 optimized weights from {weights_path}")
        else:
            print(f"Warning: {weights_path} not found. Running with default initialized weights.")
        self.model.eval()

        self.cue_extractor = MultiCueFeatureExtractor(fps=25.0)
        self.notification_service = EmergencyNotificationService(evidence_dir=evidence_dir)

    def analyze_frame_sequence(
        self,
        frame_bgr: np.ndarray,
        frame_buffer: List[np.ndarray],
        raw_buffer: List[np.ndarray],
        detections: List[Dict[str, Any]],
        camera_meta: Dict[str, Any],
        frame_idx: int,
        fps: float = 25.0
    ) -> Dict[str, Any]:
        """
        Processes a single frame in the stream:
        1. Validates frame quality
        2. Updates multi-cue extractor
        3. Maintains sliding window
        4. Runs model inference if window is full
        5. Computes severity and triggers alert if accident detected
        """
        # 1. Quality Check
        quality = VideoQualityChecker.assess_frame_quality(frame_bgr)
        if not quality["accepted"]:
            return {
                "frame_idx": frame_idx,
                "status": "FRAME_REJECTED",
                "quality_info": quality,
                "confidence": 0.0,
                "is_accident": False
            }

        # 2. Extract multi-cues
        cues = self.cue_extractor.extract_cues(frame_bgr, detections)

        # 3. Buffer management
        norm_frame = preprocess_frame(frame_bgr)
        frame_buffer.append(norm_frame)
        raw_buffer.append(frame_bgr)

        if len(frame_buffer) > self.window_size:
            frame_buffer.pop(0)
            raw_buffer.pop(0)

        # Not enough frames yet for temporal window
        if len(frame_buffer) < self.window_size:
            return {
                "frame_idx": frame_idx,
                "status": "BUFFERING",
                "confidence": 0.0,
                "cues": cues,
                "is_accident": False
            }

        # 4. Deep Learning Multi-Cue Temporal Inference
        # Frames tensor: (1, T, C, H, W)
        frames_tensor = torch.tensor(np.stack(frame_buffer), dtype=torch.float32).unsqueeze(0).to(self.device)
        # Kinematics tensor: (1, 5)
        kin_tensor = torch.tensor(cues["cues_vector"], dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out = self.model(frames_tensor, kin_tensor)
            confidence = float(out["confidence"].cpu().item())
            cue_weights = out["cue_weights"].cpu().numpy().flatten().tolist()

        is_accident = confidence >= self.confidence_threshold
        status = "ACCIDENT_DETECTED" if is_accident else ("REVIEW_RECOMMENDED" if confidence >= 0.40 else "NORMAL")

        result = {
            "frame_idx": frame_idx,
            "timestamp_sec": round(frame_idx / fps, 2),
            "status": status,
            "confidence": round(confidence, 4),
            "is_accident": is_accident,
            "cues": {
                "trajectory_score": cues["trajectory_score"],
                "deceleration_score": cues["deceleration_score"],
                "orientation_score": cues["orientation_score"],
                "collision_score": cues["collision_score"],
                "immobility_score": cues["immobility_score"]
            },
            "cue_weights": [round(w, 3) for w in cue_weights],
            "quality_info": quality
        }

        # 5. If Accident Confirmed, estimate severity & generate evidence snapshot
        if is_accident:
            incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
            vehicles_count = len(detections) if len(detections) > 0 else 1

            severity_info = SeverityEstimator.estimate_severity(
                multi_cues=cues,
                vehicles_count=vehicles_count,
                camera_meta=camera_meta,
                confidence=confidence
            )

            # Generate visual evidence snapshot
            snapshot_path = self.notification_service.save_annotated_evidence_snapshot(
                frame_bgr=raw_buffer[-1],
                incident_id=incident_id,
                confidence=confidence,
                severity=severity_info["severity"],
                priority=severity_info["priority"],
                multi_cues=cues,
                location_meta=severity_info["location_estimate"]
            )

            # Build CAD dispatch payload
            cad_payload = self.notification_service.build_cad_payload(
                incident_id=incident_id,
                confidence=confidence,
                severity_info=severity_info,
                multi_cues=cues,
                evidence_snapshot_path=snapshot_path
            )

            result["incident_package"] = {
                "incident_id": incident_id,
                "severity_info": severity_info,
                "snapshot_path": snapshot_path,
                "cad_payload": cad_payload
            }

        return result

    def render_hud_overlay(
        self,
        frame_bgr: np.ndarray,
        analysis_result: Dict[str, Any],
        detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Draws professional live video HUD overlays: vehicle bounding boxes,
        velocity vectors, multi-cue telemetry indicators, and alert warning banners.
        """
        annotated = frame_bgr.copy()
        h, w, _ = annotated.shape

        is_accident = analysis_result.get("is_accident", False)
        confidence = analysis_result.get("confidence", 0.0)
        cues = analysis_result.get("cues", {})

        # Draw vehicle bounding boxes and speed tags
        for det in detections:
            box = det.get("box", [0, 0, 10, 10])
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            v_id = det.get("vehicle_id", 0)
            spd = det.get("speed", 0.0)

            box_color = (0, 0, 255) if is_accident else (0, 255, 120)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)
            cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + 80, y1), box_color, -1)
            cv2.putText(
                annotated,
                f"V{v_id} | {spd:.0f}px/s",
                (x1 + 3, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 0) if not is_accident else (255, 255, 255),
                1
            )

        # Top Bar
        cv2.rectangle(annotated, (0, 0), (w, 36), (20, 22, 28), -1)
        status_text = "STATUS: ACCIDENT DETECTED!" if is_accident else "STATUS: NORMAL FLOW"
        status_color = (0, 50, 255) if is_accident else (100, 240, 100)
        cv2.putText(annotated, status_text, (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)

        conf_str = f"CONF: {confidence*100:.1f}%"
        cv2.putText(annotated, conf_str, (w - 140, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)

        # Bottom Telemetry Overlay
        cv2.rectangle(annotated, (0, h - 28), (w, h), (20, 22, 28), -1)
        telemetry_str = (
            f"Traj: {cues.get('trajectory_score', 0):.2f} | "
            f"Decel: {cues.get('deceleration_score', 0):.2f} | "
            f"Orient: {cues.get('orientation_score', 0):.2f} | "
            f"Coll: {cues.get('collision_score', 0):.2f} | "
            f"Immob: {cues.get('immobility_score', 0):.2f}"
        )
        cv2.putText(annotated, telemetry_str, (15, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 210, 230), 1)

        return annotated
