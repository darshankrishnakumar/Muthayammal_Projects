# Walkthrough Timestamps: AI DRIVER DROWSINESS & FATIGUE VIGILANCE DETECTION (PROJECT-035)

Exact Duration: **180.000s (03:00)** | Format: H.264 MP4 1280x800 @ 24fps | Dedicated Port: **5035**

| Timestamp | Phase | Topic / Demonstration Point | Key Visual Indicators |
|---|---|---|---|
| **00:00 - 00:30** | Phase 1 | DMS Cockpit Fleet Overview & System Health | Top-level dashboard, Port 5035 active status, Vigilance index (94.5%), fleet driver selector |
| **00:30 - 01:00** | Phase 2 | 68-Point Facial Landmark HUD & NIR Calibration | Optical NIR canvas, facial landmark overlay, eye & lip contour tracking, driver DRV-804 selection |
| **01:00 - 01:30** | Phase 3 | Attentive Driving State & Multi-Modal Telemetry | EAR (0.360), MAR (0.160), PERCLOS (3.5%), Head Pitch (+1.2°), PyTorch Classifier 'Alert' prediction |
| **01:30 - 02:00** | Phase 4 | Stage-1 Drowsiness Advisory & Warning Chimes | Subtle eyelid droop (EAR 0.22), yawn expansion (MAR 0.42), amber banner, 880Hz acoustic chime |
| **02:00 - 02:30** | Phase 5 | Critical Microsleep Emergency Intervention | Acute microsleep (EAR 0.14, PERCLOS 58%, Pitch -22°), red strobe alarm banner, auditory siren, haptic pulse |
| **02:30 - 03:00** | Phase 6 | Fleet Trip Telematics & Cryptographic Audit Ledger | Commercial fleet trip sessions table, safety grades (A+ to B), SHA-256 audit hash chain, SQLite WAL ledger |

*Verification*: Video duration strictly verified at **180.000000 seconds** via `ffprobe` prior to master audit commit.
