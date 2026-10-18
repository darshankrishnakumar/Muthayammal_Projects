"""Stage 7: Computer Vision Module - Skin Color Analysis with CIE LAB & YCrCb."""

import os
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np
import config

FACE_CASCADE = None


def get_face_cascade():
    global FACE_CASCADE
    if FACE_CASCADE is None and os.path.exists(config.HAARCASCADE_PATH):
        try:
            FACE_CASCADE = cv2.CascadeClassifier(config.HAARCASCADE_PATH)
        except Exception:
            FACE_CASCADE = None
    return FACE_CASCADE


def analyze_skin_tone_cv(img_bgr: Optional[np.ndarray]) -> Dict[str, Any]:
    """Analyzes approximate skin color and undertone using YCrCb segmentation and CIE LAB color space.

    NOTE: Measurements represent camera-derived geometric approximations.
    They do not infer race, ethnicity, medical traits, or aesthetic quality.
    """
    if img_bgr is None or not isinstance(img_bgr, np.ndarray) or img_bgr.size == 0:
        return {
            "status": "No image supplied",
            "skin_tone": "Medium",
            "undertone": "Warm",
            "L_val": 128.0,
            "b_val": 140.0,
            "confidence": "Low (Default)",
            "warning": "No image loaded. Using default demographic baseline.",
        }

    h, w = img_bgr.shape[:2]
    cascade = get_face_cascade()
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 5) if cascade is not None else []

    # 1. Isolate region of interest (Face or central upper torso)
    if len(faces) > 0:
        x, y, fw, fh = faces[0]
        # Sample forehead/cheeks to exclude lips/eyes/hair
        roi = img_bgr[y + int(0.25 * fh) : y + int(0.65 * fh), x + int(0.25 * fw) : x + int(0.75 * fw)]
        region_type = "Face ROI"
    else:
        # Fallback to central upper-torso region
        roi = img_bgr[int(0.2 * h) : int(0.6 * h), int(0.3 * w) : int(0.7 * w)]
        region_type = "Upper Torso Fallback"

    if roi.size == 0:
        roi = img_bgr

    # 2. YCrCb Skin Candidate Masking
    ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
    # Configurable human skin chrominance threshold
    lower_skin = np.array([0, 133, 77], dtype=np.uint8)
    upper_skin = np.array([255, 173, 127], dtype=np.uint8)
    skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

    skin_pixels = roi[skin_mask > 0]
    if len(skin_pixels) < 50:
        skin_pixels = roi.reshape(-1, 3)
        confidence = "Low (Uniform Lighting)"
    else:
        confidence = "Medium-High"

    mean_bgr = np.mean(skin_pixels, axis=0).astype(np.uint8).reshape(1, 1, 3)
    mean_lab = cv2.cvtColor(mean_bgr, cv2.COLOR_BGR2LAB)[0, 0]

    L = float(mean_lab[0])
    b = float(mean_lab[2])

    # Broad approximate descriptive categories
    if L > 148:
        skin_tone = "Fair"
    elif L > 108:
        skin_tone = "Medium"
    else:
        skin_tone = "Dusky"

    # CIE LAB b-axis undertone approximation
    if b > 142:
        undertone = "Warm"
    elif b < 132:
        undertone = "Cool"
    else:
        undertone = "Neutral"

    return {
        "status": "Success",
        "skin_tone": skin_tone,
        "undertone": undertone,
        "L_val": round(L, 1),
        "b_val": round(b, 1),
        "region_sampled": region_type,
        "confidence": confidence,
        "warning": "Approximate optical measurement subject to camera white balance and lighting.",
    }
