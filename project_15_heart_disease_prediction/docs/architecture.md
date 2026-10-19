# System Architecture & Technical Design

## 1. High-Level Architecture Overview

CardioPredict (PROJECT-015) is a full-stack, AI-powered cardiovascular diagnostic intelligence platform. It couples a React 18 single-page application with a Python Flask 3.1 microservice running on dedicated Port 5015.

```
+-----------------------------------------------------------------------------------+
|                        CARDIOPREDICT CLINICAL FRONTEND                            |
|     React 18 + TypeScript + Vite, Chart.js (Bar, Radar, Pie, Line), Theme Switch  |
+-----------------------------------------------------------------------------------+
                                        |  HTTP / REST (Port 5015)
                                        v
+-----------------------------------------------------------------------------------+
|                         FLASK APPLICATION MICROSERVICE                            |
|   / | /api/health | /api/predict | /api/download-report | /api/history | /api/stats |
+-----------------------------------------------------------------------------------+
                   |                                             |
                   v                                             v
+---------------------------------------+       +-----------------------------------+
|         AI/ML INFERENCE ENGINE        |       |       DATABASE & PDF ENGINE       |
|                                       |       |                                   |
|  - 11 Clinical Feature Vector Input   |       |  - SQLite (heart_patients.db)     |
|  - RandomForestClassifier (100 Trees) |       |  - 'patient_assessments' Table    |
|  - Multi-tree Gini Probability Engine |       |  - ReportLab PDF Vector Engine    |
|  - 4-Tier Risk Categorization Layer   |       |  - Tabular Parameter Summary      |
|  - Sub-2ms Latency Guarantee          |       |  - Immutable Audit Trail          |
+---------------------------------------+       +-----------------------------------+
```

## 2. Component Specifications

### 2.1 Frontend User Interface (source_code/frontend)
- React 18 with TypeScript and Vite bundling.
- Responsive form grid with 11 physiological inputs and tooltip helpers.
- Interactive Chart.js visualizers: Vital Signs Comparison, Cardiovascular Radar Profile, and Risk Distribution.
- Integrated Body Mass Index (BMI) calculator with dynamic classification.
- Light/Dark mode clinical theme toggle.

### 2.2 Backend Microservice (source_code/app.py)
- Flask microservice serving static build from `frontend/dist` and exposing REST endpoints.
- Pydantic-style type casting and input validation for all 11 medical features.
- Dedicated port allocation: **Port 5015**.

### 2.3 Diagnostic Engine (heart_model.pkl)
- Scikit-Learn `RandomForestClassifier` trained on 918 UCI patient records.
- Delivers dual-class probabilities and automated risk tier categorization.

### 2.4 Clinical PDF Reporting Subsystem
- ReportLab Platypus engine generating vector PDF reports on demand.
- Includes patient vitals, normal baseline comparisons, and formal medical disclaimers.

### 2.5 Relational SQLite Registry (heart_patients.db)
- ACID-compliant transactional persistence for all patient consultations.
