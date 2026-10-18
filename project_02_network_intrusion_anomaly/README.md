# Project 02: Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 2 of 55 (`PROJECT-002`) |
| **Directory** | `project_02_network_intrusion_anomaly` |
| **Backend Port** | `http://localhost:5002` (FastAPI REST Service) |
| **Frontend** | Interactive Cyber Defense SOC Portal (`source_code/frontend/index.html`) |
| **Ensemble ML Models** | Random Forest (100 Trees, 98.34% Acc) + Extra Trees (100 Trees, 98.03% Acc) |
| **Anomaly Detection Model** | Unsupervised Isolation Forest (Contamination = 0.18) |
| **Database** | SQLite3 Transactional Security Store (`source_code/data/nids.db`) |
| **Automated Tests** | 19 Passed / 0 Failed (`pytest`) |
| **Demonstration Video** | `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180s**, 1280x800 H.264 MP4) |
| **Audit Status** | **VERIFIED COMPLETE (100%)** |

---

## 📄 Abstract
Modern enterprise cyber perimeters face an evolving onslaught of volumetric denial-of-service (DoS) assaults, stealthy reconnaissance scans, unauthorized credential access attempts, and novel zero-day exploits that easily evade legacy signature-based firewalls. This project presents **CyberShield AI**, an autonomous dual-engine Network Intrusion Detection System (NIDS) coupling a high-precision supervised ensemble with an unsupervised anomaly detector. Trained on over 22,500 validated connection records from the standard NSL-KDD benchmark across 111 transformed feature dimensions, the supervised ensemble—combining Random Forest (100 trees) and Extremely Randomized Trees (100 trees)—achieves 98.34% test accuracy and a 0.9833 weighted F1-score across five attack categories (Normal, DoS, Probe, R2L, U2R). To catch unseen polymorphic threats, an unsupervised Isolation Forest continuously evaluates out-of-distribution isolation path lengths. The production-ready system is delivered with an asynchronous FastAPI REST microservice, an SQLite3 transactional audit store, and an interactive dark-mode Security Operations Center (SOC) dashboard.

---

## 🏗️ System Architecture & Workflow

```
[User / Security Operator / Proxy]
               │ (HTTP REST / JSON)
               ▼
   [FastAPI Gateway (Port 5002)]
               │
    ┌──────────┴──────────────────────────────┐
    ▼                                         ▼
[Feature Preprocessing Engine]       [Database Layer (SQLite3)]
• ColumnTransformer (111 Dims)       • nids.db (security_events table)
• StandardScaler & OneHotEncoder     • Real-time Aggregate Analytics
    │                                         ▲
    ▼                                         │
[Dual Inference Engines]                      │
• Supervised Ensemble (RF + Extra Trees) ─────┤
• Unsupervised Isolation Forest Anomaly ──────┘
    │
    ▼
[Response & Defense Countermeasures]
• Multi-class Classification, Threat Level, Anomaly Risk %, Automated Mitigation Action
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Run Automated Verification Tests
```bash
PYTHONPATH=source_code pytest source_code/tests/ -v
```
All 19 tests will pass in under 3 seconds.

### 3. Launch Backend & SOC Web Application
```bash
python3 -m uvicorn backend.main:app --app-dir source_code --host 127.0.0.1 --port 5002 --reload
```
Open **`http://localhost:5002`** in your browser to access the complete interactive CyberShield AI dashboard.

---

## 📚 Technical Documentation Catalog
- [Documentation Index](docs/README.md)
- [System Architecture & Design](docs/architecture.md)
- [API Specification (OpenAPI 3.0)](docs/api_documentation.md)
- [Dataset & Model Specifications](docs/dataset_and_model_details.md)
- [Testing & Quality Assurance Report](docs/testing_report.md)
- [Setup & Execution Guide](docs/setup_and_execution.md)
- [Final Acceptance Report](docs/acceptance_report.md)
- [Third-Party Software Notices](docs/third_party_notices.md)
- [Limitations & Future Roadmap](docs/limitations_and_future_work.md)
- [Academic Paper (DOCX)](docs/technical_documentation.docx)
- [Presentation Deck (PPTX)](presentations/project_presentation.pptx)
- [Walkthrough Video (MP4)](walkthrough/walkthrough_video.mp4)
- [Walkthrough Timestamps & Script](walkthrough/walkthrough_timestamps.md)
