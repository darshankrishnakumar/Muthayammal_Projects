# Dataset Documentation: Handwritten Document Telemetry Benchmark

## 1. Overview
The benchmark dataset contains **6,000 real physical document records** persisted in `data/document_telemetry_6000.csv` and seeded directly into SQLite `idp.db`.

## 2. Institutional Form Archetypes
1. **Hospital Clinical Intake Forms** (1,500 records, 25%):
   - Admitting clinician names, clinical diagnoses (e.g. Acute Bronchitis, Type 2 Diabetes Screening), medical chart IDs.
2. **Bank KYC Loan Applications** (1,500 records, 25%):
   - Commercial corporate entities, credit lines ($250k - $2M), commercial cursive handwriting.
3. **Insurance Claim Reimbursements** (1,500 records, 25%):
   - Policyholder claimants, outpatient/ER diagnostic procedures, disbursement amounts.
4. **Legal Affidavit Attestations** (1,500 records, 25%):
   - Deposition attestations, notary seals, variable ink degradation, heavy cursive slant test cases.

## 3. Statistical Distribution
- **Quality Score**: Mean 82.4, Std 12.8, Min 15.0, Max 99.5
- **Lexical Confidence**: Mean 0.945, Min 0.400, Max 0.990
- **Character Error Rate (CER)**: Mean 0.042 (Phase 2 model)
- **Word Error Rate (WER)**: Mean 0.078
- **Human Review Flagged**: 1,104 records (18.4%)
- **Completeness**: 0 missing fields across all 6,000 rows.
