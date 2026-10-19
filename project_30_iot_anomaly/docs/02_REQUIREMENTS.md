# Project 30: Requirements Specification

## 1. Functional Requirements (FR)
- **FR-01 (Telemetry Capture)**: System must extract 8 continuous network telemetry features from IoT packet flows.
- **FR-02 (Unsupervised Baseline Profiling)**: Deep Autoencoder must compute reconstruction MSE error with an adaptive threshold (0.35).
- **FR-03 (Threat Signature Attribution)**: Deep Classifier must identify exact cyber-attack signatures (Mirai, SYN Flood, Port Scan, Exfil, SSH Brute Force).
- **FR-04 (Automated Quarantine)**: CRITICAL severity threats must automatically transition device status to `ISOLATED` and log quarantine rules.
- **FR-05 (Administrative Override)**: Administrators must be able to manually toggle device isolation status via REST API.
- **FR-06 (Persistence & Audit)**: All inspections, quarantine actions, and system logs must be stored in SQLite with WAL mode.

## 2. Non-Functional Requirements (NFR)
- **NFR-01 (Inference Latency)**: PyTorch forward pass latency must remain below 10ms (system end-to-end $< 50$ms).
- **NFR-02 (Detection Accuracy)**: Threat classification accuracy must exceed 95% on held-out test data.
- **NFR-03 (Storage Footprint)**: Total model weights must remain under 100 KB for direct execution on OpenWrt edge gateways.
- **NFR-04 (Zero Lock Contention)**: SQLite database must operate in WAL mode (`PRAGMA journal_mode=WAL;`).
