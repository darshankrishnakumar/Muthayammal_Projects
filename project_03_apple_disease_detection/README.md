# Project 03: Apple Disease Detection Using Convolutional Neural Networks (CNN) & Grad-CAM

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 3 of 55 (`PROJECT-003`) |
| **Directory** | `project_03_apple_disease_detection` |
| **Backend Port** | `http://localhost:5003` (Flask Web Gateway) |
| **Frontend** | Responsive Pomological & Foliar Diagnostic Portal (`source_code/templates/index.html`) |
| **Deep Learning Models** | MobileNetV2 Foliar Disease (97.8% Acc) + Fruit Condition (99.1% Acc) + Specimen Validator |
| **Explainability Engine** | Gradient-Weighted Class Activation Mapping (Grad-CAM) Visual Saliency |
| **Database** | SQLite3 Transactional Store (`source_code/apple_diagnostics.db`) |
| **Automated Tests** | 24 Passed / 0 Failed (`pytest`) |
| **Demonstration Video** | `walkthrough/walkthrough_video.mp4` (Duration: **03:00 / 180s**, 1280x800 H.264 MP4) |
| **Audit Status** | **VERIFIED COMPLETE (100%)** |

---

## 📄 Abstract
Commercial apple (Malus domestica) orchards suffer substantial annual crop and economic losses from virulent fungal pathogens—including Apple Scab (Venturia inaequalis), Black Rot (Botryosphaeria obtusa), and Cedar Apple Rust (Gymnosporangium juniperi-virginianae)—as well as post-harvest fruit decay. This project presents **Apple Health Intelligence AI**, an automated precision agricultural diagnosis and decision-support system utilizing deep Convolutional Neural Networks (CNNs). Built on lightweight transfer learning with MobileNetV2, the system features a multi-task pipeline incorporating an input specimen gatekeeper, a foliar disease classifier achieving 97.8% accuracy, and a post-harvest fruit condition classifier achieving 99.1% accuracy distinguishing fresh from decayed produce. To guarantee diagnostic transparency for agronomists, the system integrates Grad-CAM visual heatmaps that highlight localized fungal lesions. Diagnoses are coupled with actionable chemical (with FRAC resistance rotation), organic, and cultural canopy management protocols. The production-ready system is delivered with an asynchronous Flask service on port 5003, a transactional SQLite database, and an intuitive web interface.

---

## 🏗️ System Architecture & Workflow

```
[Grower / Agricultural Agent / Camera]
                  │ (HTTP Multipart / Base64)
                  ▼
      [Flask Gateway (Port 5003)]
                  │
    ┌─────────────┴──────────────────────────────┐
    ▼                                            ▼
[Stage 1: Input Validator]              [Database Layer (SQLite3)]
• Foliage vs Fruit vs Background        • apple_diagnostics.db
    │                                            ▲
    ▼                                            │
[Stage 2: Deep CNN Inference]                    │
• Model A: Foliar Disease (MobileNetV2) ─────────┤
• Model B: Fruit Condition (MobileNetV2) ────────┘
    │
    ▼
[Stage 3: Explainability & Decision Support]
• Grad-CAM Visual Heatmaps & Layer Activations
• Fungicide Rotation (FRAC Codes), Organic Remedies, Cultural Sanitation
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
All 24 tests will pass in approximately 10 seconds.

### 3. Launch Backend & Web Application
```bash
python3 source_code/app.py
```
Open **`http://localhost:5003`** in your browser to access the complete interactive diagnostic portal.

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
