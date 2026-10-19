# Project 30: AI-Based IoT Device Anomaly Detection for Smart Home Security
## 1. Abstract & Executive Summary

The proliferation of Internet of Things (IoT) devices in residential spaces has vastly expanded the consumer attack surface. Connected endpoints (IP cameras, thermostats, locks, routers, and voice assistants) are prime targets for Mirai-style botnets, volumetric DDoS floods, credential brute-forcing, and covert data exfiltration.

Project 30 delivers an autonomous, edge-viable AI anomaly detection and Zero-Trust mitigation platform. Using an 8-dimensional network telemetry flow representation, the system deploys dual deep learning models in PyTorch:
1. `IoTAnomalyAutoencoder`: Unsupervised bottleneck autoencoder (8 -> 16 -> 8 -> 4 -> 8 -> 16 -> 8) measuring reconstruction MSE error against a dynamic 0.35 threshold.
2. `IoTThreatClassifier`: Deep residual multi-class threat classifier (9 -> 64 -> 64 -> 32 -> 6) achieving **100.0%** test accuracy across 6 cyber-threat states.

### Key Highlights
- **Real Dataset**: 5,500 network telemetry records across 6 IoT device profiles.
- **ACID Persistence**: SQLite database (`iot_security.db`) running in Write-Ahead Logging (WAL) mode.
- **Zero-Trust Containment**: Automatic MAC quarantine and port termination for critical threats.
- **Dedicated Port**: Bound to `http://127.0.0.1:5030/` with 31/31 passing automated tests (100% pass rate).
