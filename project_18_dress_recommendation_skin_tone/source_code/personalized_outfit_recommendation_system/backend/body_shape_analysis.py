"""Body Shape Analysis Module.

Estimates anatomical proportions and silhouette classification using
OpenVINO MoveNet SinglePose Thunder or OpenCV contour silhouette analysis.

IMPORTANT NOTE:
All image-based measurements are approximate proportional ratios (such as
shoulder-to-hip ratio). They do NOT represent calibrated centimeter dimensions.
"""

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


def load_movenet_ov():
    """Loads OpenVINO MoveNet model if present on disk."""
    if ie is not None and os.path.exists(config.OV_MOVENET_PATH):
        try:
            return ie.compile_model(config.OV_MOVENET_PATH, "CPU")
        except Exception as e:
            print(f"[WARNING] OpenVINO MoveNet loading failed: {e}")
            return None
    return None

_MOVENET_COMPILED = load_movenet_ov()


def run_movenet(img_bgr: np.ndarray) -> Optional[np.ndarray]:
    """Runs MoveNet inference if model is loaded. Returns (17, 3) keypoints [y, x, conf]."""
    if _MOVENET_COMPILED is None:
        return None
    try:
        inp = cv2.resize(img_bgr, (256, 256))
        inp = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB).astype(np.float32)
        inp = np.expand_dims(inp, 0)
        output_layer = _MOVENET_COMPILED.output(0)
        out = _MOVENET_COMPILED([inp])[output_layer]
        return out[0][0]  # shape (17, 3)
    except Exception as e:
        print(f"[WARNING] MoveNet inference failed: {e}")
        return None


def estimate_silhouette_ratio(img_bgr: np.ndarray) -> Tuple[float, Optional[str]]:
    """Fallback silhouette ratio estimation using Otsu thresholding and contour bounds."""
    try:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 1.0, "Could not segment silhouette; default ratio applied."

        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        if h < 50 or w < 20:
            return 1.0, "Detected subject area is too small."

        s_y = int(y + 0.25 * h)
        h_y = int(y + 0.55 * h)

        row_s = np.where(thresh[min(s_y, thresh.shape[0] - 1), :] > 0)[0]
        row_h = np.where(thresh[min(h_y, thresh.shape[0] - 1), :] > 0)[0]

        w_s = (row_s[-1] - row_s[0]) if len(row_s) > 1 else w
        w_h = (row_h[-1] - row_h[0]) if len(row_h) > 1 else w

        ratio = float(w_s) / max(float(w_h), 1.0)
        return float(np.clip(ratio, 0.5, 2.0)), "Silhouette contour analysis used as fallback."
    except Exception:
        return 1.0, "Silhouette estimation failed."


def analyze_body_shape(img_bgr: np.ndarray) -> Dict[str, Any]:
    """Classifies body shape based on anatomical or silhouette shoulder-to-hip ratio.

    Returns:
        dict containing:
        - body_shape: 'Triangle (Pear)' | 'Rectangle / Hourglass' | 'Inverted Triangle' | 'Unknown'
        - shoulder_hip_ratio: float
        - method: 'MoveNet OpenVINO' | 'Contour Silhouette' | 'Default'
        - warning: Optional[str]
        - is_calibrated_cm: False
    """
    if img_bgr is None or img_bgr.size == 0:
        return {
            "body_shape": "Unknown",
            "shoulder_hip_ratio": 1.0,
            "method": "None",
            "warning": "No image provided.",
            "is_calibrated_cm": False,
        }

    kp = run_movenet(img_bgr)
    warning = None
    method = "Contour Silhouette"

    if kp is not None:
        # MoveNet keypoints: 5=L Shoulder, 6=R Shoulder, 11=L Hip, 12=R Hip
        # Each is [y, x, conf]
        conf_s5, conf_s6 = kp[5][2], kp[6][2]
        conf_h11, conf_h12 = kp[11][2], kp[12][2]

        min_conf = min(conf_s5, conf_s6, conf_h11, conf_h12)
        if min_conf < 0.25:
            warning = f"Low pose landmark confidence ({min_conf:.2f}); pose may be obscured."

        def dist(i, j):
            return np.linalg.norm([kp[j][1] - kp[i][1], kp[j][0] - kp[i][0]])

        shoulder_width = dist(5, 6)
        hip_width = dist(11, 12)
        torso_length = (dist(5, 11) + dist(6, 12)) / 2.0
        if torso_length < 1e-4:
            torso_length = 1.0

        shoulder_norm = shoulder_width / torso_length
        hip_norm = hip_width / torso_length
        ratio = float(shoulder_norm / max(hip_norm, 1e-4))
        method = "MoveNet OpenVINO"
    else:
        ratio, warning = estimate_silhouette_ratio(img_bgr)

    # Classify body type
    if ratio < 0.90:
        shape = "Triangle (Pear)"
    elif ratio <= 1.12:
        shape = "Rectangle / Hourglass"
    else:
        shape = "Inverted Triangle"

    return {
        "body_shape": shape,
        "shoulder_hip_ratio": round(float(ratio), 3),
        "method": method,
        "warning": warning,
        "is_calibrated_cm": False,
        "disclaimer": (
            "Proportion estimate only. Landmark and silhouette ratios describe "
            "visual silhouette proportions, NOT exact physical centimeter measurements."
        ),
    }
