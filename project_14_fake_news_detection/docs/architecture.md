# System Architecture & Technical Design

## 1. High-Level Architecture Overview

VeriNews AI (PROJECT-014) is an industrial-strength, explainable fake news detection and linguistic stylometry platform. It is engineered with Python 3.12, Flask, Scikit-Learn, NLTK, and SQLite, and runs on dedicated Port 5014.

```
+-----------------------------------------------------------------------------------+
|                        VERINEWS AI WEB APPLICATION                                |
|        Tailwind CSS, FontAwesome, Dual-Spectrum Gauge, Interactive Word Pills     |
+-----------------------------------------------------------------------------------+
                                        |  HTTP / REST (Port 5014)
                                        v
+-----------------------------------------------------------------------------------+
|                         FLASK APPLICATION MICROSERVICE                            |
|       / | /predict | /api/health | /api/predict | /api/history | /api/stats       |
+-----------------------------------------------------------------------------------+
                   |                                             |
                   v                                             v
+---------------------------------------+       +-----------------------------------+
|         NLP & XAI ENGINE              |       |       DATABASE SUBSYSTEM          |
|                                       |       |        (fake_news.db)             |
|  - Source Watermark Stripper (Regex)  |       |  - 'verifications' Table          |
|  - NLTK Tokenizer & WordNet Lemmatizer|       |  - B-Tree Indexes on Timestamp    |
|  - 146,627-dim TF-IDF Vectorizer      |       |  - Stylometric Audit Logging      |
|  - Passive-Aggressive Hyperplane Model|       |  - ACID Transactional Persistence |
|  - Linear Impact Weights (w_i · x_i)  |       +-----------------------------------+
|  - 4-Signal Stylometric Radar Engine  |
+---------------------------------------+
```

## 2. Component Specifications

### 2.1 Backend Server (source_code/app.py)
A lightweight microservice running on port 5014. Exposes REST JSON APIs and dynamic server-rendered HTML pages with sub-5 millisecond response times.

### 2.2 NLP Feature Preprocessor
- Regex publisher watermark stripper to prevent source-label bias.
- WordNet lemmatizer and stopword filter with robust fallback handlers.
- Pre-trained TF-IDF vectorizer mapping text to 146,627 n-gram vocabulary features.

### 2.3 Passive-Aggressive Large-Margin Classifier
Large-margin linear model optimized for sparse high-dimensional text classification with hinge loss and online aggressive margin updates.

### 2.4 Explainable AI (XAI) Attribution Subsystem
Computes exact token directional contribution $w_i \cdot x_i$ and normalizes impact percentages. Tokens pushing toward FAKE are flagged in rose, while tokens pulling toward REAL are marked in emerald.

### 2.5 Verification Audit Ledger (source_code/data/fake_news.db)
Relational SQLite database maintaining immutable audit logs of all historical headlines evaluated by the system.
