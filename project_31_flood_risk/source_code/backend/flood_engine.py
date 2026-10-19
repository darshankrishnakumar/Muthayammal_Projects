"""
Urban Flood Risk Prediction & Early Warning System
Real-Time PyTorch Inference Engine with Dual Neural Networks:
1. FloodRiskClassifierNet: 4-Tier Alert Severity (NORMAL, ADVISORY, WARNING, CRITICAL)
2. InundationDepthRegressorNet: Inundation Depth (m) & Flood Peak Lead-Time (hours)
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
try:
    from .database import save_prediction, get_zones
except ImportError:
    from database import save_prediction, get_zones

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

BASIN_DEFAULTS = {
    'Riverside Embankment District': {
        'id': 'BASIN-01',
        'type': 'River Basin',
        'dem_elevation_m': 6.5,
        'river_threshold_m': 6.0,
        'drainage_capacity': 'Medium',
        'drainage_score': 2.0,
        'population_density': 18500,
        'icon': '🌊'
    },
    'Bay Coastal Lowlands': {
        'id': 'BASIN-02',
        'type': 'Tidal Estuary',
        'dem_elevation_m': 3.2,
        'river_threshold_m': 4.5,
        'drainage_capacity': 'Low',
        'drainage_score': 1.0,
        'population_density': 24000,
        'icon': '🏖️'
    },
    'Downtown Metropolitan Core': {
        'id': 'BASIN-03',
        'type': 'Urban Concrete Basin',
        'dem_elevation_m': 14.0,
        'river_threshold_m': 8.5,
        'drainage_capacity': 'High',
        'drainage_score': 3.0,
        'population_density': 42000,
        'icon': '🏙️'
    },
    'Industrial Valley Sector': {
        'id': 'BASIN-04',
        'type': 'Alluvial Flood Plain',
        'dem_elevation_m': 11.0,
        'river_threshold_m': 7.0,
        'drainage_capacity': 'Medium',
        'drainage_score': 2.0,
        'population_density': 8500,
        'icon': '🏭'
    },
    'Upland Ridge Buffer': {
        'id': 'BASIN-05',
        'type': 'Highland Plateau',
        'dem_elevation_m': 85.0,
        'river_threshold_m': 14.0,
        'drainage_capacity': 'Optimal',
        'drainage_score': 4.0,
        'population_density': 5200,
        'icon': '⛰️'
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# PyTorch Architectures
# ─────────────────────────────────────────────────────────────────────────────

class FloodRiskClassifierNet(nn.Module):
    """Deep Residual MLP for 4-Class Flood Severity Alert Level"""
    def __init__(self, in_features=8, num_classes=4):
        super().__init__()
        self.input_layer = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.15)
        )
        self.res_block = nn.Sequential(
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 64),
            nn.BatchNorm1d(64)
        )
        self.head = nn.Sequential(
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        h = self.input_layer(x)
        res = self.res_block(h)
        out = self.head(h + res)
        return out


class InundationDepthRegressorNet(nn.Module):
    """Physical Inundation Depth (meters) & Flood Crest Lead Time (hours) Regressor"""
    def __init__(self, in_features=8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        raw = self.net(x)
        depth = torch.nn.functional.softplus(raw[:, 0:1])
        lead_time = torch.nn.functional.softplus(raw[:, 1:2]) + 1.0
        return torch.cat([depth, lead_time], dim=1)


class FloodInferenceEngine:
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.scalers = None
        self._load_artifacts()

    def _load_artifacts(self):
        scalers_path = os.path.join(BASE_DIR, 'hydro_scalers.json')
        cls_weights = os.path.join(BASE_DIR, 'flood_risk_classifier_weights.pt')
        reg_weights = os.path.join(BASE_DIR, 'inundation_regressor_weights.pt')

        if os.path.exists(scalers_path):
            with open(scalers_path, 'r') as f:
                self.scalers = json.load(f)

        if os.path.exists(cls_weights):
            self.classifier = FloodRiskClassifierNet(in_features=8, num_classes=4)
            self.classifier.load_state_dict(torch.load(cls_weights, map_location=torch.device('cpu')))
            self.classifier.eval()

        if os.path.exists(reg_weights):
            self.regressor = InundationDepthRegressorNet(in_features=8)
            self.regressor.load_state_dict(torch.load(reg_weights, map_location=torch.device('cpu')))
            self.regressor.eval()

    def get_basin_info(self, zone_name):
        return BASIN_DEFAULTS.get(zone_name, BASIN_DEFAULTS['Riverside Embankment District'])

    def predict(self, zone_name, params=None, persist=True):
        if not params:
            params = {}

        basin = self.get_basin_info(zone_name)
        dem = basin['dem_elevation_m']
        thresh = basin['river_threshold_m']
        drain_score = basin['drainage_score']

        # Extract features with robust fallbacks
        rainfall = float(params.get('rainfall_mm', params.get('rainfall', 65.0)))
        river_stage = float(params.get('river_level_m', params.get('river_stage_m', thresh * 0.75)))
        soil_m = float(params.get('soil_moisture', 0.65))
        if soil_m > 1.0:  # If passed as percentage (e.g., 85.0)
            soil_m = soil_m / 100.0
        soil_m = max(0.05, min(1.0, soil_m))

        storm_surge = float(params.get('storm_surge_m', params.get('storm_surge', 0.4)))
        crest_ratio = river_stage / max(0.1, thresh)

        features = [
            rainfall,
            river_stage,
            thresh,
            soil_m,
            storm_surge,
            dem,
            drain_score,
            crest_ratio
        ]

        if self.classifier is not None and self.regressor is not None and self.scalers is not None:
            means = np.array(self.scalers['means'], dtype=np.float32)
            stds = np.array(self.scalers['stds'], dtype=np.float32)
            feat_arr = np.array([features], dtype=np.float32)
            feat_norm = (feat_arr - means) / stds

            x_tensor = torch.tensor(feat_norm)
            with torch.no_grad():
                logits = self.classifier(x_tensor)
                probs = torch.softmax(logits, dim=1).numpy()[0]
                pred_idx = int(np.argmax(probs))
                alert_level = self.scalers['alert_levels'][pred_idx]

                reg_out = self.regressor(x_tensor).numpy()[0]
                pred_depth = float(reg_out[0])
                pred_lead_time = float(reg_out[1])

            # Inundation depth logic: if NORMAL, suppress surface water depth to 0
            if alert_level == 'NORMAL':
                inundation_depth = 0.0
            elif alert_level == 'ADVISORY':
                inundation_depth = round(min(pred_depth, 0.15), 2)
            else:
                inundation_depth = round(max(0.2, pred_depth), 2)

            # Risk percentage aligned with physical alert severity tier
            tier_bases = {
                'NORMAL': (0.08, 0.30),
                'ADVISORY': (0.35, 0.55),
                'WARNING': (0.60, 0.78),
                'CRITICAL': (0.82, 0.98)
            }
            min_base, max_base = tier_bases[alert_level]
            soft_score = float((probs[1] * 0.35) + (probs[2] * 0.65) + (probs[3] * 1.00))
            risk_score = round(max(min_base, min(max_base, soft_score if alert_level != 'CRITICAL' else max(min_base, soft_score))), 3)
            risk_pct = round(risk_score * 100, 1)
            lead_time_hours = round(max(1.0, pred_lead_time), 1)

        else:
            # Fallback heuristic if models not found
            rain_weight = (rainfall / 250.0) * 0.35
            river_weight = crest_ratio * 0.35
            soil_weight = soil_m * 0.20
            elevation_penalty = max(0.0, (20.0 - dem) / 20.0) * 0.10
            raw_score = rain_weight + river_weight + soil_weight + elevation_penalty
            risk_score = round(max(0.05, min(0.99, raw_score)), 3)
            risk_pct = round(risk_score * 100, 1)
            if risk_score >= 0.75:
                alert_level = 'CRITICAL'
                inundation_depth = round(max(0.8, (risk_score - 0.7) * 4.0), 2)
                lead_time_hours = 2.0
            elif risk_score >= 0.55:
                alert_level = 'WARNING'
                inundation_depth = round(max(0.2, (risk_score - 0.5) * 2.0), 2)
                lead_time_hours = 5.0
            elif risk_score >= 0.35:
                alert_level = 'ADVISORY'
                inundation_depth = 0.0
                lead_time_hours = 10.0
            else:
                alert_level = 'NORMAL'
                inundation_depth = 0.0
                lead_time_hours = 20.0

        # Alert configuration
        if alert_level == 'CRITICAL':
            alert_title = '🔴 RED ALERT: Severe Inundation Imminent'
            protocol = 'Mandatory evacuation of ground floors. Deploy flood gates & high-capacity pumps.'
            color = '#ef4444'
        elif alert_level == 'WARNING':
            alert_title = '🟠 ORANGE WARNING: Flash Flood Watch'
            protocol = 'Prepare emergency relief teams, move vehicles to high ground, seal storm drains.'
            color = '#f97316'
        elif alert_level == 'ADVISORY':
            alert_title = '🟡 YELLOW ADVISORY: Elevated Water Level'
            protocol = 'Monitor upstream river gauges and clear municipal drainage grates.'
            color = '#eab308'
        else:
            alert_level = 'NORMAL'
            alert_title = '🟢 GREEN: Hydrological Equilibrium'
            protocol = 'All reservoirs and runoff channels operating within normal safety limits.'
            color = '#10b981'

        pop_at_risk = int(basin['population_density'] * (risk_score if risk_score > 0.4 else 0))

        result = {
            'zone': zone_name,
            'zone_type': basin['type'],
            'icon': basin['icon'],
            'elevation_m': dem,
            'risk_score': risk_score,
            'risk_pct': risk_pct,
            'alert_level': alert_level,
            'alert_title': alert_title,
            'emergency_protocol': protocol,
            'color': color,
            'inundation_depth_m': inundation_depth,
            'lead_time_hours': lead_time_hours,
            'telemetry': {
                'rainfall_mm': round(rainfall, 1),
                'river_stage_m': round(river_stage, 2),
                'river_threshold_m': thresh,
                'soil_saturation_pct': round(soil_m * 100, 1),
                'storm_surge_m': round(storm_surge, 2),
                'population_at_risk': pop_at_risk
            },
            'model': 'PyTorch Residual FloodNet + Inundation Regressor'
        }

        if persist:
            record_id = save_prediction(result)
            result['id'] = record_id

        return result

# Global singleton
flood_engine = FloodInferenceEngine()
