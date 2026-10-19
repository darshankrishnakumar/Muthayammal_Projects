# Project 32: Requirements Specification

## 1. Functional Requirements (FR)
- **FR-01 (Multivariate Ingestion)**: Ingest 8-dimensional telemetry streams (temperature °C, vibration RMS mm/s, discharge pressure bar, shaft RPM, oil viscosity cSt, ultrasonic acoustic emission dB, FFT harmonic ratio, bearing defect energy).
- **FR-02 (6-Class Fault Diagnostics)**: Classify incoming equipment states into: Normal Baseline, Outer Race Bearing Spall, Rotor Dynamic Imbalance, Hydraulic Cavitation Wear, Stator Winding Overheating, or Mechanical Coupling Looseness.
- **FR-03 (Remaining Useful Life Estimation)**: Quantify remaining operating life in hours (24 to 4,000 hrs) and days.
- **FR-04 (Health Score Computation)**: Output a bounded 0-100% health index reflecting multi-channel sensor degradation.
- **FR-05 (Automated Work Order Dispatch)**: Automatically issue maintenance work orders with technician assignments and corrective action protocols.
- **FR-06 (ACID Relational Storage)**: Persist all diagnostic inspections, telemetry snapshots, and work orders in SQLite with Write-Ahead Logging (WAL).

## 2. Non-Functional Requirements (NFR)
- **NFR-01 (Inference Latency)**: End-to-end forward pass latency $< 10$ milliseconds on CPU.
- **NFR-02 (Diagnostic Accuracy)**: Fault classification accuracy $> 95\%$ on held-out test data with zero false negatives on critical faults.
- **NFR-03 (High Concurrency)**: SQLite WAL mode (`PRAGMA journal_mode=WAL;`) ensuring non-blocking reads during continuous telemetry logging.
- **NFR-04 (Port Consistency)**: Operates strictly on allocated network port 5032.
