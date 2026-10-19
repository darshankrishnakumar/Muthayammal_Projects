# 03. System Architecture & Topology Design (PROJECT-027)

```mermaid
flowchart TD
    subgraph INGESTION["1. Academic Knowledge Ingestion"]
        A["6 CS Canonical Textbooks (5,000 Chunks)"] --> B["Academic N-Gram Tokenizer"]
        B --> C["PyTorch Dense Bi-Encoder (128D)"]
        C --> D["Dense Vector Index (NPZ Matrix / FAISS)"]
        B --> E["Sparse Inverted BM25 Lexical Index"]
    end

    subgraph QUERY_PROCESSING["2. Query Vectorization & Hybrid Retrieval"]
        Q["Student / Researcher Query"] --> QT["Query Preprocessing & Tokenization"]
        QT --> QE["Bi-Encoder Neural Projection (128D)"]
        QE --> VS["Vector Cosine Dot-Product (BLAS)"]
        D -.-> VS
        QT --> BM["BM25 Lexical Inverted Matcher"]
        E -.-> BM
        VS --> HF["Hybrid Rank Fusion (0.70 Dense + 0.30 BM25)"]
        BM --> HF
    end

    subgraph SYNTHESIS["3. Grounded Synthesis & Citation Binding"]
        HF --> TOPK["Top-K Evidence Chunks (K=3)"]
        TOPK --> SYN["Academic Synthesis Engine (No Hallucinations)"]
        SYN --> CIT["Chunk Provenance & Citation Formatter"]
    end

    subgraph STORAGE["4. ACID Persistence & Web Delivery"]
        CIT --> DB["SQLite Database (academic_rag.db)"]
        SYN --> UI["Web UI Dashboard (Port 5027)"]
        CIT --> UI
        DB -.-> UI
    end
```

## Hybrid Scoring Formulation
The retrieval score for chunk $d$ given query $q$ is defined as:
$$S_{	ext{hybrid}}(d, q) = lpha \cdot \cos(\mathbf{e}_q, \mathbf{e}_d) + (1 - lpha) \cdot rac{	ext{BM25}(d, q)}{\max_{d'} 	ext{BM25}(d', q)}$$
where $lpha = 0.70$ balances semantic generalization with keyword precision.
