# System Architecture & Technical Design

## Architectural Overview

Career Guidance AI is designed as a decoupled multi-tier architecture connecting an interactive frontend, Flask REST microservice, machine learning engine, domain knowledge base, and SQLite audit store.

```mermaid
flowchart TD
    subgraph Client Tier
        UserBrowser["Interactive Web Dashboard<br/>(Tailwind CSS / Glassmorphism)"]
        PresetPills["1-Click Preset Personas<br/>(Full-Stack, Cloud, Cyber, Data, UI)"]
    end

    subgraph Service Tier - Flask :5005
        Gateway["Flask REST Gateway"]
        PredictRoute["POST /api/predict"]
        PresetRoute["GET /api/presets"]
        HistoryRoute["GET/DELETE /api/history"]
        MetricsRoute["GET /api/metrics"]
        HealthRoute["GET /api/health"]
    end

    subgraph Machine Learning Engine Tier
        Engine["CareerGuidanceEngine"]
        Encoder["LabelEncoder Suite<br/>(Categorical Features)"]
        XGBoostMod["XGBoost Classifier"]
        RFMod["Random Forest (50 trees)"]
        DTMod["Decision Tree (CART)"]
        ProbabilityVector["34-Class Posterior Distribution"]
        TopKRanker["Top-K Alternative Ranker"]
    end

    subgraph Data & Persistence Tier
        SQLiteStore[("SQLite Store<br/>career_guidance.db")]
        KnowledgeBase[("Domain Knowledge Base<br/>ROLE_INSIGHTS (34 Roles)")]
        DatasetCSV[("20k Student Records<br/>career_pred.csv")]
        ModelCacheFile[("Serialized Weights<br/>model_cache.joblib")]
    end

    UserBrowser -->|HTTP Requests| Gateway
    PresetPills --> UserBrowser
    Gateway --> PredictRoute
    Gateway --> PresetRoute
    Gateway --> HistoryRoute
    Gateway --> MetricsRoute
    Gateway --> HealthRoute

    PredictRoute --> Engine
    Engine --> Encoder
    Encoder --> XGBoostMod
    Encoder --> RFMod
    Encoder --> DTMod
    XGBoostMod --> ProbabilityVector
    RFMod --> ProbabilityVector
    DTMod --> ProbabilityVector
    ProbabilityVector --> TopKRanker
    TopKRanker --> KnowledgeBase
    PredictRoute --> SQLiteStore
    HistoryRoute --> SQLiteStore
    Engine -.-> ModelCacheFile
    Engine -.-> DatasetCSV
```

## Architectural Highlights

1. **In-Memory Model Caching**:
   Serialized models, encoders, and metrics are bundled in `model_cache.joblib`, enabling cold-start inference within 30ms.

2. **Multi-Model Support**:
   Users can toggle between XGBoost, Random Forest, and Decision Tree via REST payload parameters (`model_name`).

3. **Fallback & Knowledge Augmentation**:
   Classifier outputs are mapped to `ROLE_INSIGHTS`, adding rich actionable metadata (certifications, salary, skills).
