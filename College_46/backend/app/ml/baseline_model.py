import numpy as np

class BaselineTemplateDiffDetector:
    """
    Phase 1 Baseline: Golden template difference and Otsu thresholding.
    """
    def __init__(self, diff_threshold=0.25):
        self.diff_threshold = diff_threshold

    def inspect(self, part_img: np.ndarray, golden_template: np.ndarray = None):
        if golden_template is None:
            golden_template = np.full_like(part_img, 0.5)
        diff = np.abs(part_img - golden_template)
        defect_pixels = np.sum(diff > self.diff_threshold)
        total = part_img.size
        pct = (defect_pixels / total) * 100.0
        is_def = pct > 2.0
        return {
            "verdict": "REJECT" if is_def else "PASS",
            "defect_area_pct": round(pct, 2),
            "severity_score": round(min(100.0, pct * 8.0), 1)
        }
