# 04. Data Pipeline & Corpus Engineering

## Corpus Synthesis Methodology
To train the dialogue act and priority models, 6,000 multi-meeting dialogue utterances were synthesized in `source_code/data/train_and_save_models.py` spanning four distinct meeting genres: Executive Architecture Review, Sprint Planning & Blocker Triage, Product Launch Retrospective, and DevOps Incident Postmortem.

### Corpus Characteristics
- **Total Records:** 6,000 meeting dialogue utterances.
- **Vocabulary Dimensions:** 917 unigrams and bigrams.
- **Labels:** `dialogue_act` (`ACTION_ITEM`, `DECISION`, `DISCUSSION`, `GENERAL_STATEMENT`), `priority` (`Critical`, `High`, `Medium`, `Low`).

### Class Distribution
| Dialogue Act | Percentage | Sample Count | Semantic Purpose |
|---|---|---|---|
| `ACTION_ITEM` | 36.2% | 2,171 | Task commitments, assignments, deadlines |
| `DECISION` | 24.4% | 1,465 | Consensus agreements, architectural approvals |
| `DISCUSSION` | 24.4% | 1,464 | Technical debates, trade-offs, metrics review |
| `GENERAL_STATEMENT` | 15.0% | 900 | Greetings, protocol checks, administrative |
| **Total** | **100%** | **6,000** | |
