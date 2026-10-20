import torch
import torch.nn as nn
import torch.nn.functional as F

class ClinicalComorbidityForecastNet(nn.Module):
    """
    Deep Neural Prognostic Regressor for chronic disease comorbidity trajectories
    and longitudinal outcomes from 14 integrated biomarkers and disease risks:
      Inputs (14-D):
        1. age (years)
        2. systolic_bp (mmHg)
        3. diastolic_bp (mmHg)
        4. hba1c (%)
        5. fasting_glucose (mg/dL)
        6. total_cholesterol (mg/dL)
        7. hdl_cholesterol (mg/dL)
        8. ldl_cholesterol (mg/dL)
        9. egfr (mL/min/1.73m^2)
        10. bmi (kg/m^2)
        11. cvd_risk_pct
        12. t2d_risk_pct
        13. htn_risk_pct
        14. ckd_risk_pct
        
      Outputs (4-D Bounded Clinical Forecasts):
        1. ten_year_mortality_risk_pct (0 to 100%)
        2. hospital_readmission_risk_pct (0 to 100%)
        3. polypharmacy_complexity_index (0 to 100%)
        4. renal_progression_hazard_pct (0 to 100%)
    """
    def __init__(self, input_dim: int = 14, hidden_dim: int = 64):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
        self.bn2 = nn.BatchNorm1d(hidden_dim * 2)
        self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.bn3 = nn.BatchNorm1d(hidden_dim)
        self.dropout = nn.Dropout(0.1)
        
        self.out_mortality = nn.Linear(hidden_dim, 1)
        self.out_readmission = nn.Linear(hidden_dim, 1)
        self.out_polypharmacy = nn.Linear(hidden_dim, 1)
        self.out_renal = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor):
        h = F.silu(self.bn1(self.fc1(x)))
        h = self.dropout(h)
        h = F.silu(self.bn2(self.fc2(h)))
        h = self.dropout(h)
        h = F.silu(self.bn3(self.fc3(h)))
        
        mortality = torch.sigmoid(self.out_mortality(h)) * 100.0
        readmission = torch.sigmoid(self.out_readmission(h)) * 100.0
        polypharmacy = torch.sigmoid(self.out_polypharmacy(h)) * 100.0
        renal = torch.sigmoid(self.out_renal(h)) * 100.0
        
        return torch.cat([mortality, readmission, polypharmacy, renal], dim=1)
