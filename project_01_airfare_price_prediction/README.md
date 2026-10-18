# Project 01: A Holistic Approach on Airfare Price Prediction Using LSTM Machine Learning Techniques

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 1 of 55 (`PROJECT-001`) |
| **Directory** | `project_01_airfare_price_prediction` |
| **Backend Port** | `http://localhost:5001` (FastAPI REST Service) |
| **Frontend** | Responsive Aviation Portal (`source_code/frontend/index.html`) |
| **Deep Learning Model** | PyTorch 2.0 Bidirectional LSTM Regressor ($R^2 = 0.7566$, $\text{MAE} = ₹1,362.47$) |
| **Benchmark Model** | Random Forest Regressor ($R^2 = 0.8321$, $\text{MAE} = ₹1,136.58$) |
| **Database** | SQLite3 Transactional Store (`source_code/data/airfare.db`) |
| **Automated Tests** | 18 Passed / 0 Failed (`pytest`) |
| **Demonstration Video** | `walkthrough/walkthrough_video.mp4` (Duration: **02:37**, 1280x800 H.264 MP4) |
| **Audit Status** | **VERIFIED COMPLETE (100%)** |

---

## 📄 Abstract
Airline ticket pricing is notoriously volatile and dynamically adjusted by carriers using proprietary yield management systems that optimize revenues based on demand forecasting, departure proximity, layovers, route competition, and seasonal trends. This project presents a holistic computational framework for predicting airline ticket prices using a Deep Bidirectional Long Short-Term Memory (BiLSTM) neural network alongside an ensemble Random Forest benchmark. Trained on over 10,600 verified domestic flight records across major Indian carriers (IndiGo, Air India, Jet Airways, SpiceJet, Vistara, and Air Asia), the system captures complex non-linear temporal dynamics between journey dates, booking lead times, flight duration, and stopover structures. The production-ready system provides an asynchronous FastAPI inference service, an SQLite audit database logging prediction transactions, and an interactive modern web dashboard with confidence interval estimation, empirical model comparison, historical audit logging, and pricing analytics.

---

## 🏗️ System Architecture & Workflow

```
[User / Client Interface]
          │ (HTTP REST / JSON)
          ▼
   [FastAPI Gateway (Port 5001)]
          │
    ┌─────┴────────────────────────────────┐
    ▼                                      ▼
[Feature Engineering Engine]      [Database Layer (SQLite3)]
• ColumnTransformer Preprocessor  • airfare.db (Transactional Logs)
• StandardScaler & OneHotEncoder  • Aggregate Statistics Engine
    │                                      ▲
    ▼                                      │
[Dual Inference Models]                    │
• PyTorch 2-Layer BiLSTM Neural Network    │
• Scikit-Learn Random Forest Regressor ────┘
    │
    ▼
[Response Formatter]
• Point Estimate, 95% Confidence Bounds, Currency Conversions
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
All 18 tests will pass in under 3 seconds.

### 3. Launch Backend & Web Application
```bash
python3 -m uvicorn backend.main:app --app-dir source_code --host 127.0.0.1 --port 5001 --reload
```
Open **`http://localhost:5001`** in your browser to access the complete interactive valuation portal.

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
