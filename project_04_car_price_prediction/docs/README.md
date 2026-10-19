# AutoValuate AI: Car Price Prediction & Automotive Valuation Engine

Welcome to the official technical documentation suite for **PROJECT-004: Car Price Prediction & Automotive Market Valuation Engine**.

AutoValuate AI is a production-grade machine learning platform designed to eliminate information asymmetry and deliver fair-market vehicle valuations using Scikit-Learn regression pipelines.

---

## Documentation Index

1. [System Architecture](architecture.md) - Pipeline design, component interactions, and dataflow diagrams.
2. [Dataset and Model Details](dataset_and_model_details.md) - Historical sales records, feature engineering, and model benchmarks.
3. [REST API Documentation](api_documentation.md) - OpenAPI specifications for FastAPI endpoints on Port 5004.
4. [Setup and Execution Guide](setup_and_execution.md) - Installation instructions, dependency management, and server execution.
5. [Testing & Verification Report](testing_report.md) - 18 automated pytest cases, metric reproducibility, and boundary validation.
6. [Limitations and Future Work](limitations_and_future_work.md) - Constraints, non-linear dynamics, and roadmap items (YOLOv8 damage inspection).
7. [Third-Party Notices](third_party_notices.md) - Open-source licensing register and attribution.
8. [Acceptance Sign-Off Report](acceptance_report.md) - Final engineering verification against all 15 audit criteria.

---

## Executive Overview

- **Project Identifier**: `PROJECT-004`
- **Domain**: Automotive Intelligence & Machine Learning Regression
- **Optimal Model**: 150-Tree Random Forest Regressor ($R^2 = 97.23\%$, $\text{RMSE} = ₹1.3989\text{L}$, $\text{MAE} = ₹0.8835\text{L}$)
- **Microservice Port**: `http://localhost:5004`
- **Database**: SQLite3 (`source_code/data/predictions.db`)
- **Automated Tests**: 18/18 Passed (100% Pass Rate in 2.51s)
