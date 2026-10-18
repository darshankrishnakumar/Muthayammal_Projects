"""
Video Streams and Live Camera Feeds API Endpoints.
Supports listing roadside cameras, adding live CCTV/RTSP streams, testing connections,
streaming real-time annotated MJPEG feeds, and running on-demand accident analysis.
"""

import os
import cv2
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import Camera
from backend.app.services.video_processor import video_service
from backend.app.ml.initial_prototype import InitialPrototypeInference

router = APIRouter()


class VideoAnalysisRequest(BaseModel):
    video_source: str = "data/sample_videos/high_speed_collision.mp4"
    stride: int = 5
    confidence_threshold: float = 0.60


class AddCameraRequest(BaseModel):
    camera_id: str = Field(..., example="CAM-LIVE-INTERSECTION-1")
    name: str = Field(..., example="Downtown Main St & 5th Ave (Live RTSP)")
    stream_url: str = Field(..., example="rtsp://admin:pass@192.168.1.100:554/live")
    roadway: str = Field(default="Main Street Corridor")
    latitude: float = Field(default=37.7749)
    longitude: float = Field(default=-122.4194)
    zone: str = Field(default="Northbound & Southbound Lanes")


class TestStreamRequest(BaseModel):
    stream_url: str = Field(..., example="rtsp://admin:pass@192.168.1.100:554/live")


@router.get("/cameras")
def list_cameras(db: Session = Depends(get_db)):
    cams = db.query(Camera).all()
    results = []
    for c in cams:
        results.append({
            "id": c.id,
            "camera_id": c.camera_id,
            "name": c.name,
            "roadway": c.roadway,
            "stream_url": c.stream_url,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "zone": c.zone,
            "status": c.status,
            "stream_endpoint": f"/api/streams/live/{c.camera_id}"
        })
    return {"count": len(results), "cameras": results}


@router.post("/cameras")
def add_camera(req: AddCameraRequest, db: Session = Depends(get_db)):
    """
    Registers a new live CCTV, RTSP, HTTP, or local USB webcam feed.
    """
    existing = db.query(Camera).filter(Camera.camera_id == req.camera_id).first()
    if existing:
        # Update existing
        existing.name = req.name
        existing.stream_url = req.stream_url
        existing.roadway = req.roadway
        existing.latitude = req.latitude
        existing.longitude = req.longitude
        existing.zone = req.zone
        existing.status = "ONLINE"
        db.commit()
        db.refresh(existing)
        return {"message": "Camera updated successfully", "camera_id": existing.camera_id}

    new_cam = Camera(
        camera_id=req.camera_id,
        name=req.name,
        stream_url=req.stream_url,
        roadway=req.roadway,
        latitude=req.latitude,
        longitude=req.longitude,
        zone=req.zone,
        status="ONLINE"
    )
    db.add(new_cam)
    db.commit()
    db.refresh(new_cam)
    return {
        "message": "Live CCTV camera registered successfully",
        "camera_id": new_cam.camera_id,
        "stream_endpoint": f"/api/streams/live/{new_cam.camera_id}"
    }


@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: str, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(cam)
    db.commit()
    return {"message": f"Camera {camera_id} removed"}


@router.post("/test-connection")
def test_camera_stream_connection(req: TestStreamRequest):
    """
    Performs handshake test against a live RTSP, HTTP, or webcam feed to verify connectivity.
    """
    url = req.stream_url.strip()
    source_target = int(url) if url.isdigit() else url

    if str(url).startswith("rtsp://"):
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

    cap = cv2.VideoCapture(source_target)
    if not cap.isOpened():
        return {
            "connected": False,
            "message": f"Failed to open stream at '{url}'. Ensure camera is online and accessible."
        }

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return {
            "connected": False,
            "message": "Stream opened, but failed to decode a valid frame."
        }

    h, w, _ = frame.shape
    return {
        "connected": True,
        "message": f"Connection verified successfully! Stream resolution: {w}x{h}",
        "resolution": f"{w}x{h}"
    }


@router.get("/live/{camera_id}")
def stream_live_camera(camera_id: str):
    """
    Streams multipart MJPEG video with live HUD telemetry and bounding box overlays.
    """
    return StreamingResponse(
        video_service.process_camera_stream_generator(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/analyze-video")
def analyze_video_feed(req: VideoAnalysisRequest):
    """
    Runs on-demand batch inference on a chosen video file.
    """
    if not os.path.exists(req.video_source):
        raise HTTPException(status_code=404, detail=f"Video file not found: {req.video_source}")

    prototype = InitialPrototypeInference(
        model_weights_path=settings.MODEL_WEIGHTS_PATH
    )
    results = prototype.process_video(
        video_path=req.video_source,
        stride=req.stride,
        confidence_threshold=req.confidence_threshold
    )

    return {
        "status": "COMPLETED",
        "video": req.video_source,
        "total_frames_analyzed": results["total_frames_analyzed"],
        "alerts_triggered": results["alerts_triggered"],
        "high_confidence_alerts": results["high_confidence_alerts"]
    }
