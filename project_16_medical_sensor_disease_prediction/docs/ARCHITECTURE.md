# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

PROJECT-016 is a decoupled, microservice-oriented clinical diagnostic and medical sensor monitoring platform. It combines high-throughput digital signal processing, deep 1D Residual Convolutional Neural Networks (ResNet-1D), and an evidence-based clinical decision support system.

```
+-----------------------------------------------------------------------------------+
|                        CLINICAL WEB DASHBOARD (PORT 5173)                         |
|     TanStack Start + React 19 + Tailwind CSS + Recharts Lead II Waveform Canvas   |
+-----------------------------------------------------------------------------------+
                                        |  RESTful JSON API / Reverse Proxy
                                        v
+-----------------------------------------------------------------------------------+
|                    NODE.JS EXPRESS API GATEWAY (PORT 5016)                        |
|  /api/health | /api/ecg | /api/predictions | /api/recommendations | /api/alerts   |
+-----------------------------------------------------------------------------------+
         |                                                 |
         v (HTTP /predict, Port 5017)                      v (better-sqlite3 WAL)
+-----------------------------------------+       +---------------------------------+
|      PYTORCH 1D CNN MICROSERVICE        |       |        RELATIONAL SQLITE DB     |
|                                         |       |                                 |
|  - 141,221-parameter ResNet-1D          |       |  - ecg_recordings (metadata)    |
|  - Butterworth Filter (0.5-40Hz)        |       |  - predictions (inferences)     |
|  - Pan-Tompkins QRS Peak Detector       |       |  - measurements (IoT telemetry) |
|  - 187-Sample Beat Slicing & Norm       |       |  - recommendations (guidance)   |
|  - AAMI 5-Class Softmax Probabilities   |       |  - alerts (clinical notifications)|
+-----------------------------------------+       +---------------------------------+
```

## 2. Component Specifications

### 2.1 Clinical Frontend (`pixel-perfect-pixels`)
- **Runtime & Framework**: Node.js / Bun runtime, TanStack Start, React 19, Tailwind CSS.
- **Port Allocation**: Port 5173 (`http://localhost:5173`).
- **Data Visualizations**: Recharts interactive time-series plots rendering Lead II ECG signals at 360 Hz with pan/zoom.
- **Biometric Telemetry**: Live cards tracking Heart Rate, Blood Pressure, SpO2, and Respiration.
- **Audit Views**: Tabular history tracking all past recordings, classifications, and clinical recommendations.

### 2.2 Node.js Express API Gateway (`backend`)
- **Runtime**: Node.js v18+ ESM modules with Express framework.
- **Port Allocation**: Port 5016 (`http://localhost:5016`).
- **Defensive Invariants**: Enforces strict Non-Fabrication Invariant (HTTP 503 when ML model disconnected).
- **Storage Management**: Streaming multipart uploads via Multer to `./storage/ecg` with path traversal sanitization.
- **Input Validation**: Express middleware validating physiological parameters.

### 2.3 Deep Learning Inference Service (`ml-model`)
- **Runtime**: Python 3.10+ with PyTorch 2.0+.
- **Port Allocation**: Port 5017 (`http://localhost:5017`).
- **Model Architecture**: ResNet-1D (141,221 parameters across 3 Residual Blocks with skip connections).
- **Endpoints**:
  - `GET /health`: Verifies model weights load status and readiness.
  - `POST /predict`: Ingests raw ECG file or sample vectors, runs Butterworth filtering and Pan-Tompkins peak detection, and outputs AAMI class probabilities.

### 2.4 Relational Database (`storage/medical.db`)
- SQLite database configured in Write-Ahead Logging (WAL) mode.
- Strict foreign key constraints and transactional consistency.
