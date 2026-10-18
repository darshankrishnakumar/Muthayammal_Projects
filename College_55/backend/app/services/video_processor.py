"""
Video Stream Processor and Real-Time Pipeline Service for Project 55.
Ingests camera feeds, runs the EnterpriseInferenceEngine, saves incidents to the database,
and yields multipart MJPEG streaming frames with live HUD telemetry for operator dashboards.
"""

import os
import json
import time
import asyncio
import cv2
import numpy as np
from typing import Generator, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.websocket_manager import ws_manager
from backend.app.db.session import SessionLocal
from backend.app.db.models import Camera, Incident, DispatchAlert, AuditLog
from backend.app.ml.inference_engine import EnterpriseInferenceEngine


class VideoProcessorService:
    def __init__(self):
        self.inference_engine = EnterpriseInferenceEngine()

    def process_camera_stream_generator(
        self,
        camera_id_str: str,
        fps_limit: float = 20.0
    ) -> Generator[bytes, None, None]:
        """
        Yields multipart MJPEG boundary bytes of live annotated video frames.
        Automatically performs accident detection, saves incidents, and emits alerts.
        """
        db: Session = SessionLocal()
        cam = db.query(Camera).filter(Camera.camera_id == camera_id_str).first()
        if not cam:
            video_source = "data/sample_videos/high_speed_collision.mp4"
            camera_meta = {
                "camera_id": camera_id_str,
                "roadway": "Highway 101 Corridor",
                "lat": 37.7749,
                "lon": -122.4194,
                "zone": "Northbound Lane 1"
            }
        else:
            video_source = cam.stream_url or "data/sample_videos/high_speed_collision.mp4"
            camera_meta = {
                "camera_id": cam.camera_id,
                "roadway": cam.roadway,
                "lat": cam.latitude,
                "lon": cam.longitude,
                "zone": cam.zone
            }
        db.close()

        # Load video metadata if available for ground truth vehicle tracks
        meta_path = video_source.replace(".mp4", "_meta.json")
        frame_metadata = []
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta_json = json.load(f)
                frame_metadata = meta_json.get("frames", [])

        # Distinguish between static sample file and live CCTV/RTSP/Webcam stream
        is_live = (
            video_source.startswith("rtsp://")
            or video_source.startswith("http://")
            or video_source.startswith("https://")
            or video_source.isdigit()
        )

        # Set FFMPEG options for low-latency RTSP TCP stream
        if video_source.startswith("rtsp://"):
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

        source_target = int(video_source) if video_source.isdigit() else video_source
        cap = cv2.VideoCapture(source_target)
        if is_live:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_delay = 1.0 / max(1.0, min(fps, fps_limit))

        frame_buffer = []
        raw_buffer = []
        frame_idx = 0
        reported_incident_uuids = set()

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    if is_live:
                        # Attempt live stream reconnect on packet drop
                        time.sleep(1.0)
                        cap.release()
                        cap = cv2.VideoCapture(source_target)
                        continue
                    else:
                        # Loop recorded video continuously for simulation
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        frame_idx = 0
                        frame_buffer.clear()
                        raw_buffer.clear()
                        continue

                detections = []
                if frame_idx < len(frame_metadata):
                    detections = frame_metadata[frame_idx].get("vehicles", [])

                # Run inference engine
                analysis = self.inference_engine.analyze_frame_sequence(
                    frame_bgr=frame,
                    frame_buffer=frame_buffer,
                    raw_buffer=raw_buffer,
                    detections=detections,
                    camera_meta=camera_meta,
                    frame_idx=frame_idx,
                    fps=fps
                )

                # If an accident occurred and hasn't been recorded in this sequence
                if analysis.get("is_accident") and "incident_package" in analysis:
                    pkg = analysis["incident_package"]
                    inc_uuid = pkg["incident_id"]

                    if inc_uuid not in reported_incident_uuids:
                        reported_incident_uuids.add(inc_uuid)
                        # Persist to database
                        db_write: Session = SessionLocal()
                        cam_rec = db_write.query(Camera).filter(Camera.camera_id == camera_id_str).first()
                        if cam_rec:
                            sev = pkg["severity_info"]
                            new_incident = Incident(
                                incident_uuid=inc_uuid,
                                camera_id=cam_rec.id,
                                confidence=analysis["confidence"],
                                severity=sev["severity"],
                                priority=sev["priority"],
                                status="New",
                                vehicles_involved=sev["vehicles_involved"],
                                rollover_detected=sev["rollover_detected"],
                                rationale=sev["evidence_rationale"],
                                multi_cues=analysis["cues"],
                                snapshot_path=pkg["snapshot_path"],
                                video_clip_path=video_source
                            )
                            db_write.add(new_incident)
                            db_write.commit()
                            db_write.refresh(new_incident)

                            # Dispatch automated alerts
                            cad_payload = pkg["cad_payload"]
                            dispatch_record = self.inference_engine.notification_service.dispatch_emergency_alert(cad_payload)
                            for d_item in dispatch_record["dispatches"]:
                                d_alert = DispatchAlert(
                                    incident_id=new_incident.id,
                                    dispatch_uuid=d_item["dispatch_id"],
                                    channel=d_item["channel"],
                                    status=d_item["status"],
                                    recipient=d_item["recipient"],
                                    response_code=d_item["response_code"],
                                    payload=cad_payload
                                )
                                db_write.add(d_alert)

                            audit = AuditLog(
                                incident_id=new_incident.id,
                                operator_id="AUTO_DISPATCH_SYSTEM",
                                action="AUTO_ACCIDENT_DETECTED_AND_DISPATCHED",
                                details=f"Automated incident alert generated with confidence {analysis['confidence']*100:.1f}% ({sev['priority']})"
                            )
                            db_write.add(audit)
                            db_write.commit()

                            # Schedule broadcast on event loop if running
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.run_coroutine_threadsafe(
                                        ws_manager.broadcast_incident({
                                            "incident_uuid": inc_uuid,
                                            "camera_id": camera_id_str,
                                            "severity": sev["severity"],
                                            "priority": sev["priority"],
                                            "confidence": analysis["confidence"],
                                            "timestamp": cad_payload["timestamp"],
                                            "location": cad_payload["location"],
                                            "rationale": sev["evidence_rationale"],
                                            "snapshot_url": cad_payload["evidence"]["snapshot_image_url"]
                                        }),
                                        loop
                                    )
                            except Exception:
                                pass

                        db_write.close()

                # Render live HUD overlay
                annotated_frame = self.inference_engine.render_hud_overlay(
                    frame_bgr=frame,
                    analysis_result=analysis,
                    detections=detections
                )

                # Encode to JPEG
                ret_jpg, jpeg_buf = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ret_jpg:
                    continue

                frame_bytes = jpeg_buf.tobytes()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

                frame_idx += 1
                time.sleep(frame_delay)

        finally:
            cap.release()


video_service = VideoProcessorService()
