# Project 37: AI Traffic Violation Detection & ANPR Safety Enforcement System

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 37 of 55 (College Capstone Engineering Portfolio) |
| **Domain** | Intelligent Transportation Systems (ITS) / Computer Vision / Edge Safety Enforcement |
| **Directory** | `project_37_traffic_violation` |
| **Backend Port** | `http://localhost:5037` |
| **Frontend** | Standalone Interactive HUD (`frontend/index.html`) |
| **AI Models** | PyTorch `TrafficViolationClassifierNet` (100% Acc) & `TrafficSafetySeverityRegressorNet` |
| **Database** | Relational SQLite (`traffic_enforcement.db`) with 6 Schemas in WAL Mode |
| **Verification Suite** | 35 Automated Unit/Integration/Forensic Tests (100% Pass Rate) |

---

## 📄 Abstract
As urban vehicle density continues to grow, enforcing traffic rules and maintaining road order have become increasingly challenging for law enforcement agencies. Traditional manual monitoring is insufficient for continuous surveillance and prone to human error. To address this, this project presents **TRAFFIC-AI**, an automated edge-to-cloud intelligent transportation safety enforcement system designed in strict accordance with Indian Roads Congress (IRC) SP:90 standards and ISO 39001 Road Traffic Safety Management guidelines.

The architecture synthesizes real-time multi-modal telemetry from 4K UltraHD surveillance feeds, radar speed profilers, and optical signal phase indicators to detect moving traffic infractions with sub-15ms latency. Two trained PyTorch 2.x neural networks drive inference: (1) `TrafficViolationClassifierNet`, a Deep Residual MLP classifying eight statutory violation categories with 100.0% test accuracy; and (2) `TrafficSafetySeverityRegressorNet`, a dual-head model outputting a continuous Violation Severity Index (0-100) and Collision Risk Probability (0.0-1.0). All detected violations trigger statutory Motor Vehicles Act (MVA) 2019 e-Challan records bound by SHA-256 cryptographic evidence hashes stored in an append-only block hash chain.

---

## 🚀 Key Features
- **Dedicated Port 5037 Microservice**: High-throughput Flask REST API with zero external cloud dependencies.
- **Real Trained Neural Networks**: Serialized weights on disk (`violation_classifier_weights.pt` [332 KB], `safety_regressor_weights.pt` [54 KB]).
- **6,000-Record Balanced Telemetry Dataset**: Saved to `data/traffic_violation_telemetry_6000.csv` covering 8 violation categories and 6 vehicle classes.
- **ACID Database Persistence**: SQLite Write-Ahead Logging (`traffic_enforcement.db`) with 6 relational tables.
- **Statutory MVA E-Challans**: Automatic fine calculation under MVA Sections 183(1), 184, 184(c), 194B, 194D, and 177.
- **Forensic Audit Ledger**: SHA-256 block hash chaining for court-admissible evidence integrity.
- **Interactive 4K CCTV HUD**: Animated road canvas, radar speed overlays, bounding boxes, corridor switching, and live violation feeds.
- **100% Verified QA Test Suite**: 35 automated tests passing with zero failures or flakiness.

---

## 🛠️ Quickstart

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Models
```bash
python3 source_code/backend/database.py
python3 source_code/backend/train_models.py
```

### 3. Launch Microservice
```bash
python3 source_code/backend/app.py
```
Open your browser at `http://127.0.0.1:5037/`.

### 4. Run Automated QA Tests
```bash
python3 -m unittest discover -s source_code/tests -p "test_*.py"
```
