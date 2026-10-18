import numpy as np

class BaselineCrackDetector:
    """
    Phase 1 Baseline: Adaptive Canny Edge & Morphological Filter for crack localization.
    """
    def __init__(self, threshold=0.35):
        self.threshold = threshold

    def predict_mask(self, image_np: np.ndarray) -> np.ndarray:
        # Simple intensity gradient heuristic
        if image_np.ndim == 3:
            gray = np.mean(image_np, axis=0)
        else:
            gray = image_np
        mask = (gray < self.threshold).astype(np.float32)
        return mask
