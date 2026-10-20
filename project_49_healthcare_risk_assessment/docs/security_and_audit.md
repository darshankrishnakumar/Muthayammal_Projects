# Security & HIPAA Audit — PROJECT-049
## SHA-256 Block Chained Clinical Ledger

### 1. Threat Model & Mitigations
- **Threat: Retrospective Diagnostic Manipulation**: Modifying a patient's risk tier or vital signs to alter insurance coverage or liability.
  - *Mitigation*: The block hash incorporates patient ID, vital signs, risk scores, and evidence hash. Modifying any field invalidates the block hash and breaks all subsequent links.
- **Threat: Sensor Telemetry Spoofing**: Submitting altered laboratory values.
  - *Mitigation*: All input biomarkers generate a SHA-256 evidence hash stored in the assessment and cross-referenced in the ledger block.
- **Threat: Concurrency Contention**: Multiple clinic terminals submitting simultaneous screenings.
  - *Mitigation*: SQLite WAL mode with serialized transactions ensures atomic block index increments without database locking.

### 2. Cryptographic Proof Scheme
Each block satisfies:
$$\text{block\_hash}_i = \text{SHA256}(i \parallel \text{block\_hash}_{i-1} \parallel \text{timestamp}_i \parallel \text{event}_i \parallel \text{details\_json}_i \parallel \text{evidence\_hash}_i)$$
With base case:
$$\text{block\_hash}_0 = \text{SHA256}(0 \parallel 0^{64} \parallel \text{timestamp}_0 \parallel \text{"GENESIS\_SEED"} \parallel \dots)$$
