# 02. System Requirements Specification (PROJECT-027)

## Functional Requirements (FR)
- **FR-1 [Curriculum Ingestion & Chunking]:** Ingest and chunk canonical Computer Science textbooks into 250-400 word segments with rich metadata (document ID, chapter, section, page).
- **FR-2 [Dense Vector Encoding]:** Encode queries and passages into 128-dimensional L2-normalized embeddings using PyTorch `AcademicDenseEncoder`.
- **FR-3 [Hybrid Search Fusion]:** Blend dense cosine similarity with sparse inverted BM25 lexical matching via convex combination: $S_{	ext{hybrid}} = 0.70 \cdot S_{	ext{dense}} + 0.30 \cdot S_{	ext{bm25}}$.
- **FR-4 [Grounded Response Synthesis]:** Synthesize factual academic responses strictly conditioned on top-K retrieved passages, eliminating ungrounded hallucinations.
- **FR-5 [Verifiable Attribution]:** Explicitly format citations with document title, authors, edition, chapter, section, and page number for every retrieved source.
- **FR-6 [Relational ACID Persistence]:** Record all questions, synthesized answers, latencies, and foreign-key linked citation records in SQLite `academic_rag.db`.
- **FR-7 [Interactive Web Telemetry]:** Provide an interactive web interface on Port 5027 with preset chips, real-time KPI metrics, and Chart.js similarity bar charts.

## Non-Functional Requirements (NFR)
- **NFR-1 [Vector Retrieval Latency]:** Dense cosine similarity over 5,000 chunks must execute in under 3.0 milliseconds on commodity CPU hardware.
- **NFR-2 [End-to-End Latency]:** Total query roundtrip (vectorization, retrieval, synthesis, database logging) must complete under 50 milliseconds.
- **NFR-3 [Hallucination Resistance]:** Answers must cite only passages physically present in the SQLite knowledge base; out-of-scope queries must report low confidence.
- **NFR-4 [Database Concurrency]:** Database must operate in WAL mode with a 30-second busy timeout to prevent write locks during concurrent queries.
