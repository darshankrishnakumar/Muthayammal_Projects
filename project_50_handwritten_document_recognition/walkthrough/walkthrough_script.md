# Demonstration & Walkthrough Script: Intelligent Handwritten Document Recognition & Extraction (PROJECT-050)

## Overview
- **Project Identifier**: PROJECT-050
- **Directory**: `project_50_handwritten_document_recognition`
- **Assigned Port**: 5050
- **Primary Technology Stack**: Python 3.12, PyTorch (DeepCRNNTextRecognizer & DocumentQualityAndLexicalScorerNet), FastAPI, SQLAlchemy, SQLite WAL Mode, Tailwind CSS, Chart.js.
- **Video Duration Target**: Exactly 180.000000s (03:00.000, 720 frames @ 4.0 fps).

## Demonstration Timeline & Video Cue Script

### Phase 1: Title & System Overview (00:00 - 00:30 | Frames 000 - 120)
- Navigate to `http://127.0.0.1:5050/`.
- Display top navbar: "PROJECT 50: HANDWRITTEN RECOGNITION & EXTRACTION", NLP SOTA badge, Port: 5050 badge, SQLite WAL mode indicator.
- Review 4 live KPI cards: Processed Documents (6,000 records), Field Extraction Accuracy (94.5%), Word & Character Error Rate (CER: 4.2%, WER: 7.8%), Parsing Latency (16.5 ms).
- Smooth scroll down to overview workstation layout.

### Phase 2: LayoutLM Spatial Bounding Box & Degradation HUD (00:30 - 01:00 | Frames 120 - 240)
- Highlight the 2D Spatial Grid (1280x800) Bounding Box virtual canvas showing real-time extraction targets (NAME, DIAGNOSIS, TOTAL, SIGNATURE).
- Center on Chart.js Optical Handwriting & Pen Stroke Degradation HUD.
- Display contrast ratio, stroke width variance, background SNR (dB), baseline slant angle, ink density, and signature stroke coverage.

### Phase 3: Live Form Intake — Dr. Jonathan Hayes & Global Supplies Ltd (01:00 - 01:30 | Frames 240 - 360)
- Select Preset 1: Dr. Jonathan Hayes (Hospital Clinical Intake — Clean SOTA).
- Click "Run Deep CRNN OCR & LayoutLM Extraction".
- Observe instant PyTorch forward pass: Extracted Name, Primary Diagnosis (Acute Bronchitis), 96.2% lexical confidence, 88.5 quality score, SIG VERIFIED badge, and zero human review requirement.
- Select Preset 2: Global Supplies Ltd (Handwritten Commercial Invoice).
- Run extraction: Commercial credit facility verified, $1,450.00 total amount extracted, clean audit logging.

### Phase 4: Critical Intake — Arthur Pendelton & Cursive Escalation (01:30 - 02:00 | Frames 360 - 480)
- Select Preset 3: Arthur Pendelton (Insurance Claim Reimbursement).
- Run extraction: Emergency ER consultation verified, high-quality signature confirmed.
- Select Preset 4: Anonymous Respondent #42 (Survey Sheet — Degraded Cursive Slant).
- Observe degradation simulation: Quality score drops to 34.1 / 100 with 19% occlusion, review risk spikes to 99.9%.
- System triggers "Escalated to Human Review" status and SIG UNVERIFIED warning, demonstrating automated review gating.

### Phase 5: Parsed Document Registry & SQLite WAL Mode (02:00 - 02:30 | Frames 480 - 600)
- Scroll to Parsed Document Registry table displaying real rows from SQLite `processed_documents`.
- Inspect columns: Doc ID, Template Archetype, Extracted Name, Diagnosis / Purpose, Date, Quality, Confidence, Review Required, and Ready Status.
- Confirm ACID persistence and zero table locks under SQLite Write-Ahead Logging mode.

### Phase 6: Cryptographic Audit Ledger & SHA-256 Hash Chaining (02:30 - 03:00 | Frames 600 - 720)
- Scroll to Cryptographic Audit Ledger table.
- Verify Genesis Block #0 (seeded with 64-char zero previous hash).
- Confirm continuous SHA-256 block hash chaining where Block N previous_hash strictly matches Block N-1 block_hash.
- Highlight "HASH CHAIN VERIFIED" badge and total blocks counter.
- Conclude video demonstration at exactly 180.000000 seconds.
