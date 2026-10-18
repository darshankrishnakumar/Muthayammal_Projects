import numpy as np

class BaselineELADetector:
    """
    Phase 1 Baseline: Error Level Analysis (ELA) pixel difference thresholding.
    """
    def __init__(self, threshold=0.15):
        self.threshold = threshold

    def detect_tampering(self, img_np: np.ndarray):
        # ELA simulated residual
        diff = np.abs(img_np - np.mean(img_np, axis=(1,2), keepdims=True))
        ela_score = float(np.mean(diff > self.threshold))
        is_forged = ela_score > 0.05
        return {
            "verdict": "FORGED" if is_forged else "AUTHENTIC",
            "forgery_probability": round(float(np.clip(ela_score * 8.0, 0.05, 0.95)), 3),
            "tampered_area_pct": round(ela_score * 100.0, 2)
        }
