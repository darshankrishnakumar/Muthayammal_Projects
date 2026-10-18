"""
Phase 1 Initial Application Prototype.
Demonstrates the end-to-end inference workflow:
Accepts video input -> Validates quality -> Runs preprocessing ->
Invokes baseline model -> Returns accident confidence score ->
Generates annotated visual proof frames.
"""

import os
import argparse
import json
import cv2
import numpy as np
import torch
from typing import Dict, Any, List

from backend.app.ml.dataset import VideoQualityChecker, preprocess_frame
from backend.app.ml.baseline_model import BaselineTemporalCNNGRU


class InitialPrototypeInference:
    """
    Decoupled inference wrapper for the Phase 1 Baseline Model.
    Can be seamlessly hot-swapped for Phase 2 models without modifying caller code.
    """

    def __init__(self, model_weights_path: str = "experiments/baseline_model.pt", window_size: int = 16):
        self.window_size = window_size
        self.device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = BaselineTemporalCNNGRU().to(self.device)

        if os.path.exists(model_weights_path):
            self.model.load_state_dict(torch.load(model_weights_path, map_location=self.device, weights_only=True))
            print(f"Loaded trained baseline weights from {model_weights_path}")
        else:
            print(f"Warning: {model_weights_path} not found. Running with initial weights.")

        self.model.eval()

    def process_video(
        self,
        video_path: str,
        output_evidence_dir: str = "experiments/phase1_visual_samples",
        stride: int = 8,
        confidence_threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Processes a video, checks frame quality, performs sliding-window inference,
        and records visual evidence of any detected accident frame.
        """
        os.makedirs(output_evidence_dir, exist_ok=True)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_buffer = []
        raw_frames_buffer = []
        predictions = []
        high_confidence_alerts = []

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            # Quality Check
            q_res = VideoQualityChecker.assess_frame_quality(frame)
            if not q_res["accepted"]:
                print(f"Warning: Frame {frame_idx} rejected: {q_res['reason']}")

            preprocessed = preprocess_frame(frame)
            frame_buffer.append(preprocessed)
            raw_frames_buffer.append(frame)

            if len(frame_buffer) > self.window_size:
                frame_buffer.pop(0)
                raw_frames_buffer.pop(0)

            # Evaluate model every `stride` frames when buffer is full
            if len(frame_buffer) == self.window_size and (frame_idx % stride == 0):
                # Shape: (1, T, C, H, W)
                tensor_in = torch.tensor(np.stack(frame_buffer), dtype=torch.float32).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    confidence = float(self.model(tensor_in).cpu().item())

                status = "ACCIDENT_DETECTED" if confidence >= confidence_threshold else "NORMAL"
                timestamp_sec = round(frame_idx / fps, 2)

                pred_entry = {
                    "frame_idx": frame_idx,
                    "timestamp_sec": timestamp_sec,
                    "accident_confidence": round(confidence, 4),
                    "status": status
                }
                predictions.append(pred_entry)

                # Visual Evidence Recording (Phase 1 Deliverable)
                if confidence >= confidence_threshold:
                    evidence_frame = raw_frames_buffer[-1].copy()
                    cv2.putText(
                        evidence_frame,
                        f"ALERT: ACCIDENT DETECTED! (Conf: {confidence*100:.1f}%)",
                        (30, 45),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                    cv2.putText(
                        evidence_frame,
                        f"Time: {timestamp_sec:.2f}s | Frame: {frame_idx}",
                        (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 255, 255),
                        1
                    )
                    evidence_filename = f"evidence_frame_{frame_idx}_{int(confidence*100)}pct.jpg"
                    evidence_path = os.path.join(output_evidence_dir, evidence_filename)
                    cv2.imwrite(evidence_path, evidence_frame)
                    pred_entry["evidence_image"] = evidence_path
                    high_confidence_alerts.append(pred_entry)

            frame_idx += 1

        cap.release()

        return {
            "video_path": video_path,
            "total_frames_analyzed": frame_idx,
            "fps": fps,
            "total_evaluations": len(predictions),
            "alerts_triggered": len(high_confidence_alerts),
            "predictions_sample": predictions[:10],
            "high_confidence_alerts": high_confidence_alerts
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 1 Initial Application Prototype for Accident Detection")
    parser.add_argument("--video", type=str, default="data/sample_videos/high_speed_collision.mp4", help="Path to input video file")
    parser.add_argument("--weights", type=str, default="experiments/baseline_model.pt", help="Path to trained baseline model weights")
    parser.add_argument("--stride", type=int, default=5, help="Frame stride for sliding window")
    args = parser.parse_args()

    print(f"=== Project 55: Phase 1 Prototype Execution ===")
    print(f"Input Video: {args.video}")
    engine = InitialPrototypeInference(model_weights_path=args.weights)
    result = engine.process_video(args.video, stride=args.stride)

    print("\n--- Inference Summary ---")
    print(f"Total Frames Analyzed: {result['total_frames_analyzed']}")
    print(f"Alerts Triggered: {result['alerts_triggered']}")
    if result["alerts_triggered"] > 0:
        print(f"Earliest Alert: Frame {result['high_confidence_alerts'][0]['frame_idx']} at {result['high_confidence_alerts'][0]['timestamp_sec']}s (Conf: {result['high_confidence_alerts'][0]['accident_confidence']})")
        print(f"Visual Evidence Saved to: {result['high_confidence_alerts'][0].get('evidence_image')}")
    else:
        print("Normal traffic flow detected. No accident anomalies triggered.")

if __name__ == "__main__":
    main()
