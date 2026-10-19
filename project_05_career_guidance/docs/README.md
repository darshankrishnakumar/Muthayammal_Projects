# Career Guidance AI: Student Career Path Recommendation System

Welcome to the official technical documentation suite for **PROJECT-005: Career Guidance App for Students - AI Assisted**.

Career Guidance AI is an intelligent machine learning system designed to eliminate career ambiguity for engineering undergraduates by modeling 38 multi-modal academic and cognitive parameters into 34 technology career pathways.

---

## Documentation Index

1. [System Architecture](architecture.md) - Pipeline design, microservice endpoints, and dataflow diagrams.
2. [Dataset and Model Details](dataset_and_model_details.md) - 20,000 student records, feature engineering, and model benchmarks.
3. [REST API Documentation](api_documentation.md) - Flask microservice specifications on Port 5005.
4. [Setup and Execution Guide](setup_and_execution.md) - Installation instructions, dependency management, and server execution.
5. [Testing & Verification Report](testing_report.md) - 18 automated pytest cases, sub-50ms latency, and CRUD flow.
6. [Limitations and Future Work](limitations_and_future_work.md) - Known boundaries, LLM resume parsing, and market indexing.
7. [Third-Party Notices](third_party_notices.md) - Open-source licensing register and research paper citations.
8. [Acceptance Sign-Off Report](acceptance_report.md) - Final engineering verification against all 15 audit criteria.

---

## Executive Overview

- **Project Identifier**: `PROJECT-005`
- **Domain**: Educational Technology / Applied Machine Learning / Decision Support
- **Core Algorithms**: XGBoost, Random Forest (50 trees), Decision Tree (CART)
- **Target Roles**: 34 Technology Specializations
- **Microservice Port**: `http://localhost:5005`
- **Database**: SQLite3 (`source_code/career_guidance.db`)
- **Automated Tests**: 18/18 Passed (100% Pass Rate in 1.04s)
