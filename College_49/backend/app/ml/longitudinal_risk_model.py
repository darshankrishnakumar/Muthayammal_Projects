import torch
import torch.nn as nn
import torch.nn.functional as F

class LongitudinalHealthRiskNet(nn.Module):
    """
    Phase 2 Architecture: Multi-Condition Temporal Longitudinal Risk Network:
    Ingests 10 longitudinal physiological biomarkers:
    [Age, SBP, DBP, HbA1c, Fasting Glucose, Total Cholesterol, HDL, LDL, eGFR, BMI]
    Predicts calibrated risk probabilities across 4 chronic diseases:
    1. Cardiovascular Disease (CVD)
    2. Type 2 Diabetes (T2D)
    3. Hypertension (HTN)
    4. Chronic Kidney Disease (CKD)
    """
    def __init__(self, in_features=10):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU()
        )
        self.cvd_head = nn.Linear(32, 1)
        self.t2d_head = nn.Linear(32, 1)
        self.htn_head = nn.Linear(32, 1)
        self.ckd_head = nn.Linear(32, 1)

    def forward(self, x):
        h = self.encoder(x)
        cvd = torch.sigmoid(self.cvd_head(h)) * 100.0
        t2d = torch.sigmoid(self.t2d_head(h)) * 100.0
        htn = torch.sigmoid(self.htn_head(h)) * 100.0
        ckd = torch.sigmoid(self.ckd_head(h)) * 100.0
        return cvd, t2d, htn, ckd
