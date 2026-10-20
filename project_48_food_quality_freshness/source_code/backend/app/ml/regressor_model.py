import torch
import torch.nn as nn
import torch.nn.functional as F

class ShelfLifeForecastRegressorNet(nn.Module):
    """
    Deep Neural Regressor for perishable food shelf-life forecasting
    and multi-risk estimation from 10 physicochemical and telemetry features:
      1. storage_temp_c
      2. relative_humidity_pct
      3. storage_duration_hours
      4. browning_index
      5. tvbn_mg_per_100g
      6. ph_level
      7. ethylene_concentration_ppm
      8. moisture_content_pct
      9. bacterial_log_cfu_g
      10. reflectance_ratio_650_850
      
    Outputs 4 bounded regression predictions:
      1. remaining_shelf_life_days (0 to 21.0 days)
      2. spoilage_risk_pct (0 to 100.0%)
      3. microbial_risk_pct (0 to 100.0%)
      4. cold_chain_compliance_score (0 to 100.0%)
    """
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
        self.bn2 = nn.BatchNorm1d(hidden_dim * 2)
        self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.bn3 = nn.BatchNorm1d(hidden_dim)
        self.dropout = nn.Dropout(0.1)
        
        self.out_shelf_life = nn.Linear(hidden_dim, 1)
        self.out_spoilage_risk = nn.Linear(hidden_dim, 1)
        self.out_microbial_risk = nn.Linear(hidden_dim, 1)
        self.out_cold_chain = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor):
        h = F.silu(self.bn1(self.fc1(x)))
        h = self.dropout(h)
        h = F.silu(self.bn2(self.fc2(h)))
        h = self.dropout(h)
        h = F.silu(self.bn3(self.fc3(h)))
        
        shelf_life = F.relu(self.out_shelf_life(h)) * 21.0
        spoilage_risk = torch.sigmoid(self.out_spoilage_risk(h)) * 100.0
        microbial_risk = torch.sigmoid(self.out_microbial_risk(h)) * 100.0
        cold_chain = torch.sigmoid(self.out_cold_chain(h)) * 100.0
        
        return torch.cat([shelf_life, spoilage_risk, microbial_risk, cold_chain], dim=1)
