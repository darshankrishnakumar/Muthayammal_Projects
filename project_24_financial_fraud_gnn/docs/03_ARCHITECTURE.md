# 03. System Architecture & Component Design

## High-Level Architecture Diagram
```
+------------------------------------------------------------------------+
|                     CLIENT APPLICATION LAYER (PORT 5024)               |
|  - Force-Directed Canvas Physics Engine (HTML5 Canvas + Euler Euler)   |
|  - Forensic Account Inspector Drawer (Ledger History & GNN Explanations)|
|  - Syndicate Pattern Hunter (Cycle Traversal & Camera Auto-Focus)      |
|  - Latent Embedding Space Matrix Table & FinCEN SAR Regulatory Ledger  |
+-----------------------------------+------------------------------------+
                                    | Asynchronous JSON / REST
                                    v
+------------------------------------------------------------------------+
|                      FLASK REST APPLICATION SERVICE                    |
|  - Endpoints: /api/health, /api/graph, /api/node/<id>, /api/export/sar |
|  - Sanctions Engine: /api/account/freeze, /api/account/unfreeze        |
|  - Synthetic Ring Injector: /api/simulate/ring                         |
+-------------------+--------------------------------+-------------------+
                    |                                |
                    v                                v
+-----------------------------------+  +---------------------------------+
|     SPECTRAL GNN ML ENGINE        |  |  RELATIONAL SQLITE PERSISTENCE  |
|  - PyTorch 2-Layer GCN            |  |  - Database: fraud_graph.db     |
|  - Symmetrized Adjacency Norm     |  |  - Tables: accounts, transactions|
|  - Latent Vector Extraction H^(1) |  |    syndicates, frozen_sanctions |
|  - 8-Dim Scaled Topological Feats |  |    system_audit                 |
+-----------------------------------+  +---------------------------------+
```

## Component Breakdown
1. **`app.py`:** Main Flask application entrypoint binding to Port 5024.
2. **`gnn_model.py`:** PyTorch Graph Convolutional Network architecture (`FinancialGCN`), feature extraction, and forensic explainability.
3. **`database.py`:** SQLite database wrapper handling schema creation, CSV seeding, CRUD operations, and transactional audit trails.
4. **`train_and_save_gnn.py`:** Standalone reproducible dataset generator and PyTorch GCN training pipeline.
5. **`index.html`:** Single-page frontend dashboard with force-directed graph canvas physics.\n