# 04. Academic Data Pipeline & Corpus Engineering (PROJECT-027)

## Curated Textbook Corpora
The knowledge base comprises 5,000 structured chunks across 6 canonical CS reference textbooks:

| Corpus ID | Reference Textbook | Domain Focus | Indexed Chunks | Page Range |
|---|---|---|---|---|
| `DOC-01` | *Attention Is All You Need* (Vaswani et al. 2017) | Deep Learning & NLP Transformers | 834 | 1 - 15 |
| `DOC-02` | *Operating System Concepts* (Silberschatz et al. 10th Ed) | Systems, Virtual Memory, Paging, TLB | 833 | 1 - 850 |
| `DOC-03` | *Introduction to Algorithms* (Cormen et al. CLRS 4th Ed) | Graph Algorithms, Dijkstra, Red-Black Trees | 833 | 1 - 1312 |
| `DOC-04` | *Database System Concepts* (Silberschatz et al. 7th Ed) | Relational ACID, Write-Ahead Logging, 2PC | 834 | 1 - 1376 |
| `DOC-05` | *Computer Networks* (Tanenbaum & Wetherall 6th Ed) | TCP Reno/Cubic, Congestion Control | 833 | 1 - 960 |
| `DOC-06` | *Designing Data-Intensive Applications* (Martin Kleppmann) | Raft Consensus, Replicated Logs | 833 | 1 - 616 |

## Data Serialization Artifacts
- **Corpus JSON:** `source_code/data/academic_corpus.json` (5,000 records with `chunk_id`, `text`, `chapter`, `page`, `topics`)
- **Dense Matrix:** `source_code/backend/academic_vector_index.npz` (5,000 x 128 float32 matrix)
- **Metadata JSON:** `source_code/backend/rag_metadata.json` (vocabulary, dimensions, metrics)
- **SQLite Database:** `source_code/backend/academic_rag.db` (5 relational tables)
