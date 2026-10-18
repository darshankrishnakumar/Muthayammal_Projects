"""Skin Tone and Undertone Analysis Module.

Uses OpenCV Haar Cascade face detection, YCrCb color space segmentation,
and CIE LAB color analysis to estimate skin tone and undertone.
"""

import os
from typing import Dict, Tuple, Optional
import cv2
import numpy as np
import config


def get_face_cascade() -> Optional[cv2.CascadeClassifier]:
    """Loads Haar Cascade classifier from local file or OpenCV data path."""
    cascade_paths = [
        config.HAARCASCADE_PATH,
        os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"),
    ]
    for p in cascade_paths:
        if os.path.exists(p):
            detector = cv2.CascadeClassifier(p)
            if not detector.empty():
                return detector
    return None


def analyze_skin_tone(
    img_bgr: np.ndarray,
) -> Dict[str, any]:
    """Analyzes an input BGR image to estimate skin tone, undertone, and average skin color.

    Returns:
        dict containing:
        - skin_tone: 'Fair' | 'Medium/Wheatish' | 'Dusky/Dark' | 'Unknown'
        - undertone: 'Warm' | 'Cool' | 'Neutral' | 'Unknown'
        - avg_color_bgr: (b, g, r)
        - confidence_warning: Optional[str]
        - face_detected: bool
    """
    if img_bgr is None or img_bgr.size == 0:
        return {
            "skin_tone": "Unknown",
            "undertone": "Unknown",
            "avg_color_bgr": (0, 0, 0),
            "confidence_warning": "No image provided.",
            "face_detected": False,
        }

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    detector = get_face_cascade()
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    face_detected = False
    warning = None

    if detector is not None and not detector.empty():
        faces = detector.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=4, minSize=(60, 60))
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = img_rgb[y:y + h, x:x + w]
            face_detected = True
        else:
            # Fallback to upper 30% of full-body photo
            h_tot = img_rgb.shape[0]
            face = img_rgb[:max(int(h_tot * 0.35), 50), :]
            warning = "Face not clearly detected; sampled upper torso region as fallback."
    else:
        h_tot = img_rgb.shape[0]
        face = img_rgb[:max(int(h_tot * 0.35), 50), :]
        warning = "Face detection model unavailable; estimated from upper image region."

    # Resize crop for standardized sampling
    face = cv2.resize(face, (300, 300))
    ycrcb = cv2.cvtColor(face, cv2.COLOR_RGB2YCrCb)

    # Standard empirical skin threshold in YCrCb
    mask = cv2.inRange(
        ycrcb,
        np.array([0, 133, 77], dtype=np.uint8),
        np.array([255, 173, 127], dtype=np.uint8),
    )

    pixels = face[mask > 0]
    if len(pixels) < 100:
        # Fallback to central region if mask too sparse
        central = face[75:225, 75:225]
        pixels = central.reshape(-1, 3)
        warning = (warning + " • " if warning else "") + "Sparse skin pixels; lighting may be dim or shadowed."

    if len(pixels) == 0:
        return {
            "skin_tone": "Unknown",
            "undertone": "Unknown",
            "avg_color_bgr": (128, 128, 128),
            "confidence_warning": "Could not segment skin pixels from image.",
            "face_detected": face_detected,
        }

    avg_rgb = np.mean(pixels, axis=0).astype(np.uint8)
    avg_bgr = (int(avg_rgb[2]), int(avg_rgb[1]), int(avg_rgb[0]))

    # Convert average color to CIE LAB space
    lab = cv2.cvtColor(np.uint8([[avg_rgb]]), cv2.COLOR_RGB2LAB)[0][0]
    L, A, B = int(lab[0]), int(lab[1]), int(lab[2])

    # Tone classification (L channel: Luminance)
    if L > 148:
        tone = "Fair"
    elif L > 108:
        tone = "Medium/Wheatish"
    else:
        tone = "Dusky/Dark"

    # Undertone classification (B channel: Blue-Yellow axis)
    if B > 148:
        undertone = "Warm"
    elif B < 132:
        undertone = "Cool"
    else:
        undertone = "Neutral"

    return {
        "skin_tone": tone,
        "undertone": undertone,
        "avg_color_bgr": avg_bgr,
        "confidence_warning": warning,
        "face_detected": face_detected,
        "lab_values": {"L": L, "A": A, "B": B},
    }
