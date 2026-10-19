# 03. System Architecture & Topology

## Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    A[Customer Ingestion / REST Client] -->|HTTP POST /api/classify| B(Flask REST API - Port 5022)
    B --> C[Sublinear TF-IDF Vectorizer<br/>2,603 unigram + bigram features]
    C --> D[Feature Vector x]
    
    subgraph Dual-Head NLP Engine
        D -->|Vector x| E[Head 1: Category Classifier<br/>Calibrated Multinomial Logistic]
        D -->|Vector x| F[Head 2: Priority Classifier<br/>Calibrated Multinomial Logistic]
    end
    
    E --> G[Category Posterior Probabilities<br/>P_cat in R^6]
    F --> H[Priority Distribution<br/>P_prio in R^4]
    
    G --> I[SLA Policy & Urgency Engine]
    H --> I
    
    I --> J[Triage Ticket Payload]
    J -->|ACID Insert| K[(Relational SQLite 3 Ledger<br/>complaints.db)]
    J -->|Log Event| L[(Append-Only Audit Trail<br/>system_audit)]
    
    K --> M[Glassmorphic Management Dashboard]
    L --> M
```

## Layer Specifications
1. **Presentation Layer:** Semantic HTML5, CSS3 Glassmorphism, Chart.js 4.4, responsive flex/grid layouts.
2. **Application Layer:** Python 3.12, Flask, Flask-CORS, Joblib model deserialization, Scikit-Learn inference.
3. **Machine Learning Pipeline:** `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)`, `LogisticRegression(C=2.5, class_weight='balanced')`.
4. **Data Persistence Layer:** SQLite 3 in Write-Ahead Logging (WAL) mode, structured across 4 relational schemas (`complaints`, `departments`, `sla_policies`, `system_audit`).
