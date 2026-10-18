import numpy as np

class BaselineBlobCrowdCounter:
    """
    Phase 1 Baseline: Connected component blob count and basic pixel density.
    """
    def estimate_count(self, image_tensor: np.ndarray) -> int:
        # Grayscale thresholding estimation
        val = float(np.mean(image_tensor))
        return int(val * 450.0)

    def detect_anomaly(self, count: int, variance: float) -> dict:
        is_anomaly = count > 300 or variance > 0.65
        return {
            "baseline_count": count,
            "anomaly": is_anomaly,
            "risk_score": min(1.0, count / 400.0)
        }
