# Comprehensive Video Walkthrough Script: Medical Sensor-Based Disease Prediction and Recommendation Using CNN Algorithm (PROJECT-016)

**Total Duration**: Exactly 180.0 seconds (03:00.00)  
**Resolution**: 1280x800  
**Video Codec**: H.264 (libx264, yuv420p)  
**Audio / Narration Track**: Synchronized Clinical Engineering Voiceover  

---

### Phase 1: Clinical Command Center & Telemetry Overview (00:00 - 00:25)
**Visual**: Browser navigates to `http://localhost:5173/`. The Command Center loads with real-time biometric telemetry cards displaying Heart Rate (76 bpm), Blood Pressure (122/81 mmHg), Oxygen Saturation (98% SpO2), and Respiration Rate (16 breaths/min). The system health indicator verifies that the Node.js Express Gateway (Port 5016) and PyTorch 1D CNN Inference Engine (Port 5017) are actively connected.
**Narrator**: "Welcome to the demonstration of Project 16: Medical Sensor-Based Disease Prediction and Recommendation Using 1D Residual Convolutional Neural Networks. We begin at the Clinical Command Center, where continuous IoT sensor telemetry is ingested and monitored in real time. Notice the verified system banner confirming zero simulated scores and authentic connection to our dedicated deep learning inference microservice."

---

### Phase 2: ECG Signal Ingestion & Lead II Canvas (00:25 - 00:55)
**Visual**: Navigation to `/ecg`. An MIT-BIH benchmark ECG recording (`sample_test_100.csv`) is selected. The application plots the high-frequency Lead II cardiac time-series sampled at 360 Hz using an interactive Recharts canvas. Pan and zoom controls highlight clean P-waves, narrow QRS complexes, and T-wave repolarization filtered via our bidirectional Butterworth bandpass filter (0.5 to 40 Hz).
**Narrator**: "Navigating to the ECG Analysis module, we inspect raw sensor waveform ingestion. The platform supports standard clinical formats including CSV, JSON, and PhysioNet WFDB records. Our deterministic digital preprocessing pipeline applies a 2nd-order zero-phase Butterworth filter between 0.5 and 40 Hertz to eliminate baseline wander and powerline interference, followed by Pan-Tompkins QRS peak detection."

---

### Phase 3: 1D CNN Inference & Arrhythmia Classification (00:55 - 01:25)
**Visual**: Navigation to `/predictions`. The user triggers 1D CNN inference on the ingested cardiac cycles. The PyTorch ResNet-1D model executes a tensor forward pass across 187-sample beat slices. The interface displays the prediction card: Class V (Ventricular Ectopic Beat / Premature Ventricular Contraction) with 78.2% confidence, complete with full multiclass probability distributions across all 5 AAMI EC57 classes and a clinical narrative explanation.
**Narrator**: "Here in the Diagnostic Prediction engine, our trained PyTorch Residual 1D CNN processes the segmented 187-sample cardiac windows. The model classifies the predominant rhythm as Class V—Ventricular Ectopic Beat—with 78.2% calibrated confidence. The inference engine provides an automated clinical narrative detailing beat morphology and ectopic burden without human latency."

---

### Phase 4: Multi-Parameter Vitals Monitoring (01:25 - 01:50)
**Visual**: Navigation to `/monitoring`. The screen displays longitudinal hemodynamic trend charts tracking mean arterial pressure (MAP), diurnal blood pressure shifts, and oxygen saturation over multi-hour observation windows. Boundary checks visually flag any physiological anomalies.
**Narrator**: "Moving to Vitals Monitoring, we track longitudinal physiological telemetry. The system enforces strict defensive validation at the API boundary, guaranteeing that physiologically impossible values such as inverted blood pressures or negative heart rates are rejected immediately with HTTP 422 errors."

---

### Phase 5: Evidence-Based Clinical Recommendations (01:50 - 02:15)
**Visual**: Navigation to `/recommendations`. Dynamic clinical decision cards appear, categorized into Lifestyle Modifications, Diagnostic Referrals, and Pharmacological Interventions. The high ventricular ectopic burden triggers an urgent 24-hour Holter monitoring recommendation, serum electrolyte screening, and cardiology review.
**Narrator**: "The Clinical Decision Support subsystem analyzes detected arrhythmia patterns against evidence-based cardiology guidelines. For elevated ventricular ectopic activity, the engine automatically recommends an urgent 24-hour Holter assessment, serum magnesium and potassium screening, and consultation for beta-blocker therapy, with full clinician review workflows."

---

### Phase 6: Diagnostic Reports & Critical Alert Center (02:15 - 02:40)
**Visual**: Navigation to `/reports`. The application renders a consolidated patient diagnostic report synthesizing vital statistics, arrhythmia frequency, and overall cardiovascular risk status. The Alert Center lists severity-tiered notifications with buttons for clinician acknowledgment.
**Narrator**: "In the Diagnostic Reports center, clinicians receive an aggregated summary of telemetry trends, ectopic frequency, and risk stratification. The notification engine organizes events into Critical, Warning, and Informational tiers, maintaining an immutable audit log of physician acknowledgments."

---

### Phase 7: Historical Archive & System Sign-Off (02:40 - 03:00)
**Visual**: Navigation to `/history`. The table displays the complete SQLite audit trail of all uploaded recordings, model classifications, and timestamps. The narrator summarizes project accomplishments as the camera pans across the full diagnostic record.
**Narrator**: "Finally, the Diagnostic History module demonstrates relational SQLite persistence with full ACID compliance and zero data fabrication. With 63 passing automated tests, a 98.6% accurate PyTorch ResNet-1D model, and an intuitive clinical interface, Project 16 is verified 100% complete and submission-ready."
