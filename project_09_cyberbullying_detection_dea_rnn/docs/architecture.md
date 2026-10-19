# System Architecture: DEA-RNN Cyberbullying Detection

## 1. High-Level System Overview
PROJECT-009 implements an end-to-end, multi-class cyberbullying triage platform designed for real-time microblog streams (specifically Twitter/X). The architecture combines Differential Evolutionary Algorithms (DEA) for global hyperparameter optimization with a 2-layer Bidirectional Gated Recurrent Unit (Bi-GRU) neural network enhanced with an Additive Token-Level Attention layer.

```
+-----------------------------------------------------------------------------------+
|                            TWITTER INGESTION STREAM                               |
|                  (Raw Tweets, Mentions, Slang, Slurs, Punctuation)                |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        TEXT NORMALIZATION & TOKENIZER                             |
|  - Regex Cleaning: URLs, @handles, #hashtags, punctuation                         |
|  - Vocabulary Mapping: 545 domain tokens with <PAD>=0, <UNK>=1                    |
|  - Sequence Formatting: Fixed window length (max_len = 40)                        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       PYTORCH DEA-RNN DEEP NEURAL NETWORK                         |
|  1. Embedding Layer: nn.Embedding(545, 64, padding_idx=0)                         |
|  2. Bidirectional GRU: nn.GRU(64, 64, num_layers=2, bidirectional=True)           |
|     -> 128-dimensional bilateral contextual representations                       |
|  3. Additive Token Attention: e_t = W_a * h_t -> alpha_t = softmax(e_t)           |
|     -> Dynamic context vector c = sum(alpha_t * h_t)                              |
|  4. Dense Classification Head: Linear(128, 64) -> ReLU -> Dropout(0.3)           |
|     -> Linear(64, 6) -> Softmax Probabilities                                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         TRI-TIER MODERATION GOVERNANCE                            |
|  - APPROVED FOR BROADCAST: Clean / Safe content (severity < 0.10)                 |
|  - FLAGGED FOR HUMAN MODERATION: Ambiguous/moderate toxicity (0.50 <= sev < 0.80) |
|  - AUTOMATIC ACCOUNT QUARANTINE: Severe identity slurs (severity >= 0.80)         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                 FASTAPI REST MICROSERVICE & PERSISTENCE (PORT 5009)               |
|  - Endpoints: /health, /api/stats, /api/metrics, /api/history, /api/predict       |
|  - Relational Database: SQLite3 (cyberbullying.db - scans table)                  |
|  - Responsive Web UI: Token Attention Heatmap, Probability Bars, Audit Ledger     |
+-----------------------------------------------------------------------------------+
```

## 2. Component Specifications
- **Framework**: PyTorch 2.14 / Torch MPS (Apple Silicon Acceleration & CPU Fallback).
- **Backend**: FastAPI 0.115+ running on Uvicorn (Port 5009).
- **Frontend**: Vanilla HTML5, CSS3 Custom Properties, Chart.js for distribution bars.
- **Database**: SQLite3 (`cyberbullying.db`) recording transaction timestamp, text, category, confidence, severity, action, and latency.
