# Walkthrough Timestamps: Medical Sensor-Based Disease Prediction and Recommendation Using CNN Algorithm (PROJECT-016)

| Timestamp | Duration | Phase | Demonstration Point / System Action |
|---|---|---|---|
| **00:00 - 00:25** | 25s | Clinical Command Center | Navigation to `http://localhost:5173/`. Real-time sensor vitals telemetry (Heart Rate, Blood Pressure, SpO2), genuine 1D CNN status banner, recent clinical activity log. |
| **00:25 - 00:55** | 30s | ECG Signal Ingestion & Lead II Canvas | Navigation to `/ecg`. Multi-format upload, interactive Recharts time-series canvas rendering MIT-BIH Lead II waveform at 360 Hz with Pan-Tompkins peak visualization. |
| **00:55 - 01:25** | 30s | 1D CNN Inference & Arrhythmia Classification | Navigation to `/predictions`. Triggering PyTorch Residual 1D CNN inference, AAMI 5-class classification, Ventricular Ectopic Beat (PVC) detection (78.2% confidence), clinical explanation. |
| **01:25 - 01:50** | 25s | Multi-Parameter Vitals Monitoring | Navigation to `/monitoring`. Hemodynamic telemetry tracking, blood pressure ranges (systolic/diastolic), mean arterial pressure, and physiological range validation. |
| **01:50 - 02:15** | 25s | Evidence-Based Clinical Recommendations | Navigation to `/recommendations`. AI-driven clinical decision support categorizing interventions into Lifestyle, Diagnostic, and Medication tiers based on arrhythmia burden. |
| **02:15 - 02:40** | 25s | Diagnostic Reports & Critical Alert Center | Navigation to `/reports`. Consolidated 24-hour diagnostic summary, severity-tiered alert notifications (Critical, Warning, Informational), and clinician acknowledgment audit trail. |
| **02:40 - 03:00** | 20s | Historical Archive & System Sign-Off | Navigation to `/history`. Comprehensive SQLite persistence review, immutable diagnostic records, model forensics, and capstone engineering sign-off. |

*Total Duration: Exactly 180.0 seconds (03:00.00). Resolution: 1280x800, Video Codec: H.264 (libx264, yuv420p).*
