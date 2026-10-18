# PROJECT 44: Intelligent Resume Screening and Job Matching Using Natural Language Processing

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Contextual Transformer NLP Applicant Tracking System & Objective Skill Matching Engine.**

```
        [Candidate Resume (PDF/DOCX)]
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
[Skill Entity Extractor]   [Job Description Model]
• Experience Normalizer    • Required Competency Set
• Demographic Anonymizer   • Seniority Weighting
        │                           │
        └─────────────┬─────────────┘
                      ▼
     [SBERT Transformer Semantic Matcher]
                      │
                      ▼
      [Objective Match Score & Ranking]
```

## Quickstart
```bash
cd College_44
pip install -r requirements.txt
python run_system.py --port 8044
```
Dashboard at [http://localhost:8044](http://localhost:8044)
