# Child Gait Prediction and Biomechanical Assessment System

**Project Code**: PROJECT-006  
**Subject Domain**: Pediatric Biomechanics / Biomedical Informatics / Machine Learning  
**Core Technologies**: Python 3.12, FastAPI, Scikit-Learn 1.7+, SQLite3, Tailwind CSS, Chart.js  
**Operational Port**: `http://127.0.0.1:5006`  

---

## 1. Overview
The Child Gait Prediction System is a clinical-grade diagnostic decision-support platform designed to analyze pediatric gait kinematics and kinetic ground reaction forces. By evaluating parameters such as heel and toe pressure, foot tilt angle, cadence, stride length, and walking velocity, the system identifies locomotion pathologies including:
- **Normal Gait**: Symmetrical locomotion within normative reference thresholds.
- **Spastic Diplegia**: Bilateral crouch gait characterized by excessive knee/hip flexion and equinus.
- **Hemiplegia**: Asymmetrical gait with unilateral bias, circumduction, or drop-foot.

---

## 2. Key Highlights
- **Real C3D Clinical Dataset**: Trained on authentic 3D optical motion capture gait trials from the SimTK Pediatric Gait Repository.
- **Strict Zero-Leakage Split**: Partitioned strictly by participant ID to ensure the model generalizes to completely unseen pediatric patients.
- **Tuned Random Forest Ensemble**: Optimized hyperparameters (50 trees, max depth 3) achieving 1.000 Macro One-vs-Rest ROC-AUC.
- **Full-Stack Architecture**: Single unified FastAPI microservice on Port 5006 serving interactive UI, REST APIs, and SQLite database.
- **Longitudinal Tracking**: Chart.js progression graphs tracking walking velocity and stride improvements across clinical visits.
- **Automated Physical Therapy Advisories**: Instant evidence-based clinical guidance and Ankle-Foot Orthosis (AFO) recommendations.
- **23/23 Passing Automated Tests**: Rigorous pytest suite verifying ML inference, database CRUD, and REST APIs.

---

## 3. Documentation Suite
- [Architecture & Data Flow](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/architecture.md)
- [Dataset and Machine Learning Details](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/dataset_and_model_details.md)
- [REST API Documentation](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/api_documentation.md)
- [Setup and Execution Guide](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/setup_and_execution.md)
- [Comprehensive Testing Report](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/testing_report.md)
- [Limitations and Future Work](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/limitations_and_future_work.md)
- [Third-Party Notices](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/third_party_notices.md)
- [Final Project Acceptance Report](file:///Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/acceptance_report.md)
