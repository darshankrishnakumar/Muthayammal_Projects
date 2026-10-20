# API Specification: PROJECT-050 RESTful Microservice

## Base URL
`http://127.0.0.1:5050`

## Endpoints

### 1. System Health Check
- **Endpoint**: `GET /api/health/`
- **Description**: Returns microservice operational status, assigned port, database WAL mode status, device acceleration (MPS/CUDA), and model parameter counts.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "Project 50 Handwritten Document IDP API",
  "project_id": "PROJECT-050",
  "port": 5050,
  "database_wal_mode": true,
  "cuda_available": false,
  "mps_available": true,
  "models": {
    "crnn_text_recognizer": "DeepCRNNTextRecognizer",
    "crnn_parameters": 326569,
    "quality_scorer": "DocumentQualityAndLexicalScorerNet",
    "quality_scorer_parameters": 12580,
    "total_parameters": 339149
  }
}
```

### 2. System Analytics Summary
- **Endpoint**: `GET /api/analytics/summary`
- **Description**: Computes live aggregate statistics from the SQLite database.
- **Response**:
```json
{
  "total_documents_processed": 6000,
  "human_review_queue_count": 1104,
  "average_transcription_confidence": 0.945,
  "average_quality_score": 82.4,
  "model_performance": {
    "character_accuracy_cer": 0.042,
    "word_accuracy_wer": 0.078,
    "processing_latency_ms": 16.5,
    "field_extraction_accuracy": 0.945
  }
}
```

### 3. Document Processing & Ingestion
- **Endpoint**: `POST /api/idp/process`
- **Request Body**:
```json
{
  "document_type": "HOSPITAL_CLINICAL_INTAKE",
  "patient_or_client_name": "Dr. Jonathan Hayes",
  "primary_diagnosis_or_purpose": "Acute Bronchitis",
  "date_field": "2026-10-12",
  "id_number": "MED-8842",
  "total_amount": "$350.00",
  "simulate_cursive_unclear": false
}
```
- **Response**: Returns document record, transcription, lexical confidence, quality score, review status, and SHA-256 audit block.

### 4. Cryptographic Audit Ledger
- **Endpoint**: `GET /api/idp/audit-logs?limit=50`
- **Response**: Returns list of verified blocks and boolean `chain_valid`.
