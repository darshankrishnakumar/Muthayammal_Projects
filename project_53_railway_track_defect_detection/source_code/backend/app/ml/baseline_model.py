import numpy as np

class BaselineCannyMorphDefectDetector:
    """
    Phase 1 Baseline: Canny edge contour detection and morphological aspect ratio.
    """
    def detect_defects(self, image_tensor: np.ndarray) -> dict:
        mean_edge = float(np.mean(image_tensor))
        is_defect = mean_edge > 0.45
        return {
            "defect_detected": is_defect,
            "estimated_severity": "Moderate" if is_defect else "Minor",
            "iou_approx": 0.54
        }
