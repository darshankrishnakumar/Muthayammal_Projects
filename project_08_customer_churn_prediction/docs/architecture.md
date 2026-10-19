# System Architecture & Technical Design: Customer Churn Prediction (PROJECT-008)

## 1. High-Level Architectural Overview
PROJECT-008 is structured as an enterprise-grade, multi-tier intelligence application designed to predict telecom subscriber churn, model time-to-event survival hazard curves, compute customer lifetime value (CLTV), and deliver local explainability via SHAP.

```mermaid
flowchart TD
    subgraph Client ["Client Presentation Tier (Bootstrap 5 & HTML5)"]
        UI_Dash["Executive Dashboard (/)\nKPIs, Churn Rate, Donut Chart"]
        UI_Pred["Inference Portal (/predict)\nProfile Forms & Pre-configured Presets"]
        UI_Gauge["Dynamic Visualizations\nRisk Needle Gauge, Survival Curve, SHAP Plot"]
        UI_Perf["Performance Leaderboard (/model-performance)\nConfusion Matrix, ROC Curve, Accuracy"]
        UI_Hist["Audit History (/history)\nSQLite Transaction Table"]
    end

    subgraph Service ["Flask WSGI Application Tier (Port 5008)"]
        Router["URL Routing & Request Handlers"]
        Validator["Input Sanitizer & Boundary Verification"]
        NormWrapper["Probability Normalization Engine"]
        CLTVCalc["CLTV Integral Estimator"]
        ActionEngine["Rule-Based Retention Policy Engine"]
    end

    subgraph ML ["Dual Machine Learning Core"]
        RF["Random Forest Classifier\n1,000 Decision Trees (38 MB)\nSoft Voting Probability"]
        Cox["Cox Proportional Hazards Model\nLifelines Semi-Parametric Engine (710 KB)\nCumulative Hazard & Survival Decay"]
        SHAP["SHAP TreeExplainer\nGame-Theoretic Feature Attribution"]
    end

    subgraph Storage ["Persistence & Data Assets"]
        CSV["Telco-Customer-Churn.csv\n7,043 Real Customer Records"]
        DB[(SQLite predictions.db\nACID Audit Ledger)]
        Metrics["model_evaluation_metrics.json\nPrecomputed Holdout Metrics"]
    end

    Client -->|HTTP GET/POST| Router
    Router --> Validator
    Validator --> NormWrapper
    NormWrapper --> RF
    Validator --> Cox
    Validator --> SHAP
    RF --> ActionEngine
    Cox --> CLTVCalc
    Router --> DB
    Router --> Metrics
```

## 2. Component Design Specifications

### 2.1 Microservice Controller (`app.py`)
- **Port Allocation**: 5008 (`http://127.0.0.1:5008`)
- **Framework**: Flask 3.0+ WSGI application with Jinja2 templating.
- **Backward Compatibility Shims**: Custom `_CustomUnpickler` and `_PatchedTree` dynamically resolve scikit-learn tree node state differences across minor library releases.
- **REST APIs**: JSON endpoints (`/api/stats`, `/api/metrics`, `/api/history`) support programmatic consumption by third-party CRMs.

### 2.2 Dual Machine Learning Inference Pipeline
- **Binary Classification (Random Forest)**:
  - 1,000 estimators with balanced class weighting.
  - Takes 23 input features (demographics, services, contracts, charges, and tenure).
  - Encapsulated with a probability normalization wrapper ensuring $\sum P(Y) = 1.0$.
- **Time-to-Event Survival Analysis (Cox Proportional Hazards)**:
  - Evaluates hazard multiplier $h(t|X) = h_0(t) \exp(\beta^T X)$.
  - Takes 22 features (excluding tenure duration $T$).
  - Outputs continuous survival probability curve $S(t)$ over 72 months.
- **Local Interpretability (SHAP TreeExplainer)**:
  - Decomposes exact Shapley feature values $\phi_i$ for each customer query.
  - Automatically generates dynamic Matplotlib bar charts converted to Base64 image URIs.

### 2.3 Transactional Data Persistence (`database.py`)
- SQLite database (`predictions.db`) stores every evaluated subscriber profile, risk score, CLTV, and prescribed retention intervention.
- ACID transaction guarantees ensure zero data loss during high-concurrency requests.
