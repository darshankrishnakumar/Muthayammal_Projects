# Walkthrough Timestamps: Academic QA RAG System (PROJECT-027)

**System Designation:** Academic Question Answering System with Retrieval-Augmented Generation (RAG)  
**Dedicated Port:** Port 5027 (`http://127.0.0.1:5027/`)  
**Video Container:** `walkthrough/walkthrough_video.mp4` (H.264 / AAC, 1280x800, Exactly 180.000s / 03:00)

| Timestamp Interval | Phase | Feature Demonstrated | Visual & Technical Focus |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | Academic QA Cockpit & Telemetry Ribbon | Live metrics (5,000 chunks, 6 textbooks, 94.2% confidence, 1.25ms latency), preset query chips, and PyTorch Bi-Encoder architecture overview |
| **00:30 - 01:00** | Phase 2 | Deep Learning: Scaled Dot-Product Attention Query | Query on Transformers, sub-2ms vector retrieval from Vaswani et al. (DL-C03-004), 98.5% cosine match, and grounded synthesis |
| **01:00 - 01:30** | Phase 3 | Source Citations & Cosine Distribution Telemetry | Multi-source evidence inspection (Chapter 3, Page 4), excerpt verification, and Chart.js cosine similarity bar chart |
| **01:30 - 02:00** | Phase 4 | Systems Evaluation: Virtual Memory Paging & TLB | Query on Virtual Memory & Translation Lookaside Buffer from Silberschatz OS Concepts (OS-C18-142), hit/miss latency breakdown |
| **02:00 - 02:30** | Phase 5 | Algorithm Complexity & Distributed Raft Consensus | Evaluation of Dijkstra's O(V log V + E) running time (CLRS) and Raft Leader Election consensus logs (DDIA) |
| **02:30 - 03:00** | Phase 6 | Relational SQLite Ledger, Corpora Catalog & Verification | Scrolled view of indexed CS textbooks, SQLite ACID query history, audit logs, and 30/30 QA test suite verification |

*Status: Exact 180.0s recording rendered and verified via ffprobe.*
