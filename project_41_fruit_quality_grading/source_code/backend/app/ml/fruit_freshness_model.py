import torch
import torch.nn as nn

class FruitFreshnessShelfLifeRegressorNet(nn.Module):
    """
    Multi-Target Neural Regressor predicting:
    - Fruit Flesh Penetrometer Firmness (Newtons) [10.0 to 95.0 N]
    - Soluble Solids Sugar Content (Brix %) [7.0 to 22.0 Brix]
    - Marketable Shelf Life Remaining (Days) [0.5 to 30.0 Days]
    - Batch Economic Quality Index (0.0 to 100.0 Points)
    """
    def __init__(self, in_features=10):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.10)
        )
        self.firmness_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.sugar_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.shelf_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.economic_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        h = self.trunk(x)
        # Scaled physical outputs
        firmness_n = 10.0 + self.firmness_head(h) * 85.0       # [10.0, 95.0] N
        sugar_brix = 7.0 + self.sugar_head(h) * 15.0          # [7.0, 22.0] Brix
        shelf_life_days = 0.5 + self.shelf_head(h) * 29.5     # [0.5, 30.0] Days
        economic_index = self.economic_head(h) * 100.0        # [0.0, 100.0] Points
        return firmness_n, sugar_brix, shelf_life_days, economic_index
