# Project 03: Documentation Index

## Overview
This directory contains technical, architectural, and agronomic documentation for **Project 03: Apple Disease Detection Using Convolutional Neural Networks (CNN) & Grad-CAM Explainability** (Apple Health Intelligence AI).

### Documentation Catalog
1. [Architecture & System Design](architecture.md) — Multi-task deep learning pipeline, MobileNetV2 inverted residual blocks, Grad-CAM mathematical formulation, and SQLite3 database schema.
2. [API Specification](api_documentation.md) — Complete OpenAPI 3.0 REST endpoint documentation (/health, /api/samples, /api/predict, /api/db/status, /api/db/history, /api/encyclopedia).
3. [Dataset & Model Specifications](dataset_and_model_details.md) — PlantVillage benchmark analysis, data augmentation parameters, model checkpoint details, and empirical accuracy/F1 metrics.
4. [Testing & Quality Assurance Report](testing_report.md) — Test execution report with 24 passing tests (100% pass rate) across models, transforms, database, and Flask REST APIs.
5. [Setup & Execution Guide](setup_and_execution.md) — Instructions for local environment reproduction, running tests, launching the web portal on port 5003, and retraining models.
6. [Acceptance & Compliance Report](acceptance_report.md) — Verification matrix against the 15 final-year engineering criteria and technical audit sign-off.
7. [Third-Party Software Notices](third_party_notices.md) — Licenses, attributions, and open-source dependencies (PyTorch, Torchvision, Flask, etc.).
8. [Limitations & Future Roadmap](limitations_and_future_work.md) — Discussion of lighting invariance, handheld drone integrations, and edge deployment.

Formal academic documentation is compiled in [technical_documentation.docx](technical_documentation.docx) and presentation slides are in `../presentations/project_presentation.pptx`.
