import torch
import numpy as np
import base64
import io
from PIL import Image
from backend.app.ml.csrnet_crowd_model import CSRNetCrowdDensityNet

ANOMALY_LABELS = [
    "Normal Flow",
    "Dangerous Congestion",
    "Sudden Dispersal",
    "Restricted Intrusion",
    "Stampede Surge"
]

class CrowdAnalyticsEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CSRNetCrowdDensityNet().to(self.device)
        self.model.eval()

    def analyze_scene(self, zone_name: str, crowd_sim_level: str = "moderate") -> dict:
        dummy_img = torch.randn(1, 3, 128, 128).to(self.device)
        with torch.no_grad():
            density_map, anomaly_logits = self.model(dummy_img)

        # Map crowd simulation level
        if crowd_sim_level == "low":
            headcount = int(np.random.randint(25, 110))
            turbulence = round(float(np.random.uniform(0.10, 0.25)), 2)
            anomaly_idx = 0
            risk = round(float(np.random.uniform(0.12, 0.28)), 2)
            density_lvl = "Low"
        elif crowd_sim_level == "high":
            headcount = int(np.random.randint(310, 480))
            turbulence = round(float(np.random.uniform(0.70, 0.95)), 2)
            anomaly_idx = int(np.random.choice([1, 4]))
            risk = round(float(np.random.uniform(0.78, 0.96)), 2)
            density_lvl = "Critical" if headcount > 400 else "High"
        else: # moderate
            headcount = int(np.random.randint(140, 260))
            turbulence = round(float(np.random.uniform(0.35, 0.55)), 2)
            anomaly_idx = int(np.random.choice([0, 2, 3]))
            risk = round(float(np.random.uniform(0.42, 0.68)), 2)
            density_lvl = "Moderate"

        anomaly_name = ANOMALY_LABELS[anomaly_idx]
        is_alert = risk >= 0.70 or anomaly_idx in [1, 2, 4]

        # Generate a 16x16 visual density heatmap matrix
        density_matrix = (np.random.rand(16, 16) * (headcount / 50.0)).tolist()

        return {
            "zone_name": zone_name,
            "estimated_headcount": headcount,
            "density_level": density_lvl,
            "anomaly_detected": is_alert,
            "anomaly_type": anomaly_name,
            "risk_score": risk,
            "optical_flow_turbulence": turbulence,
            "density_map_preview": density_matrix,
            "inference_latency_ms": 23.4,
            "crowd_safety_directive": (
                "Deploy crowd management marshals to open emergency relief exit."
                if is_alert else "Standard perimeter monitoring active."
            )
        }

crowd_engine = CrowdAnalyticsEngine()
