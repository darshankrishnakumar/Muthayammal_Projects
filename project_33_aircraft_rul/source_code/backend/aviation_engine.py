import os
import json
import torch
import torch.nn as nn
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR = os.path.join(BASE_DIR, "source_code", "backend", "models")

FEATURE_COLS = [
    'cycle_ratio',
    't50_lpt_outlet_temp_r',
    'p30_hpc_pressure_psia',
    'nc_core_speed_rpm',
    'nf_fan_speed_rpm',
    'fuel_flow_ratio_pps_psi',
    'egt_margin_deg_c',
    'vibration_broadband_g'
]

STATUS_LABELS = [
    'AIRWORTHY / OPTIMAL',
    'MAINTENANCE DUE SOON',
    'GROUNDED / MANDATORY SHOP VISIT'
]

COMPONENTS_REGISTRY = {
    'COMP-TURB-01': {
        'id': 'COMP-TURB-01',
        'name': 'High-Pressure Turbine (HPT) Blades',
        'engine_model': 'CFM56-7B / LEAP-1B',
        'max_design_cycles': 4200,
        'nominal_temp_r': 1580,
        'nominal_pres_psia': 550,
        'nominal_core_rpm': 9450,
        'nominal_fan_rpm': 2500,
        'nominal_fuel_ratio': 0.0265,
        'icon': '🔥',
        'failure_mode': 'Thermal Creep & Oxidation Erosion',
        'aliases': ['high-pressure turbine (hpt) blades', 'hpt', 'hpt blades', 'turbine', 'comp-turb-01']
    },
    'COMP-HPC-02': {
        'id': 'COMP-HPC-02',
        'name': 'High-Pressure Compressor (HPC) Rotor',
        'engine_model': 'GE90-115B',
        'max_design_cycles': 6000,
        'nominal_temp_r': 1120,
        'nominal_pres_psia': 480,
        'nominal_core_rpm': 9200,
        'nominal_fan_rpm': 2350,
        'nominal_fuel_ratio': 0.0245,
        'icon': '🌀',
        'failure_mode': 'High-Cycle Fatigue (HCF) Micro-Cracking',
        'aliases': ['high-pressure compressor (hpc) rotor', 'hpc', 'hpc rotor', 'compressor', 'comp-hpc-02']
    },
    'COMP-BRG-03': {
        'id': 'COMP-BRG-03',
        'name': 'Mainshaft Roller Bearings (#4 Bearing)',
        'engine_model': 'Trent 1000',
        'max_design_cycles': 5500,
        'nominal_temp_r': 460,
        'nominal_pres_psia': 45,
        'nominal_core_rpm': 9100,
        'nominal_fan_rpm': 2400,
        'nominal_fuel_ratio': 0.0230,
        'icon': '⚙️',
        'failure_mode': 'Spallation & Subsurface Shear Fatigue',
        'aliases': ['mainshaft roller bearings (#4 bearing)', 'bearing', 'bearings', 'roller bearing', 'comp-brg-03']
    },
    'COMP-FMU-04': {
        'id': 'COMP-FMU-04',
        'name': 'Fuel Metering Unit (FMU)',
        'engine_model': 'PW1100G-JM',
        'max_design_cycles': 8500,
        'nominal_temp_r': 320,
        'nominal_pres_psia': 1200,
        'nominal_core_rpm': 9300,
        'nominal_fan_rpm': 2480,
        'nominal_fuel_ratio': 0.0280,
        'icon': '⛽',
        'failure_mode': 'Servo Valve Sticking & Orifice Wear',
        'aliases': ['fuel metering unit (fmu)', 'fmu', 'fuel unit', 'metering unit', 'comp-fmu-04']
    },
    'COMP-LPT-05': {
        'id': 'COMP-LPT-05',
        'name': 'Low-Pressure Turbine (LPT) Stator',
        'engine_model': 'CF34-8E',
        'max_design_cycles': 7200,
        'nominal_temp_r': 1340,
        'nominal_pres_psia': 180,
        'nominal_core_rpm': 9050,
        'nominal_fan_rpm': 2320,
        'nominal_fuel_ratio': 0.0250,
        'icon': '🛩️',
        'failure_mode': 'Thermal Barrier Coating (TBC) Delamination',
        'aliases': ['low-pressure turbine (lpt) stator', 'lpt', 'lpt stator', 'comp-lpt-05']
    }
}

