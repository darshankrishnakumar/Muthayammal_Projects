import torch
import torch.nn as nn

class RadarPrecipitationAndExtremeWeatherRegressorNet(nn.Module):
    """
    Model 2: Deep Multi-Task Radar Precipitation & Extreme Weather Regressor.
    Ingests 12-dimensional atmospheric telemetry and radar features:
    [Temperature, Barometric Pressure, Wind Speed, Relative Humidity, Radar Reflectivity,
     Dew Point, Solar Irradiance, CAPE Convective Energy, Lifted Index, Wind Gust Velocity,
     Precipitable Water PWAT, Station Elevation].
    Predicts Precipitation Rate (mm/h), CAPE (J/kg), Wind Gust (km/h), Severe Storm Risk (0.0-1.0),
    and 3-class alert severity classification (Minor, Severe, Extreme).
    """
    def __init__(self, input_dim: int = 12):
        super().__init__()
        self.feature_net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.15),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.10),
            nn.Linear(64, 32),
            nn.ReLU(inplace=True)
        )
        self.head_precip = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_cape = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_gust = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_risk = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.head_severity = nn.Linear(32, 3) # Minor, Severe, Extreme

    def forward(self, x: torch.Tensor):
        feat = self.feature_net(x)
        precip = self.head_precip(feat) * 150.0 # 0-150 mm/h precipitation rate
        cape = self.head_cape(feat) * 5000.0   # 0-5000 J/kg CAPE
        gust = self.head_gust(feat) * 180.0    # 0-180 km/h wind gust
        risk = self.head_risk(feat)            # 0.0 - 1.0 probability
        severity_logits = self.head_severity(feat)
        return {
            "precipitation_rate_mmh": precip,
            "cape_joules": cape,
            "wind_gust_kmh": gust,
            "severe_weather_risk": risk,
            "severity_logits": severity_logits
        }
