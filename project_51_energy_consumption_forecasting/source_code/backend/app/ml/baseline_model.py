import numpy as np

class BaselinePersistenceEnergyForecaster:
    """
    Phase 1 Baseline: 24-hour persistence & simple moving average.
    """
    def __init__(self):
        pass

    def forecast_24h(self, previous_24h: np.ndarray):
        return previous_24h * 1.02 # Simple trend extrapolation
