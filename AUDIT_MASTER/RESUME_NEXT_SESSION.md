# Resume Instructions for Next Step / Session

## Current Status
- **PROJECT-001**: **100% VERIFIED COMPLETE**.
  - Code, dataset, models, database, backend (port 5001), frontend, 18/18 tests, 02:37 MP4 walkthrough video, 15-slide PPTX with screenshots, DOCX documentation, and master trackers all updated and verified.
- **Next Project to Execute**: **`PROJECT-002: network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection`**

---

## Action Plan for PROJECT-002
1. **Directory**: `project_02_network_intrusion_anomaly`
2. **Inspect Existing State**:
   - Check existing files, code, datasets, tests, docs, PPTX.
3. **Acquire Real Dataset**:
   - NSL-KDD or CICIDS2017 network traffic dataset (features: duration, protocol_type, service, flag, src_bytes, dst_bytes, count, srv_count, etc., target: normal vs. attack categories like DoS, Probe, R2L, U2R).
4. **Train Ensemble ML & Anomaly Detection Models**:
   - Random Forest Regressor / Classifier.
   - Extra Trees or Gradient Boosting Classifier.
   - Isolation Forest for zero-day / anomaly detection.
   - Save serialized weights to `source_code/models/`.
5. **Backend & Database**:
   - FastAPI backend on port 5002 (or appropriate non-conflicting port).
   - SQLite database for traffic logging, alerts, and attack metrics.
6. **Frontend**:
   - Network Security Operations Center (SOC) dashboard:
     - Real-time packet analyzer & scoring.
     - Anomaly detection gauge.
     - Attack breakdown (DoS, Probe, etc.).
     - Incident logs & analytics.
7. **Automated Tests**:
   - Comprehensive pytest suite (unit, model, database, API, anomaly detection).
8. **Screen Recording**:
   - 2.5–3.5 minute MP4 recording (`walkthrough/walkthrough_video.mp4`).
9. **Presentations & Docs**:
   - High-res screenshots in `project_presentation.pptx` (15 slides).
   - Comprehensive `docs/technical_documentation.docx` and markdown documentation.
10. **Master Tracker Updates & Acceptance Sign-off**:
   - Update `AUDIT_MASTER/` inventory, CSV, Excel, and progress logs.
