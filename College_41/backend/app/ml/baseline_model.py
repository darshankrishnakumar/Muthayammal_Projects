import numpy as np

class BaselineColorHistogramGrader:
    """
    Phase 1 Baseline: Color histogram and surface pixel thresholding.
    """
    def __init__(self):
        pass

    def grade(self, img_rgb: np.ndarray):
        # img_rgb (3, 64, 64)
        defect_pixels = np.sum((img_rgb[0] < 0.2) & (img_rgb[1] < 0.2))
        total_pixels = img_rgb[0].size
        pct = (defect_pixels / total_pixels) * 100.0

        if pct < 2.0:
            return "GRADE_A_PREMIUM", "NONE", round(pct, 1), 0.78
        elif pct < 8.0:
            return "GRADE_B_STANDARD", "BRUISE", round(pct, 1), 0.74
        else:
            return "GRADE_C_REJECT", "SKIN_ROT", round(pct, 1), 0.72
