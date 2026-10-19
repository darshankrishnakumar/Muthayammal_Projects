# 06. REST API Specification (PROJECT-027)

The backend provides a RESTful interface over HTTP on assigned Port 5027:

### 1. `GET /api/health`
Returns system status, model architecture, active port, and indexed chunk counts.
```json
{
  "status": "healthy",
  "port": 5027,
  "service": "Academic Retrieval-Augmented Generation (RAG) System API",
  "architecture": "Dense Bi-Encoder (PyTorch) + Hybrid Lexical BM25 Ranking",
  "indexed_documents": 6,
  "total_chunks": 5000,
  "embedding_dimension": 128
}
```

### 2. `POST /api/ask`
Submits an academic query for hybrid retrieval and grounded synthesis.
```json
// Request
{ "question": "Explain how Scaled Dot-Product Attention works in Transformers" }

// Response
{
  "question": "Explain how Scaled Dot-Product Attention works in Transformers",
  "answer": "Based on **Attention Is All You Need** (Chapter 3, Page 4)...",
  "primary_source": { "doc_name": "Attention Is All You Need", "chunk_id": "DL-C03-004", "page": 4 },
  "top_sources": [
    { "doc_name": "Attention Is All You Need", "chunk_id": "DL-C03-004", "relevance_pct": 98.5, "page": 4 }
  ],
  "confidence": 0.985,
  "retrieval_latency_ms": 1.25,
  "tokens_generated": 142
}
```

### 3. `GET /api/stats`
Returns corpus statistics, query count, average confidence, and latency metrics.

### 4. `GET /api/documents`
Lists all 6 canonical indexed textbooks with chunk distributions and keyword topics.

### 5. `GET /api/history`
Returns recent question answering queries and linked citation records.
