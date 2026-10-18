import numpy as np

class BaselineFacialCountEngagement:
    """
    Phase 1 Baseline: Simple face count and eye blink frequency ratio.
    """
    def __init__(self):
        pass

    def estimate(self, detected_faces: int, total_students: int, blink_rate: float):
        ratio = detected_faces / max(1, total_students)
        score = min(100.0, ratio * 85.0 + (1.0 - blink_rate) * 15.0)
        return {
            "engagement_score": round(score, 1),
            "state": "ENGAGED" if score > 70.0 else "DISENGAGED"
        }
