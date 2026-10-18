# PROJECT 47: Intelligent Classroom Engagement Analysis Using Facial Expression and Activity Recognition

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Privacy-Preserving Multimodal Affective Computing, Classroom Attentiveness Index & Real-Time Intervention AI.**

```
        [Classroom Video Camera Feed]
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
[Facial Expression Stream]   [Head Pose & Posture Stream]
• Attentive / Bored / Drowsy • Yaw / Pitch / Roll (Board Gaze)
• Anonymized Feature Vectors • Note Taking / Slumping Motion
        │                           │
        └─────────────┬─────────────┘
                      ▼
         [Multimodal Fusion Network]
                      │
                      ▼
      [Class Engagement Index & Interventions]
```

## Quickstart
```bash
cd College_47
pip install -r requirements.txt
python run_system.py --port 8047
```
Dashboard at [http://localhost:8047](http://localhost:8047)
