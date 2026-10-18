# Resume Instructions for Next Step / Session

## Current Status
- **PROJECT-001**: **100% VERIFIED COMPLETE**. (BiLSTM .pth, 18/18 tests, 02:37 video, 15-slide PPTX, DOCX, port 5001).
- **PROJECT-002**: **100% VERIFIED COMPLETE**. (Random Forest + Extra Trees + Isolation Forest, NSL-KDD 22,544 rows, 19/19 tests, 03:00 video, 15-slide PPTX, DOCX, port 5002).
- **Next Project to Execute**: **`PROJECT-003: Plant Disease Detection (Apple Disease Detection Using Deep Learning / CNN)`**

---

## Action Plan for PROJECT-003
1. **Directory**: `project_03_apple_disease_detection`
2. **Inspect Existing State**:
   - Check existing code, datasets, models, database, tests, docs, PPTX.
3. **Acquire Real Dataset**:
   - PlantVillage Apple dataset (Apple Scab, Black Rot, Cedar Apple Rust, Healthy).
4. **Train Computer Vision / Deep Learning Model**:
   - PyTorch CNN / MobileNetV2 / ResNet transfer learning on apple leaf disease images.
   - Save serialized weights `.pth` in `source_code/models/`.
5. **Backend & Database**:
   - FastAPI backend on port 5003.
   - SQLite database for diagnostic scans, treatments, and leaf metrics.
6. **Frontend**:
   - Diagnostic leaf image uploader, disease confidence gauge, symptoms breakdown, chemical/organic treatment recommendations.
7. **Automated Tests**:
   - pytest suite for image tensor loading, model inference, database, and API endpoints.
8. **Screen Recording**:
   - 2.5–3.5 minute MP4 recording (`walkthrough/walkthrough_video.mp4`).
9. **Presentations & Docs**:
   - High-res screenshots in `project_presentation.pptx` (15 slides).
   - Comprehensive `docs/technical_documentation.docx` and markdown documentation.
10. **Master Tracker Updates & Acceptance Sign-off**:
   - Update `AUDIT_MASTER/` inventory, CSV, Excel, and progress logs.
