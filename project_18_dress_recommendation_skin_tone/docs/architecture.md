# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

PROJECT-018 is an enterprise-grade multi-modal personalized fashion recommendation platform. It combines a trained Gradient Boosting Machine (GBM) for category preference prediction, TF-IDF NLP textual modeling, optical melanin chromatic absorption theory, and anatomical silhouette geometry.

```
+-----------------------------------------------------------------------------------+
|                        FASHION STUDIO WEB UI (PORT 5018)                          |
|     Dark Glassmorphism UI + Preset Personas + Live Outfit Cards + XAI Forensics   |
+-----------------------------------------------------------------------------------+
                                         |  JSON REST API
                                         v
+-----------------------------------------------------------------------------------+
|                        FASTAPI ASYNCHRONOUS BACKEND (PORT 5018)                   |
|     /api/recommend | /api/catalogue | /api/models | /api/history | /health        |
+-----------------------------------------------------------------------------------+
          |                                                 |
          v                                                 v
+-----------------------------------------+       +---------------------------------+
|      MULTI-MODAL HYBRID ENGINE          |       |        RELATIONAL SQLITE DB     |
|                                         |       |                                 |
|  - Channel 1: TF-IDF Textual (35%)      |       |  user_data.db                   |
|  - Channel 2: GBM Category Model (30%)  |       |  - USER_PROFILE                 |
|  - Channel 3: Melanin Harmony (20%)     |       |  - BODY_MEASUREMENTS            |
|  - Channel 4: Silhouette Geometry (15%) |       |  - USER_PREFERENCES             |
|  - Multi-Component Score Synthesis      |       |  - RECOMMENDATION_HISTORY       |
+-----------------------------------------+       +---------------------------------+
```

## 2. Key Modules
- **FastAPI Engine (`server.py`)**: Asynchronous REST endpoints, Jinja2 template rendering, static file serving for outfit photographs.
- **Hybrid Recommendation Engine (`backend/recommendation_engine.py`)**: Convex score fusion uniting NLP, ML, and rule-based heuristic channels.
- **Gradient Boosting Classifier (`backend/gbm_recommender.py`)**: Serialized 1.5MB pipeline trained on 1,000 multi-attribute consumer purchase cycles.
- **Profile Manager (`backend/profile_manager.py`)**: ACID relational transaction logging in SQLite (`user_data.db`).
