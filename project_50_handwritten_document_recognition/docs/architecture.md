# System Architecture: PROJECT-050 Intelligent Document Processing Platform

## 1. High-Level System Architecture
The Intelligent Handwritten Document Recognition and Information Extraction Platform is structured as an enterprise-grade asynchronous microservice deployed on **Port 5050**.

```
                           [Handwritten Intake Form Scan (PDF/JPG)]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
         [DeepCRNNTextRecognizer]              [DocumentQualityAndLexicalScorerNet]
         • ConvNet Feature Extractor           • 12-Dimensional Physical Vector
         • Bi-GRU Sequence Context             • Optical Degradation & Slant
         • Linear CTC Logits (326,569 params)  • Quality & Review Head (12,580 params)
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             ▼
                              [LayoutLM Structural Entity Parser]
                                             │
                                             ▼
                               [FastAPI Gateway (Port 5050)]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
           [SQLite WAL Mode Storage]                 [Cryptographic Audit Ledger]
           • Table: processed_documents              • Continuous SHA-256 Hash Chain
           • 6,000 Verified Telemetry Rows           • Genesis Block #0 Seeding
```

## 2. Port Allocation
- **Assigned Port**: `5050`
- **Formula**: `5001 + 50 - 1 = 5050`
- **Transport**: HTTP/1.1 REST + WebSockets (`/api/ws`) for live broadcast.

## 3. Dual PyTorch Neural Engines
1. **DeepCRNNTextRecognizer**:
   - Parameters: 326,569
   - Convolutional blocks + Bidirectional GRU (hidden_dim=128) + 37-class CTC character projection.
2. **DocumentQualityAndLexicalScorerNet**:
   - Parameters: 12,580
   - Multi-task dense network with LayerNorm, dropout, and 4 specialized heads.
3. **Total Active Parameters**: 339,149 parameters.
