import numpy as np

class BaselineColorDeltaGrader:
    """
    Phase 1 Baseline: RGB to HSV color thresholding & mean luminance decay.
    """
    def __init__(self):
        pass

    def inspect(self, img_rgb: np.ndarray):
        # Brown / oxidized pixel ratio
        brown_pixels = (img_rgb[0] > 0.4) & (img_rgb[1] < 0.3) & (img_rgb[2] < 0.2)
        ratio = float(np.mean(brown_pixels))
        score = float(np.clip(100.0 - ratio * 200.0, 10.0, 98.0))
        return {
            "freshness_score": round(score, 1),
            "stage": "FRESH" if score > 75.0 else ("MARGINAL" if score > 50.0 else "DETERIORATED")
        }
