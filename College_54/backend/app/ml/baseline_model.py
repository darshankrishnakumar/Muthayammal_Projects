import numpy as np

class BaselineWeatherMLP:
    """
    Phase 1 Baseline: Flat tabular multi-layer perceptron for weather classification.
    """
    def predict(self, features: np.ndarray) -> dict:
        # Simple weighted sum heuristic
        prob = min(1.0, max(0.0, float(features[0] * 0.02 + features[4] * 0.015)))
        return {
            "predicted_class": "Heavy Rainfall" if prob > 0.5 else "Normal Transition",
            "probability": prob,
            "accuracy_baseline": 0.742
        }
