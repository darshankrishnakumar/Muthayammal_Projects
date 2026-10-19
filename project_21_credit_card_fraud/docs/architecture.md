# VIGIL-CARD System Architecture & Data Topology

## 1. System Overview
Project-021 delivers **VIGIL-CARD: Advanced Credit Card Fraud Detection and Autonomous Threat Interdiction Suite**, an enterprise-grade FinTech machine learning platform integrating balanced multi-model ensembles, real-time directional SHAP explainability, and transactional relational persistence.

```
+-------------------------------------------------------------------------------+
|                       FINTECH COMMAND CENTER TIER                             |
|   HTML5 / CSS3 Dark Glassmorphic SPA • Canvas ROC Curve • Port 5021           |
|   Telematics Stream | Forensic Inspector | Benchmarks | Batch & Sanctions     |
+---------------------------------------+---------------------------------------+
                                        | HTTP REST API (JSON Payloads)
+---------------------------------------v---------------------------------------+
                                APPLICATION TIER                                |
|   Python 3.12 Flask Microservices • CORS Security • Rate Limiter              |
|   Cost-Sensitive Policy Engine • Card Sanction State Controller               |
+---------------------------------------+---------------------------------------+
                    |                                       |
+-------------------v-------------------+       +-----------v-------------------+
|         ENSEMBLE MACHINE LEARNING     |       |       PERSISTENCE TIER        |
|  • Balanced Random Forest (100 Trees) |       |  • Relational SQLite Storage  |
|  • Gradient Boosting Regressor (100)  |       |  • 'credit_card_fraud.db'     |
|  • Neural MLP (64-32 Dense ReLU)      |       |  • transactions & blocked     |
|  • Directional SHAP Feature Attrib    |       |  • system_audit & benchmarks  |
+---------------------------------------+       +-------------------------------+
```

## 2. Component Specifications
- **Presentation Layer**: Interactive dark glassmorphic single-page dashboard featuring four specialized modules: Real-Time Telematics Stream, Forensic Inspector with SHAP Waterfall, Model Benchmarks & Threshold Studio, and Batch Evaluation & Card Sanctions.
- **Application Engine**: Python 3.12 with Flask, providing high-throughput authorization endpoints, dynamic threshold recalculation, and automated interlock latching.
- **Ensemble ML Engine**: Multi-model decision system combining 100-tree Balanced Random Forest (cost-sensitive learning), 100-stage Gradient Boosting, and deep feedforward Neural MLP.
- **Explainability Subsystem**: Real-time directional Shapley attribution engine calculating positive and negative risk contributors for every transaction vector.
- **Database Engine**: Transactional SQLite database preserving complete auditable history and card sanction state machines.
