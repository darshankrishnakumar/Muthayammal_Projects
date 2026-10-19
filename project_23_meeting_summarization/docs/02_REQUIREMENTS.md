# 02. System Requirements & Domain Scope

## Functional Requirements
1. **Multi-Speaker Transcript Ingestion:**
   - Ingests raw multi-speaker transcripts with bracketed/colon tags e.g., `[Sarah (Product Lead)]: ...` or `Marcus: ...`.
   - Normalizes text, splits utterances into candidate sentences, and computes speaker talk-time distribution.

2. **Graph-Based TextRank Centrality (Extractive Summary):**
   - Projects candidate sentences into sublinear TF-IDF vector space (917 features).
   - Constructs pairwise sentence cosine similarity matrix $W_{ij}$ and computes power-iteration PageRank centrality.
   - Extracts top salient sentences to form an objective, hallucination-free executive summary.

3. **Multi-Class Dialogue Act Classification:**
   - Classifies utterances into four acts: `ACTION_ITEM`, `DECISION`, `DISCUSSION`, `GENERAL_STATEMENT`.
   - Output calibrated posterior class probability distributions.

4. **Action Item Parsing & Ownership Attribution:**
   - Detects assignees from speaker turns or in-predicate named syntax.
   - Predicts priority tiers (Critical, High, Medium, Low).
   - Extracts temporal deadlines (e.g. Tomorrow 10 AM, Friday 5 PM, End of Sprint).

5. **Decision & Consensus Mining:**
   - Filters consensus agreements into a distinct decision register.

6. **Conversational Diagnostics & Quality Profiling:**
   - Computes Shannon entropy over speaker turn probability distribution to measure participation equity and engagement.
   - Computes collaborative vs blocker token sentiment ratios.
   - Renders 5-axis Radar Quality Profile (Engagement, Clarity, Task Density, Consensus, Compression).

7. **Transactional Persistence & Auditing:**
   - Relational SQLite 3 storage across 4 tables (`meetings`, `action_items`, `decisions`, `system_audit`).
   - Generates downloadable Markdown meeting minutes.

## Non-Functional Requirements
- **Latency:** < 5ms end-to-end processing per meeting transcript.
- **Hardware Footprint:** Zero GPU requirement, < 45 MB total RAM usage.
- **Port Assignment:** Dedicated binding on Port 5023.
- **Reliability:** 100% verification pass rate across automated QA test suite.
