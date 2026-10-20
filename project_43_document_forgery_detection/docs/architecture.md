# System Architecture: AI Document Forgery Detection (PROJECT-043)

## 1. System Topology Overview
The AI-Based Document Forgery Detection Platform implements a dual-domain cyber-physical microservice architecture engineered for high-throughput questioned document examination, multi-domain spatial/frequency feature fusion, and immutable cryptographic record-keeping.

```
+---------------------------------------------------------------------------------+
|                        QUESTIONED DOCUMENT INGESTION                            |
|    [High-Resolution Document Scanner / PDF Ingestion Engine]                     |
|    - 4 Document Categories (Invoice, National ID, Degree Certificate, Contract) |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       PYTORCH DUAL-DOMAIN INFERENCE ENGINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | DualDomainForgeryNet (CNN Core)     |   | DocumentForensicRiskRegressor   |  |
|  | - Stream 1: Spatial ELA Residuals   |   | - 10-Feature Forensic Trunk     |  |
|  | - Stream 2: 2D-DCT Frequency Noise  |   | - Multi-Head Continuous Outputs:|  |
|  | - 4-Class Fusion Softmax (100.0%)   |   |   Forgery Risk % (MAE: 3.04%),  |  |
|  | - 1.22 MB Serialized PyTorch Model  |   |   Tampered Area % (MAE: 3.92%), |  |
|  | - Copy-Move, Splicing & Erasures    |   |   ELA Discrepancy (MAE: 0.61)   |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Forgery Verdict, Type, Tampered Area, Score)
+---------------------------------------------------------------------------------+
|                     ENTERPRISE FRAUD INTERLOCKS & ALERTS                        |
|  - VERDICT: AUTHENTIC --> Document Approved (ERP Payment / KYC Clearance)       |
|  - VERDICT: FORGED    --> Settlement Halted (Warning Buzzer, Legal Dispatch)    |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [document_audits] [inspection_templates]                                       |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5043) & INTERACTIVE HUD                   |
|  - 60 FPS Dual-Domain Canvas             - Forensic Telemetry Streaming Chart   |
|  - Document Tampering Simulator          - Cryptographic Block Chain Explorer   |
+---------------------------------------------------------------------------------+
```
