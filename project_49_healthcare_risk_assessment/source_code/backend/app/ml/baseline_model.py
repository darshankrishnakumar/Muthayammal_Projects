import numpy as np

class BaselineFraminghamRiskScorer:
    """
    Phase 1 Baseline: Heuristic Framingham risk point system.
    """
    def __init__(self):
        pass

    def evaluate(self, age: int, systolic_bp: float, hba1c: float, ldl: float):
        score = (age * 0.5) + (systolic_bp - 100.0) * 0.4 + (hba1c * 5.0) + (ldl * 0.1)
        prob = float(np.clip(score / 1.5, 10.0, 95.0))
        return {
            "cardio_risk_pct": round(prob, 1),
            "tier": "HIGH" if prob > 65.0 else ("MODERATE" if prob > 35.0 else "LOW")
        }
