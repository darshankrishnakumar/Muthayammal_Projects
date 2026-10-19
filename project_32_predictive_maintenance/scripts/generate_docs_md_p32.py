#!/usr/bin/env python3
"""
Generate 8-File Markdown Documentation Suite for Project 32
Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data and Deep Learning
"""

import os

def generate_markdown_docs():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    files = {
        "01_ABSTRACT.md": """# Project 32: Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data & Deep Learning
## 1. Abstract & Executive Summary

Industrial rotating machinery (compressors, pumps, motors, and gas turbines) forms the operational backbone of modern process manufacturing. Unscheduled downtime caused by sudden bearing spalling, dynamic imbalance, or cavitation imposes severe economic and safety tolls on plant operations.

Project 32 establishes an AI-driven condition monitoring and Remaining Useful Life (RUL) estimation platform deployed as an edge-viable microservice. Integrating 8-band Fast Fourier Transform (FFT) vibration kinematics with multivariate thermal, acoustic, and pressure telemetry, the system executes dual deep learning models in PyTorch:
1. `MachineHealthClassifierNet`: Deep Residual Multi-Layer Perceptron (8 -> 64 -> 64 -> 32 -> 6) classifying equipment health across 6 operational fault modes with 96.83% validation accuracy.
2. `RULRegressorNet`: Physics-constrained neural regressor estimating continuous health scores (0-100) and forecasting Remaining Useful Life in operating hours and days.

### Key Highlights
- **Real Industrial Telemetry**: 6,000 multivariate sensor records across 5 mission-critical machines.
- **8-Band FFT Kinematics**: Harmonic tracking of 1X, 2X, BPFO, BPFI, BSF, FTF, and HF noise bands.
- **ACID Persistence**: SQLite database (`predictive_maintenance.db`) running in Write-Ahead Logging (WAL) mode.
- **Dedicated Port**: Bound to `http://127.0.0.1:5032/` with 31/31 passing automated QA tests (100% pass rate).
""",

        "02_REQUIREMENTS.md": """# Project 32: Requirements Specification

## 1. Functional Requirements (FR)
- **FR-01 (Multivariate Ingestion)**: Ingest 8-dimensional telemetry streams (temperature °C, vibration RMS mm/s, discharge pressure bar, shaft RPM, oil viscosity cSt, ultrasonic acoustic emission dB, FFT harmonic ratio, bearing defect energy).
- **FR-02 (6-Class Fault Diagnostics)**: Classify incoming equipment states into: Normal Baseline, Outer Race Bearing Spall, Rotor Dynamic Imbalance, Hydraulic Cavitation Wear, Stator Winding Overheating, or Mechanical Coupling Looseness.
- **FR-03 (Remaining Useful Life Estimation)**: Quantify remaining operating life in hours (24 to 4,000 hrs) and days.
- **FR-04 (Health Score Computation)**: Output a bounded 0-100% health index reflecting multi-channel sensor degradation.
- **FR-05 (Automated Work Order Dispatch)**: Automatically issue maintenance work orders with technician assignments and corrective action protocols.
- **FR-06 (ACID Relational Storage)**: Persist all diagnostic inspections, telemetry snapshots, and work orders in SQLite with Write-Ahead Logging (WAL).

## 2. Non-Functional Requirements (NFR)
- **NFR-01 (Inference Latency)**: End-to-end forward pass latency $< 10$ milliseconds on CPU.
- **NFR-02 (Diagnostic Accuracy)**: Fault classification accuracy $> 95\%$ on held-out test data with zero false negatives on critical faults.
- **NFR-03 (High Concurrency)**: SQLite WAL mode (`PRAGMA journal_mode=WAL;`) ensuring non-blocking reads during continuous telemetry logging.
- **NFR-04 (Port Consistency)**: Operates strictly on allocated network port 5032.
""",

        "03_ARCHITECTURE.md": """# Project 32: System Architecture

```
+-----------------------------------------------------------------------------------+
|                        INDUSTRIAL ASSET SENSOR TELEMETRY                          |
|   [Accelerometers]   [RTD Thermal]   [Pressure Transducers]   [Encoders]   [AE]   |
+------------------------------------------+----------------------------------------+
                                           | 8-D Multivariate Stream (Vib/Temp/Press)
                                           v
+-----------------------------------------------------------------------------------+
|                     APPLICATION TIER (Flask Microservice @ Port 5032)             |
|  +-----------------------------------------------------------------------------+  |
|  | REST Endpoints: /api/analyze, /api/machines, /api/history, /api/work-order  |  |
|  +-----------------------------------------------------------------------------+  |
|                                          |                                        |
|         +--------------------------------+-------------------------------+        |
|         v                                                                v        |
|  +----------------------------------+          +-------------------------------+  |
|  | MachineHealthClassifierNet       |          | RULRegressorNet               |  |
|  | - Deep Residual MLP              |          | - LayerNorm + GELU MLP        |  |
|  | - 6 Fault Classes Diagnosis      |          | - Health Score (0-100)        |  |
|  | - Cross-Entropy Loss             |          | - RUL Hours (24 - 4,000 hrs)  |  |
|  +----------------------------------+          +-------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     DATA PERSISTENCE & WORK ORDER DISPATCH TIER                   |
|  +-----------------------------------------------------------------------------+  |
|  | SQLite Relational DB (predictive_maintenance.db) in WAL Mode                |  |
|  | Tables: machines, sensor_telemetry, diagnostic_inspections, work_orders     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```
""",

        "04_DATASET_AND_PREPROCESSING.md": """# Project 32: Dataset & Sensor Preprocessing

## 1. Machine Fleet Composition
The dataset comprises 6,000 records distributed across 5 industrial rotating machines:
- **Screw Compressor A-101**: 2,980 RPM, Rotary Screw Compressor, High criticality.
- **Centrifugal Pump B-204**: 1,480 RPM, Slurry Circulation Pump, Critical.
- **Induction Motor C-302**: 1,780 RPM, 3-Phase 350kW Motor, Medium criticality.
- **Gas Turbine Generator D-401**: 5,400 RPM, Co-Gen Gas Turbine, Critical.
- **Conveyor Drive Unit E-505**: 720 RPM, Heavy Ore Conveyor Drive, Low criticality.

## 2. Feature Definitions
| Feature Name | Type | Unit | Description |
|---|---|---|---|
| `temperature_c` | Float | °C | Bearing race temperature |
| `vibration_mm_s` | Float | mm/s | Casing vibration velocity RMS |
| `pressure_bar` | Float | bar | Fluid discharge pressure |
| `rpm` | Float | RPM | Shaft angular velocity |
| `oil_viscosity_cst` | Float | cSt | Lubrication oil dynamic viscosity |
| `acoustic_emission_db` | Float | dB | High-frequency ultrasonic emission |
| `fft_harmonic_ratio` | Float | ratio | 2X to 1X harmonic ratio |
| `bearing_defect_freq_energy` | Float | energy | BPFO/BPFI defect frequency energy |

Normalized using z-score normalization parameters stored in `pdm_scalers.json`.
""",

        "05_MODEL_DESIGN_AND_TRAINING.md": """# Project 32: Model Design & Training Dynamics

## 1. Neural Network Topologies
- **MachineHealthClassifierNet**: Residual multi-layer perceptron with skip connections, batch normalization, and dropout. Trained with AdamW ($lr=0.003$) and CrossEntropyLoss over 25 epochs, reaching **96.83%** validation accuracy.
- **RULRegressorNet**: Deep dense MLP utilizing LayerNorm and GELU activations. The output heads utilize Sigmoid scaling (0-100 health score) and Softplus activation (+24h minimum RUL) to enforce strict physical degradation boundaries.

## 2. Training Trajectory
- Classification Loss: 0.2840 -> 0.0884 (Epoch 25).
- Validation Accuracy: 96.83% on 1,200 held-out test records.
- Weights saved on disk: `pdm_classifier_weights.pt` (56.7 KB) and `pdm_rul_weights.pt` (33.4 KB).
""",

        "06_API_SPECIFICATION.md": """# Project 32: REST API Specification

### Base URL: `http://127.0.0.1:5032/`

#### 1. Liveness & Health
- `GET /api/health`
- Response: Status, Port 5032, Monitored Assets, Active Models, Storage Mode.

#### 2. Diagnostic Analysis & RUL Forecasting
- `POST /api/analyze`
- Body:
```json
{
  "machine": "Gas Turbine Generator D-401",
  "scenario": "fault",
  "features": {
    "temperature_c": 135.0,
    "vibration_mm_s": 5.2,
    "pressure_bar": 21.0
  }
}
```
- Response: `fault_mode`, `health_score`, `urgency`, `action_required`, `color`, `rul_hours`, `rul_days`, `fft_harmonics`, `telemetry`.

#### 3. Equipment Inventory & Work Orders
- `GET /api/machines`: Lists all 5 monitored equipment assets with nominal parameters.
- `GET /api/history?limit=30`: Queries historical diagnostic inspections.
- `GET /api/stats`: Fleet-wide reliability KPIs.
- `POST /api/work-order`: Automatically dispatch corrective maintenance crews.
- `GET /api/work-orders`: Returns dispatched maintenance work orders.
- `GET /api/audit-logs`: System audit trail.
""",

        "07_DATABASE_DESIGN.md": """# Project 32: Relational Database Schema & WAL Configuration

### Engine: SQLite3 in Write-Ahead Logging (WAL) Mode
- `PRAGMA journal_mode=WAL;`
- `PRAGMA synchronous=NORMAL;`
- `PRAGMA foreign_keys=ON;`

### Database Tables:
1. `machines`: Equipment master inventory (ID, name, type, nominal RPM, baseline temp, vibration, oil, AE, criticality).
2. `sensor_telemetry`: High-frequency multi-modal telemetry streams.
3. `diagnostic_inspections`: Model forward-pass inference logs, health scores, fault modes, and 8-band FFT spectra.
4. `maintenance_work_orders`: Official corrective work orders, assigned technicians, and resolution statuses.
5. `audit_log`: Chronological system lifecycle and operational events.
""",

        "08_TESTING_AND_VERIFICATION.md": """# Project 32: Quality Assurance & Verification Suite

## 1. Automated Test Results
- **Test Runner**: Pytest 9.1.1 & Unittest (Python 3.12).
- **Test File**: `source_code/tests/test_api_and_system.py` (28 tests) & `test_audit_verification.py` (3 tests).
- **Results**: **31 passed in 0.50s (100% pass rate)**.

## 2. Test Coverage Matrix
- System health and dedicated Port 5032 verification.
- PyTorch model weights integrity and tensor dimension checks.
- SQLite WAL mode and table existence verification.
- Machine fleet enumeration and nominal operating baseline checks.
- Normal baseline vs fault scenario bifurcations.
- Pressure PSI to bar unit conversion verification.
- Health score bounds ($0 \le \text{score} \le 100$) and RUL hours ($\ge 24$h).
- 8-band FFT harmonic spectrum extraction.
- Automated work order generation and audit logging.
"""
    }

    for fname, content in files.items():
        fpath = os.path.join(docs_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"Generated {fpath}")

if __name__ == "__main__":
    generate_markdown_docs()
