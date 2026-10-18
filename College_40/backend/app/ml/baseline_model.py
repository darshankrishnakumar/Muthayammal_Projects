import numpy as np

class BaselineColorFireDetector:
    """
    Phase 1 Baseline: HSV / YCbCr Chromatic rule-based fire & smoke detector.
    """
    def __init__(self, red_threshold=0.6, smoke_diff_threshold=0.2):
        self.red_threshold = red_threshold
        self.smoke_diff_threshold = smoke_diff_threshold

    def detect(self, rgb_image: np.ndarray):
        # Normalized rgb (3, H, W)
        r, g, b = rgb_image[0], rgb_image[1], rgb_image[2]
        flame_pixels = (r > self.red_threshold) & (r > g) & (g > b)
        smoke_pixels = (np.abs(r - g) < self.smoke_diff_threshold) & (np.abs(g - b) < self.smoke_diff_threshold) & (r > 0.4)
        
        has_flame = np.sum(flame_pixels) > 20
        has_smoke = np.sum(smoke_pixels) > 30
        
        if has_flame and has_smoke:
            return "DUAL_HAZARD", 0.75
        elif has_flame:
            return "FLAME", 0.72
        elif has_smoke:
            return "SMOKE", 0.68
        return "NONE", 0.15
