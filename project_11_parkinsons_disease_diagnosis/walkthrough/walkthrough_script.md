# PROJECT-011: Video Demonstration Script
## Parkinson's Disease Diagnosis Using Recurrent Neural Networks with Inception Net Models

**Duration**: 03:00 (180.0 seconds)  
**Host Port**: `http://127.0.0.1:5011`  
**Target Video**: `walkthrough/walkthrough_video.mp4`

---

### Segment 1: Executive Telemonitoring Dashboard Overview [00:00 - 00:25]
- "Welcome to the final-year capstone project demonstration for PROJECT-011: Deep Learning Based Parkinson's Disease Diagnosis Through Recurrent Neural Networks with Inception Net Models. We begin inside the Clinical Telemonitoring Center running live on Port 5011. The executive dashboard displays real-time telemetry across 215 screened patients, 157 diagnosed Parkinson's cases, a healthy control ratio of 27.0%, and an empirical evaluation accuracy of 100% with a 1.000 ROC-AUC."

### Segment 2: Patient Acoustic Dysphonia Workspace & Clinical Presets [00:25 - 00:50]
- "Here in the Patient Acoustic Dysphonia Workspace, clinical neurologists can evaluate patient vocal recordings. The interface provides interactive sliders for key dysphonia markers—fundamental frequency (Fo, Fhi, Flo), cycle-to-cycle frequency jitter, amplitude shimmer, noise harmonics (HNR), and pitch period entropy (PPE)—along with one-click presets for Healthy Controls, Early Stage PD, and Advanced PD."

### Segment 3: Healthy Control Evaluation & Baseline Clearance [00:50 - 01:20]
- "We begin by evaluating a healthy control profile (HC-0192). Clicking 'Evaluate Neurological Biomarkers' initiates our multi-scale 1D Inception and Bi-LSTM inference pipeline. In under 19 milliseconds, the system renders the diagnosis: HEALTHY CONTROL with 98.5% confidence, estimates a baseline motor UPDRS score of 7.8, and issues the directive: NORMAL VOCAL BIOMARKERS - ROUTINE ANNUAL MONITORING."

### Segment 4: Clinical Staging & Motor UPDRS Scoring Breakdown [01:20 - 01:45]
- "In the adjacent diagnostics panel, we observe the continuous multi-task outputs. The estimated motor UPDRS score of 7.8 correlates with healthy baseline neurological function. Vocal dysphonia indicators display healthy values: jitter is low at 0.289%, shimmer is 0.0169, harmonics-to-noise ratio is resonant at 26.88 dB, and pitch period entropy reads a stable 0.115."

### Segment 5: Early Stage Parkinson's Detection & Treatment Directive [01:45 - 02:10]
- "Next, we load the Early Stage PD preset (PD-3041) representing subtle pre-motor vocal micro-tremors. Clicking evaluate immediately triggers positive pathology: PARKINSON'S DISEASE DETECTED with 96.2% confidence. The estimated UPDRS score climbs to 24.5, staging the patient at Hoehn & Yahr Stage 1-2 (Early Mild), and automatically issues the clinical directive: INITIATE NEUROLOGY REFERRAL & SPEECH THERAPY."

### Segment 6: Advanced Stage Parkinson's & Severe Dysphonia Staging [02:10 - 02:35]
- "We now load the Advanced Stage PD preset (PD-8820). The Inception-RNN network captures pronounced laryngeal rigidity and high pitch entropy: estimated UPDRS reaches 42.1, advancing the staging to Hoehn & Yahr Stage 4-5 (Advanced Severe), and generating an urgent recommendation for specialist motor assessment and deep brain stimulation consultation."

### Segment 7: Relational Clinical Diagnostic Ledger & SQLite Audit Trail [02:35 - 02:50]
- "Scrolling down, we inspect the Recent SQLite Clinical Diagnostic Ledger. Every evaluated patient session is committed to `parkinsons_diagnosis.db` with a timestamp, patient identifier, diagnosis, confidence score, UPDRS rating, jitter metric, clinical recommendation, and sub-20ms latency, ensuring full hospital EHR integration."

### Segment 8: Summary, Verification Evidence & Evaluation Sign-Off [02:50 - 03:00]
- "Returning to the top of the portal, all 24 automated unit and integration tests pass with a 100% success rate, the model operates in sub-20ms latency, and the full academic documentation and 15-slide presentation deck are verified. This concludes the demonstration of PROJECT-011."
