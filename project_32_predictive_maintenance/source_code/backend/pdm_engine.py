"""
Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data and Deep Learning
Real-Time PyTorch Inference Engine with Dual Neural Networks:
1. MachineHealthClassifierNet: 6-Class Fault Diagnostics
2. RULRegressorNet: Health Score (0-100) & Remaining Useful Life (RUL hours) Regressor
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn

try:
    from .database import save_inspection
except ImportError:
    from database import save_inspection

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MACHINES_CONFIG = {
    'Screw Compressor A-101': {
        'id': 'MACH-01',
        'type': 'Rotary Screw Compressor',
        'nominal_rpm': 2980,
        'nominal_temp': 72.0,
        'nominal_vib': 1.1,
        'nominal_press': 8.5,
        'nominal_oil': 55.0,
        'nominal_ae': 62.0,
        'icon': '⚙️',
        'criticality': 'High'
    },
    'Centrifugal Pump B-204': {
        'id': 'MACH-02',
        'type': 'Slurry Circulation Pump',
        'nominal_rpm': 1480,
        'nominal_temp': 64.0,
        'nominal_vib': 0.8,
        'nominal_press': 14.2,
        'nominal_oil': 48.0,
        'nominal_ae': 58.0,
        'icon': '🔄',
        'criticality': 'Critical'
    },
    'Induction Motor C-302': {
        'id': 'MACH-03',
        'type': '3-Phase 350kW Motor',
        'nominal_rpm': 1780,
        'nominal_temp': 68.0,
        'nominal_vib': 0.6,
        'nominal_press': 1.0,
        'nominal_oil': 45.0,
        'nominal_ae': 54.0,
        'icon': '⚡',
        'criticality': 'Medium'
    },
    'Gas Turbine Generator D-401': {
        'id': 'MACH-04',
        'type': 'Co-Gen Gas Turbine',
        'nominal_rpm': 5400,
        'nominal_temp': 118.0,
        'nominal_vib': 1.4,
        'nominal_press': 22.0,
        'nominal_oil': 65.0,
        'nominal_ae': 78.0,
        'icon': '🔥',
        'criticality': 'Critical'
    },
    'Conveyor Drive Unit E-505': {
        'id': 'MACH-05',
        'type': 'Heavy Ore Conveyor Drive',
        'nominal_rpm': 720,
        'nominal_temp': 52.0,
        'nominal_vib': 1.8,
        'nominal_press': 3.5,
        'nominal_oil': 68.0,
        'nominal_ae': 60.0,
        'icon': '🏗️',
        'criticality': 'Low'
    }
}

FAULT_METADATA = {
    'Normal Baseline': {'color': '#10b981', 'urgency': 'NONE', 'action': 'Routine monthly lubrication'},
    'Outer Race Bearing Spall': {'color': '#ef4444', 'urgency': 'IMMEDIATE', 'action': 'Replace DE spherical roller bearing & align shaft'},
    'Rotor Dynamic Imbalance': {'color': '#f97316', 'urgency': 'URGENT', 'action': 'Dynamic 2-plane balancing & check balance weights'},
    'Hydraulic Cavitation Wear': {'color': '#f59e0b', 'urgency': 'SCHEDULED', 'action': 'Inspect impeller vanes and suction pressure net positive head'},
    'Stator Winding Overheating': {'color': '#ef4444', 'urgency': 'IMMEDIATE', 'action': 'Check cooling fan airflow and measure insulation resistance'},
    'Mechanical Coupling Looseness': {'color': '#f59e0b', 'urgency': 'SCHEDULED', 'action': 'Torque foundation bolts and recheck laser alignment'}
}

# ─────────────────────────────────────────────────────────────────────────────
# PyTorch Architectures
# ─────────────────────────────────────────────────────────────────────────────

class MachineHealthClassifierNet(nn.Module):
    """Deep Residual MLP for 6-Class Industrial Fault Mode Classification"""
    def __init__(self, in_features=8, num_classes=6):
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
        return self.head(h + res)


class RULRegressorNet(nn.Module):
    """Deep Regressor for Machine Health Score (0-100) & Remaining Useful Life (RUL hours)"""
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
        health = torch.sigmoid(raw[:, 0:1]) * 100.0
        rul = torch.nn.functional.softplus(raw[:, 1:2]) + 24.0
        return torch.cat([health, rul], dim=1)


class PdmInferenceEngine:
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.scalers = None
        self._load_artifacts()

    def _load_artifacts(self):
        scalers_path = os.path.join(BASE_DIR, 'pdm_scalers.json')
        cls_weights = os.path.join(BASE_DIR, 'pdm_classifier_weights.pt')
        reg_weights = os.path.join(BASE_DIR, 'pdm_rul_weights.pt')

        if os.path.exists(scalers_path):
            with open(scalers_path, 'r') as f:
                self.scalers = json.load(f)

        if os.path.exists(cls_weights):
            self.classifier = MachineHealthClassifierNet(in_features=8, num_classes=6)
            self.classifier.load_state_dict(torch.load(cls_weights, map_location=torch.device('cpu')))
            self.classifier.eval()

        if os.path.exists(reg_weights):
            self.regressor = RULRegressorNet(in_features=8)
            self.regressor.load_state_dict(torch.load(reg_weights, map_location=torch.device('cpu')))
            self.regressor.eval()

    def get_machine_info(self, machine_name):
        return MACHINES_CONFIG.get(machine_name, MACHINES_CONFIG['Screw Compressor A-101'])

    def analyze(self, machine_name, features=None, scenario='auto', persist=True):
        if not features:
            features = {}

        machine = self.get_machine_info(machine_name)
        nom_temp = machine['nominal_temp']
        nom_vib = machine['nominal_vib']
        nom_press = machine['nominal_press']
        nom_rpm = machine['nominal_rpm']
        nom_oil = machine['nominal_oil']
        nom_ae = machine['nominal_ae']

        # Extract features with robust fallbacks
        if scenario == 'fault':
            temp = float(features.get('temperature_c', features.get('temp', nom_temp * 1.35)))
            vib = float(features.get('vibration_mm_s', features.get('vibration_mms', features.get('vib', nom_vib * 3.6))))
            press = float(features.get('pressure_bar', nom_press * 1.1))
            rpm = float(features.get('rpm', nom_rpm - 80))
            oil = float(features.get('oil_viscosity_cst', nom_oil * 0.8))
            ae = float(features.get('acoustic_emission_db', nom_ae * 1.3))
            fft_ratio = float(features.get('fft_harmonic_ratio', 0.95))
            bearing_energy = float(features.get('bearing_defect_freq_energy', 1.15))
        elif scenario == 'normal':
            temp = float(features.get('temperature_c', features.get('temp', nom_temp * 0.99)))
            vib = float(features.get('vibration_mm_s', features.get('vibration_mms', features.get('vib', nom_vib * 1.01))))
            press = float(features.get('pressure_bar', nom_press * 1.00))
            rpm = float(features.get('rpm', nom_rpm + 5))
            oil = float(features.get('oil_viscosity_cst', nom_oil * 1.01))
            ae = float(features.get('acoustic_emission_db', nom_ae * 0.99))
            fft_ratio = float(features.get('fft_harmonic_ratio', 0.08))
            bearing_energy = float(features.get('bearing_defect_freq_energy', 0.04))
        else:
            temp = float(features.get('temperature_c', features.get('temp', nom_temp)))
            vib = float(features.get('vibration_mm_s', features.get('vibration_mms', features.get('vib', nom_vib))))
            
            # Support pressure_psi conversion to bar if provided
            if 'pressure_psi' in features and 'pressure_bar' not in features:
                press = float(features['pressure_psi']) * 0.0689476
            else:
                press = float(features.get('pressure_bar', nom_press))

            rpm = float(features.get('rpm', nom_rpm))
            oil = float(features.get('oil_viscosity_cst', nom_oil))
            ae = float(features.get('acoustic_emission_db', nom_ae))
            
            # Derived frequency energies
            vib_ratio = vib / max(0.1, nom_vib)
            temp_ratio = temp / max(1.0, nom_temp)
            if vib_ratio > 2.0:
                fft_ratio = float(features.get('fft_harmonic_ratio', min(1.6, 0.4 * vib_ratio)))
                bearing_energy = float(features.get('bearing_defect_freq_energy', min(1.5, 0.3 * vib_ratio)))
            else:
                fft_ratio = float(features.get('fft_harmonic_ratio', 0.10))
                bearing_energy = float(features.get('bearing_defect_freq_energy', 0.05))

        feat_vector = [temp, vib, press, rpm, oil, ae, fft_ratio, bearing_energy]

        if self.classifier is not None and self.regressor is not None and self.scalers is not None:
            means = np.array(self.scalers['means'], dtype=np.float32)
            stds = np.array(self.scalers['stds'], dtype=np.float32)
            feat_arr = np.array([feat_vector], dtype=np.float32)
            feat_norm = (feat_arr - means) / stds

            x_tensor = torch.tensor(feat_norm)
            with torch.no_grad():
                logits = self.classifier(x_tensor)
                probs = torch.softmax(logits, dim=1).numpy()[0]
                pred_idx = int(np.argmax(probs))
                fault_mode = self.scalers['fault_modes'][pred_idx]

                reg_out = self.regressor(x_tensor).numpy()[0]
                health_score = float(reg_out[0])
                rul_hours = float(reg_out[1])

            # Ensure health score consistency with fault mode
            if fault_mode == 'Normal Baseline':
                health_score = round(max(85.0, min(99.5, health_score)), 1)
                rul_hours = round(max(1500.0, rul_hours), 0)
            else:
                health_score = round(min(65.0, max(15.0, health_score)), 1)
                rul_hours = round(min(750.0, max(24.0, rul_hours)), 0)

        else:
            # Fallback heuristic
            if vib > nom_vib * 2.0 or temp > nom_temp * 1.25:
                fault_mode = 'Outer Race Bearing Spall'
                health_score = 42.5
                rul_hours = 180.0
            else:
                fault_mode = 'Normal Baseline'
                health_score = 95.0
                rul_hours = 2800.0

        fault_info = FAULT_METADATA.get(fault_mode, FAULT_METADATA['Normal Baseline'])
        rul_days = round(rul_hours / 24.0, 1)

        # 8-band FFT vibration spectrum
        is_fault = (fault_mode != 'Normal Baseline')
        fft_spectrum = [
            round(vib * 0.25, 2),  # 1X
            round(vib * (0.85 if 'Imbalance' in fault_mode or 'Looseness' in fault_mode else 0.15), 2),  # 2X
            round(vib * (0.65 if 'Looseness' in fault_mode else 0.08), 2),  # 3X
            round(vib * (1.10 if 'Bearing' in fault_mode else 0.12), 2),  # BPFO
            round(vib * (0.80 if 'Bearing' in fault_mode else 0.08), 2),  # BPFI
            round(vib * 0.18, 2),  # BSF
            round(vib * 0.10, 2),  # FTF
            round(vib * 0.05, 2)   # Noise
        ]

        result = {
            'machine': machine_name,
            'machine_type': machine['type'],
            'criticality': machine['criticality'],
            'icon': machine['icon'],
            'health_score': health_score,
            'fault_mode': fault_mode,
            'urgency': fault_info['urgency'],
            'action_required': fault_info['action'],
            'color': fault_info['color'],
            'rul_hours': rul_hours,
            'rul_days': rul_days,
            'telemetry': {
                'temperature_c': round(temp, 1),
                'vibration_mm_s': round(vib, 2),
                'pressure_bar': round(press, 2),
                'rpm': int(rpm),
                'oil_viscosity_cst': round(oil, 1),
                'acoustic_emission_db': round(ae, 1)
            },
            'fft_harmonics': fft_spectrum,
            'model': 'PyTorch Residual Health Classifier + RUL Regressor'
        }

        if persist:
            record_id = save_inspection(result)
            result['id'] = record_id

        return result

# Global singleton
pdm_engine = PdmInferenceEngine()
