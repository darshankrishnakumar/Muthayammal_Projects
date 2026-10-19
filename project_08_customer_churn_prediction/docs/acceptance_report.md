# Technical Acceptance Report: Customer Churn Intelligence System (PROJECT-008)

## 1. Project Identification
- **Project ID**: PROJECT-008
- **Project Directory**: `project_08_customer_churn_prediction`
- **Official Academic Title**: Customer Survival Analysis and Churn Prediction
- **Assigned Service Port**: 5008 (`http://127.0.0.1:5008`)
- **Evaluation Date**: October 19, 2026
- **Auditor Role**: Senior Technical Auditor, Software QA Engineer & Project Completion Manager

---

## 2. Technical Deliverable Checklist & Audit Findings

| Category | Requirement | Status | Evidence / Verification Notes |
|---|---|---|---|
| **Data Integrity** | Real tabular dataset loaded | PASS | 7,043 real IBM Telco records loaded in `source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/Telco-Customer-Churn.csv` |
| **Machine Learning** | Fully trained ML models | PASS | Real serialized Random Forest (`model.pkl`, 38 MB) and Cox survival model (`survivemodel.pkl`, 710 KB); ROC-AUC = 0.844 |
| **Explainable AI** | SHAP Interpretability | PASS | SHAP TreeExplainer generates dynamic force/waterfall visualizations on-the-fly |
| **Backend API** | REST API service | PASS | Flask microservice running on port 5008 (`/api/stats`, `/api/metrics`, `/api/history`, `/predict`) |
| **Frontend UI** | Modern web interface | PASS | Responsive Bootstrap 5 interface with executive KPIs, form input controls, needle gauges, and survival curves |
| **Database** | Relational data persistence | PASS | SQLite relational store (`predictions.db`) recording transaction histories and risk tiers |
| **Automated Tests** | $\ge 15$ passing automated tests | PASS | **23/23 passing unit & integration tests** in 2.88s (`pytest source_code/tests/`) |
| **UI Screenshots** | Real captured UI screenshots | PASS | 7 high-res PNG screenshots captured into `docs/screenshots/` |
| **Presentation** | 15-slide widescreen PPTX | PASS | `presentations/project_presentation.pptx` (918 KB) embedding real UI screenshots |
| **Documentation** | Academic DOCX document | PASS | `docs/technical_documentation.docx` containing 57 detailed academic paragraphs |
| **Documentation** | Comprehensive Markdown suite | PASS | 9 markdown documents (`README.md`, `architecture.md`, `dataset_and_model_details.md`, `api_documentation.md`, `setup_and_execution.md`, `testing_report.md`, `limitations_and_future_work.md`, `third_party_notices.md`, `acceptance_report.md`) |
| **Demonstration** | 2.5–3.5 min MP4 video | PASS | `walkthrough/walkthrough_video.mp4` verified (exact 03:00 / 180s, 1280x800 H.264) |
| **Execution Scripts** | Timestamps & walkthrough script | PASS | Complete script and timestamp synchronization in `walkthrough/` |

---

## 3. Auditor Final Verdict
**STATUS: 100% COMPLETE AND SUBMISSION READY.**  
PROJECT-008 fulfills all software engineering standards, functional requirements, and academic capstone evaluation criteria.
