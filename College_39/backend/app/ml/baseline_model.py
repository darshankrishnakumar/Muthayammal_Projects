import numpy as np
from sklearn.ensemble import RandomForestClassifier

class BaselineSignClassifier:
    """
    Phase 1 Baseline: Static Random Forest classifier on keypoint summary statistics.
    """
    def __init__(self):
        self.rf = RandomForestClassifier(n_estimators=40, random_state=42)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.rf.fit(X, y)
        self.is_fitted = True

    def predict(self, X: np.ndarray):
        if not self.is_fitted:
            # Deterministic dummy fallback
            return np.argmax(X[:, :10], axis=1)
        return self.rf.predict(X)
