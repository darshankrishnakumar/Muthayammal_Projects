import torch
import torch.nn as nn
import torch.nn.functional as F

class GridPeakAndCarbonEmissionRegressorNet(nn.Module):
    """
    Phase 2 Architecture: Multi-Task Physical Grid Regressor & Sustainability Classifier:
    Processes 12 continuous smart grid & meteorological features:
    (temp, humidity, solar, wind, occupancy, base_load, ev_load, cdd, hdd, tariff, renewable_pct, freq).
    Outputs:
    - forecasted_peak_kwh (kW load)
    - grid_stress_index (0 - 100 scale)
    - carbon_intensity_gco2 (gCO2/kWh)
    - curtailment_risk_prob (0.0 - 1.0)
    - peak_shaving_potential_pct (0.0 - 40.0%)
    """
    def __init__(self, input_dim: int = 12, hidden_dim: int = 128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.ln1 = nn.LayerNorm(hidden_dim)
        self.dropout1 = nn.Dropout(0.15)

        self.fc2 = nn.Linear(hidden_dim, 64)
        self.ln2 = nn.LayerNorm(64)
        self.dropout2 = nn.Dropout(0.10)

        self.fc3 = nn.Linear(64, 32)
        self.ln3 = nn.LayerNorm(32)

        # Multi-task heads
        self.head_peak = nn.Linear(32, 1)          # Peak Demand (kW)
        self.head_stress = nn.Linear(32, 1)        # Grid Stress Index (0-100)
        self.head_carbon = nn.Linear(32, 1)        # Carbon Intensity (gCO2/kWh)
        self.head_curtailment = nn.Linear(32, 1)   # Renewable Curtailment Probability (0-1)
        self.head_shaving = nn.Linear(32, 1)       # Peak Shaving Potential (0-40%)

    def forward(self, x: torch.Tensor):
        h = F.relu(self.ln1(self.fc1(x)))
        h = self.dropout1(h)
        h = F.relu(self.ln2(self.fc2(h)))
        h = self.dropout2(h)
        h = F.relu(self.ln3(self.fc3(h)))

        peak = torch.relu(self.head_peak(h))
        stress = torch.sigmoid(self.head_stress(h)) * 100.0
        carbon = torch.relu(self.head_carbon(h))
        curtailment = torch.sigmoid(self.head_curtailment(h))
        shaving = torch.sigmoid(self.head_shaving(h)) * 40.0

        return {
            "forecasted_peak_kwh": peak,
            "grid_stress_index": stress,
            "carbon_intensity_gco2": carbon,
            "curtailment_risk_prob": curtailment,
            "peak_shaving_potential_pct": shaving
        }
