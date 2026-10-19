# PROJECT-014: Explainable Fake News Detection & Linguistic Stylometry

[![Status](https://img.shields.io/badge/Status-VERIFIED%20COMPLETE-emerald.svg)]()
[![Tests](https://img.shields.io/badge/Tests-27%2F27%20Passed%20(100%25)-emerald.svg)]()
[![Port](https://img.shields.io/badge/Port-5014-indigo.svg)]()
[![Model](https://img.shields.io/badge/Model-Passive--Aggressive%20Classifier-blue.svg)]()
[![Accuracy](https://img.shields.io/badge/Validation%20Accuracy-96.2%25-green.svg)]()

## Overview
**VeriNews AI** is an advanced NLP and Explainable AI (XAI) platform designed to detect fabricated news headlines and articles through intrinsic linguistic stylometry and high-dimensional linear margin optimization. 

Unlike traditional platforms that rely on easily bypassed domain blacklists or opaque deep learning black boxes, VeriNews AI provides:
1. **Explainable AI (XAI)**: Exact token-level mathematical attribution ($w_i \cdot x_i$) showing the words that swayed the verdict.
2. **Beyond Blacklists Mode**: Automatic detection and stripping of publisher watermarks (e.g., `- The New York Times`) to evaluate pure linguistic syntax.
3. **Intuitive Stylometric Radars**: 4 signal meters measuring sensationalism, speculative hearsay, formatting hysteria (% CAPS), and information density.
4. **Sub-5ms Inference**: Passive-Aggressive classifier operating across 146,627 vocabulary dimensions.
5. **Relational SQLite Persistence**: Full transaction logging in `fake_news.db`.

## Quick Start
```bash
# Navigate to source code
cd source_code

# Install requirements
pip install -r requirements.txt

# Run server on port 5014
python app.py

# Run test suite (27 tests)
python -m pytest tests/ -v
```

## Documentation Suite
- [System Architecture](docs/architecture.md)
- [API Reference](docs/api_documentation.md)
- [Algorithmic Methodology](docs/model_methodology.md)
- [Linguistic Stylometry & XAI](docs/stylometry_and_xai.md)
- [Database Schema](docs/database_schema.md)
- [Test Plan & Evidence](docs/test_plan_and_evidence.md)
- [Installation Guide](docs/installation_and_deployment.md)
- [Verification Report](docs/verification_report.md)
