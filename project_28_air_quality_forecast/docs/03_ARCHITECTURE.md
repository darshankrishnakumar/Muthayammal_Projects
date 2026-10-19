# 03. System Architecture & Topology Design (PROJECT-028)

```mermaid
flowchart TD
    subgraph SENSORY_INGESTION["1. Atmospheric Sensory Ingestion"]
        S["10 Global Stations (5,500 Hourly Records)"] --> F["10-Dimensional Feature Extraction"]
        F --> N["Z-Score Standardization (Means & Stds)"]
    end

    subgraph DEEP_LEARNING["2. Dual-Engine Deep Learning Core"]
        N --> W["24-Hour Sliding Temporal Window (1 x 24 x 10)"]
        W --> LSTM["ENGINE A: PyTorch 2-Layer BiLSTM (Sequence Forecaster)"]
        LSTM --> TRAJ["Future 24-Hour Trajectory (PM2.5, PM10, AQI)"]
        N --> MLP["ENGINE B: 4-Layer Hazard MLP Classifier"]
        MLP --> CLS["6-Class EPA Softmax Probability Distribution"]
    end

    subgraph DECISION_SUPPORT["3. Decision Support & Health Advisories"]
        TRAJ --> ADV["Clinical Health Recommendation Engine"]
        CLS --> ADV
        ADV --> MED["N95 Respirator, HEPA & Outdoor Advisories"]
    end

    subgraph STORAGE_DELIVERY["4. ACID Relational Storage & Delivery"]
        TRAJ --> DB["SQLite Database (air_quality.db WAL Mode)"]
        CLS --> DB
        MED --> UI["Interactive Web Dashboard (Port 5028)"]
        DB -.-> UI
    end
```

## Mathematical Formulations
- **Huber Loss Function ($\delta = 10.0$):**
  $$L_\delta(y, \hat{y}) = \begin{cases} 0.5 (y - \hat{y})^2 & \text{for } |y - \hat{y}| \le \delta \\ \delta (|y - \hat{y}| - 0.5 \delta) & \text{otherwise} \end{cases}$$
- **Softmax Hazard Probability:**
  $$P(y = c \mid \mathbf{x}) = \frac{\exp(z_c)}{\sum_{j=1}^6 \exp(z_j)}$$
