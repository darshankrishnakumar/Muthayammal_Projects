# Telemetry Benchmark Dataset (6,000 Records)

## Dataset Specifications
- **File Location**: `source_code/data/document_forgery_telemetry_6000.csv`
- **Total Records**: Exactly 6,000 rows (plus header row).
- **Class Balance**:
  - 3,000 Authentic Documents (50.0%).
  - 3,000 Manipulated / Forged Documents (50.0%).
- **Forgery Vector Breakdown**:
  - 1,000 Copy-Move Manipulations (`COPY_MOVE`).
  - 1,000 Splicing Insertions (`SPLICING`).
  - 1,000 Inpainted Text Erasures (`TEXT_ERASURE`).
- **Document Category Distribution**:
  - 1,500 Invoices (`INVOICE`).
  - 1,500 Identification Cards (`IDENTITY_CARD`).
  - 1,500 Academic Certificates (`ACADEMIC_CERTIFICATE`).
  - 1,500 Legal Contracts (`CONTRACT`).
- **Scalers & Metadata**:
  - `forgery_scalers.json`: Precomputed Z-score normalization parameters.
  - `model_metadata.json`: Model architecture, parameter counts, and validation benchmarks.
