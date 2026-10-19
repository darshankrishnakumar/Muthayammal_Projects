# PROJECT-015: CardioPredict — Multi-Factor Heart Disease Diagnostic Platform

[![Status](https://img.shields.io/badge/Status-VERIFIED%20COMPLETE-emerald.svg)]()
[![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passed%20(100%25)-emerald.svg)]()
[![Port](https://img.shields.io/badge/Port-5015-blue.svg)]()
[![Model](https://img.shields.io/badge/Model-Random%20Forest%20(100%20Trees)-green.svg)]()
[![Accuracy](https://img.shields.io/badge/Validation%20Accuracy-89.1%25-green.svg)]()

## Overview
**CardioPredict** is a full-stack cardiovascular diagnostic intelligence platform that leverages Random Forest ensemble learning to assess coronary artery disease risk from 11 non-invasive physiological biomarkers.

### Key Capabilities
1. **Ensemble Machine Learning**: 100 bagged decision trees trained on 918 patient records with Gini impurity splitting.
2. **Clinical Risk Stratification**: Four-tier risk categorization (Low, Moderate, Elevated, High) based on continuous soft probabilities.
3. **Automated PDF Clinical Reports**: On-demand downloadable vector PDFs with tabular parameter comparisons and physician disclaimers.
4. **Interactive Chart.js Dashboards**: Vital Signs Comparison (Bar), Cardiovascular Profile (Radar), and Risk Distribution (Pie & Line).
5. **Integrated BMI Calculator**: Real-time anthropometric assessment with automated classification.
6. **Relational SQLite Registry**: Full transactional persistence in `heart_patients.db`.

## Quick Start
```bash
# Navigate to source code
cd source_code

# Install dependencies
pip install -r requirements.txt

# Start backend on port 5015
python app.py

# Run test suite (25 tests)
python -m pytest tests/ -v
```

## Documentation Suite
- [System Architecture](docs/architecture.md)
- [API Reference](docs/api_documentation.md)
- [Algorithmic Methodology](docs/model_methodology.md)
- [Clinical Features Data Dictionary](docs/clinical_features_dictionary.md)
- [Database Schema](docs/database_schema.md)
- [Test Plan & Evidence](docs/test_plan_and_evidence.md)
- [Installation Guide](docs/installation_and_deployment.md)
- [Verification Report](docs/verification_report.md)
