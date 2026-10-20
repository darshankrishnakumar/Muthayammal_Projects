# EPA & ASTM D5231 Regulatory Compliance Guide

## 1. Applicable Standards
- **EPA 40 CFR Part 246**: Guidelines for the Source Separation of Materials for Recovery.
- **ASTM D5231**: Standard Test Method for Determination of the Composition of Unprocessed Municipal Solid Waste.
- **ISO 14064-1**: Greenhouse Gas Quantification and Avoided Emissions Reporting.

## 2. Compliance Mapping Matrix
| Requirement | Standard | SORT-AI Implementation |
|---|---|---|
| Material Stream Segregation | EPA 40 CFR §246.200 | Automated sorting into 6 pure material streams with >98% accuracy |
| Purity & Contamination Limits | ASTM D5231 | Continuous Contamination Risk Regressor flagging cross-material batches |
| Carbon Offset Accounting | ISO 14064-1 | Embodied carbon calculation per classified item based on EPA WARM model |
| Chain-of-Custody Integrity | NIST SP 800-88 | SHA-256 cryptographic hash chains on all dispatch and audit records |
