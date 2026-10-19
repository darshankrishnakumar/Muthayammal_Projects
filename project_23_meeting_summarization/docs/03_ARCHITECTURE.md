# 03. System Architecture & Topology

## Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    A[Transcript Input / REST Client] -->|HTTP POST /api/summarize| B(Flask REST API - Port 5023)
    B --> C[Speaker Turn & Sentence Parser]
    
    C -->|Speaker Word Counts| D[Speaker Donut Analytics]
    C -->|Candidate Sentences| E[Sublinear TF-IDF Vectorizer<br/>917 unigram + bigram features]
    
    subgraph Parallel NLP Engine
        E -->|Sentence Vectors| F[TextRank Graph Centrality<br/>Cosine Similarity + PageRank]
        E -->|Utterance Vectors| G[Calibrated Dialogue Act Classifier<br/>Logistic Regression]
    end
    
    F --> H[Salient Sentence Extractive Summary]
    G --> I[Action Item & Decision Extractor]
    
    I -->|Task Vectors| J[Priority Classifier<br/>Critical / High / Medium / Low]
    I --> K[Assignee & Deadline Resolver]
    
    H --> L[Executive Summary Dossier]
    J --> L
    K --> L
    
    L -->|ACID Insert| M[(Relational SQLite 3 Database<br/>meetings.db)]
    L -->|Log Event| N[(System Audit Trail<br/>system_audit)]
    
    M --> O[Glassmorphic Management Dashboard]
    N --> O
```

## Component Architecture
1. **Frontend Cockpit:** HTML5, CSS3 Glassmorphism, Chart.js (Donut & Radar charts), Canvas wave animation.
2. **Backend API:** Python 3.12, Flask, Flask-CORS, Joblib deserializer.
3. **Machine Learning Pipeline:** `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)`, `LogisticRegression(C=2.5, class_weight='balanced')`.
4. **Graph Centrality Engine:** Pairwise cosine similarity matrix with 25-cycle power iteration PageRank ($d=0.85$).
5. **Database Storage:** Relational SQLite 3 operating with Write-Ahead Logging (WAL).
