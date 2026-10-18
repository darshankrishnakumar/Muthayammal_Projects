"""Stage 7: Computer Vision Module - Body Proportions & Pose Measurements."""

import os
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np
import config

try:
    from openvino.runtime import Core
    ie = Core()
except Exception:
    ie = None


def load_movenet():
    if ie is not None and os.path.exists(config.OV_MOVENET_PATH):
        try:
            return ie.compile_model(config.OV_MOVENET_PATH, "CPU")
        except Exception:
            return None
    return None


MOVENET_MODEL = load_movenet()


def analyze_body_proportions_cv(
    img_bgr: Optional[np.ndarray],
    manual_ratio: Optional[float] = None,
    manual_shape: Optional[str] = None,
) -> Dict[str, Any]:
    """Estimates visual anatomical proportions (shoulder-to-hip ratio) and body shape styling category.

    IMPORTANT NOTE:
    All measurements are approximate optical ratios (e.g. shoulder/hip).
    They do NOT represent medical diagnoses, exact centimeters, or certified measurements.
    """
    if manual_shape is not None and manual_shape in config.SUPPORTED_BODY_SHAPES:
        return {
            "status": "User Manual Input",
            "body_shape": manual_shape,
            "shoulder_to_hip_ratio": manual_ratio or 1.0,
            "method": "Self-Declared User Profile",
            "is_camera_estimate": False,
        }

    if img_bgr is None or not isinstance(img_bgr, np.ndarray) or img_bgr.size == 0:
        return {
            "status": "No image supplied",
            "body_shape": "Rectangle / Hourglass",
            "shoulder_to_hip_ratio": 1.0,
            "method": "Default Standard",
            "is_camera_estimate": False,
            "disclaimer": "No image loaded. Default styling proportion applied.",
        }

    h, w = img_bgr.shape[:2]
    ratio = 1.0
    method = "Experimental Contour Silhouette"

    # 1. Try MoveNet pose keypoints if model is compiled
    if MOVENET_MODEL is not None:
        try:
            input_tensor = cv2.resize(img_bgr, (256, 256))
            input_tensor = np.expand_dims(input_tensor, axis=0)
            res = MOVENET_MODEL([input_tensor])[MOVENET_MODEL.output(0)]
            # Keypoints: [1, 1, 17, 3] -> (y, x, conf)
            kpts = res[0, 0]
            # Keypoints: 5=L shoulder, 6=R shoulder, 11=L hip, 12=R hip
            s_width = np.linalg.norm(kpts[5, :2] - kpts[6, :2])
            h_width = np.linalg.norm(kpts[11, :2] - kpts[12, :2])
            if h_width > 0.05:
                ratio = float(s_width / h_width)
                method = "MoveNet Anatomical Keypoints"
        except Exception:
            pass

    # 2. Experimental contour fallback
    if method != "MoveNet Anatomical Keypoints":
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(largest)
            # Upper third width vs Lower third width
            upper_slice = thresh[by : by + int(bh * 0.4), bx : bx + bw]
            lower_slice = thresh[by + int(bh * 0.4) : by + int(bh * 0.8), bx : bx + bw]
            w_upper = np.sum(upper_slice > 0) / max(1, upper_slice.shape[0])
            w_lower = np.sum(lower_slice > 0) / max(1, lower_slice.shape[0])
            if w_lower > 0:
                ratio = float(w_upper / w_lower)

    # Classify into broad styling proportion category
    if ratio > 1.15:
        shape = "Inverted Triangle"
    elif ratio < 0.90:
        shape = "Triangle (Pear)"
    else:
        shape = "Rectangle / Hourglass"

    return {
        "status": "Success",
        "body_shape": shape,
        "shoulder_to_hip_ratio": round(ratio, 2),
        "method": method,
        "is_camera_estimate": True,
        "disclaimer": "Ratios represent optical silhouette proportions, not certified centimetre dimensions.",
    }