class ResidualBlock(nn.Module):
    def __init__(self, hidden_dim, dropout=0.15):
        super().__init__()
        self.fc1 = nn.Linear(hidden_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        res = x
        out = self.act(self.bn1(self.fc1(x)))
        out = self.drop(out)
        out = self.bn2(self.fc2(out))
        return self.act(out + res)

class AviationAirworthinessClassifierNet(nn.Module):
    def __init__(self, in_features=8, hidden_dim=64, num_classes=3):
        super().__init__()
        self.in_proj = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.GELU()
        )
        self.block1 = ResidualBlock(hidden_dim, dropout=0.15)
        self.block2 = ResidualBlock(hidden_dim, dropout=0.15)
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.GELU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        h = self.in_proj(x)
        h = self.block1(h)
        h = self.block2(h)
        logits = self.head(h)
        return logits

class TurbofanRULRegressorNet(nn.Module):
    def __init__(self, in_features=8, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 32),
            nn.GELU()
        )
        self.health_head = nn.Sequential(
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.rul_head = nn.Sequential(
            nn.Linear(32, 1),
            nn.Softplus()
        )

    def forward(self, x):
        feat = self.net(x)
        health = self.health_head(feat) * 100.0
        rul_cycles = self.rul_head(feat) * 4500.0
        return health, rul_cycles

class AviationInferenceEngine:
    def __init__(self):
        self.classifier = AviationAirworthinessClassifierNet(in_features=8, hidden_dim=64, num_classes=3)
        self.regressor = TurbofanRULRegressorNet(in_features=8, hidden_dim=64)
        self.scalers = {}
        self.metadata = {}
        self._load_artifacts()

    def _load_artifacts(self):
        cls_weights = os.path.join(MODELS_DIR, "aviation_classifier_weights.pt")
        reg_weights = os.path.join(MODELS_DIR, "turbofan_rul_weights.pt")
        scalers_path = os.path.join(MODELS_DIR, "aviation_scalers.json")
        meta_path = os.path.join(MODELS_DIR, "model_metadata.json")

        if os.path.exists(cls_weights):
            self.classifier.load_state_dict(torch.load(cls_weights, map_location=torch.device('cpu')))
            self.classifier.eval()

        if os.path.exists(reg_weights):
            self.regressor.load_state_dict(torch.load(reg_weights, map_location=torch.device('cpu')))
            self.regressor.eval()

        if os.path.exists(scalers_path):
            with open(scalers_path, "r") as f:
                self.scalers = json.load(f)

        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)

    def resolve_component(self, identifier):
        if not identifier:
            return COMPONENTS_REGISTRY['COMP-TURB-01']
        clean_id = str(identifier).strip().upper()
        if clean_id in COMPONENTS_REGISTRY:
            return COMPONENTS_REGISTRY[clean_id]
        clean_lower = str(identifier).strip().lower()
        for comp in COMPONENTS_REGISTRY.values():
            if clean_lower == comp['name'].lower() or clean_lower in comp['aliases']:
                return comp
        # Default fallback
        return COMPONENTS_REGISTRY['COMP-TURB-01']

    def normalize_features(self, feat_dict):
        vec = []
        for col in FEATURE_COLS:
            val = float(feat_dict.get(col, 0.0))
            if col in self.scalers:
                c_min = self.scalers[col]['min']
                c_max = self.scalers[col]['max']
                norm_val = (val - c_min) / (c_max - c_min + 1e-8)
            else:
                norm_val = 0.5
            vec.append(norm_val)
        return torch.tensor([vec], dtype=torch.float32)

    def predict(self, component_ident, flight_cycles=None, operating_hours=None, scenario='auto'):
        comp = self.resolve_component(component_ident)
        max_cycles = comp['max_design_cycles']

        # Determine flight cycles
        if flight_cycles is not None:
            current_cycles = int(flight_cycles)
        elif operating_hours is not None:
            current_cycles = int(float(operating_hours) / 2.8)
        else:
            if scenario == 'worn':
                current_cycles = int(max_cycles * 0.88)
            elif scenario == 'fresh':
                current_cycles = int(max_cycles * 0.22)
            else:
                current_cycles = int(max_cycles * 0.58)

        current_cycles = max(10, min(int(max_cycles * 1.05), current_cycles))
        current_hours = round(current_cycles * 2.8, 1)

        cycle_ratio = current_cycles / float(max_cycles)
        wear_index = min(1.0, max(0.0, cycle_ratio ** 1.75))

        # Calculate C-MAPSS physical sensor telemetry
        t50 = round(comp['nominal_temp_r'] * (1.0 + wear_index * 0.11), 1)
        p30 = round(comp['nominal_pres_psia'] * (1.0 - wear_index * 0.075), 1)
        nc = round(comp['nominal_core_rpm'] + wear_index * 420.0, 1)
        nf = round(comp['nominal_fan_rpm'], 1)
        fuel_ratio = round(comp['nominal_fuel_ratio'] + wear_index * 0.0055, 5)
        egt_margin = round(85.0 - wear_index * 92.0, 1)
        vib = round(0.35 + (wear_index ** 1.6) * 3.2, 3)

        feat_dict = {
            'cycle_ratio': cycle_ratio,
            't50_lpt_outlet_temp_r': t50,
            'p30_hpc_pressure_psia': p30,
            'nc_core_speed_rpm': nc,
            'nf_fan_speed_rpm': nf,
            'fuel_flow_ratio_pps_psi': fuel_ratio,
            'egt_margin_deg_c': egt_margin,
            'vibration_broadband_g': vib
        }

        # PyTorch model forward pass
        x_tensor = self.normalize_features(feat_dict)

        with torch.no_grad():
            logits = self.classifier(x_tensor)
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()
            pred_idx = int(torch.argmax(logits, dim=-1).item())

            pred_health_t, pred_rul_t = self.regressor(x_tensor)
            health_score = round(float(pred_health_t.squeeze().item()), 1)
            health_score = max(0.0, min(100.0, health_score))
            rul_cycles = max(0, int(round(float(pred_rul_t.squeeze().item()))))
            rul_hours = round(rul_cycles * 2.8, 1)

        status = STATUS_LABELS[pred_idx]

        if pred_idx == 2 or health_score < 30.0:
            status = 'GROUNDED / MANDATORY SHOP VISIT'
            color = '#ef4444'
            action = 'AOG Alert: Immediate engine teardown and non-destructive eddy-current inspection.'
        elif pred_idx == 1 or health_score < 60.0:
            status = 'MAINTENANCE DUE SOON'
            color = '#f59e0b'
            action = 'Schedule borescope inspection within next 75 flight cycles. Monitor EGT margin.'
        else:
            status = 'AIRWORTHY / OPTIMAL'
            color = '#10b981'
            action = 'Normal on-wing operation. Proceed to standard A-check interval.'

        # 11-point degradation curve
        degradation_curve = [
            round(100.0 - ((i / 10.0) ** 1.75) * (100.0 - health_score), 1)
            for i in range(11)
        ]

        return {
            'component_id': comp['id'],
            'component': comp['name'],
            'component_name': comp['name'],
            'engine_model': comp['engine_model'],
            'icon': comp['icon'],
            'flight_cycles_completed': current_cycles,
            'flight_hours_completed': current_hours,
            'max_design_cycles': max_cycles,
            'health_score': health_score,
            'rul_cycles': rul_cycles,
            'rul_flight_hours': rul_hours,
            'airworthiness_status': status,
            'failure_mode': comp['failure_mode'],
            'action_required': action,
            'color': color,
            'status_probabilities': {
                'airworthy_optimal': round(probs[0], 4),
                'maintenance_due_soon': round(probs[1], 4),
                'grounded_mandatory': round(probs[2], 4)
            },
            'cmapss_sensors': feat_dict,
            'degradation_curve': degradation_curve,
            'model': 'PyTorch Residual Airworthiness Net + Dual-Head Turbofan RUL Regressor (NASA C-MAPSS FD001-FD004)'
        }

engine = AviationInferenceEngine()
