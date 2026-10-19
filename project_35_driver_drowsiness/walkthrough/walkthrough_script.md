# Video Walkthrough Script: AI Driver Drowsiness & Fatigue Vigilance Detection System

**Project**: PROJECT-035  
**Target Duration**: 180.000s (03:00)  
**Resolution**: 1280x800 Widescreen  
**Endpoint**: `http://127.0.0.1:5035/`

---

### [00:00 - 00:30] Phase 1: DMS Cockpit Fleet Overview & System Health
- **Visual**: The video opens on the VIGILANCE-AI cockpit dashboard running on assigned Port 5035. The status pill displays `Active (:5035)` with a pulsating emerald indicator. The header and driver selector bar showcase commercial fleet operations across Class 8 Freightliners, Hazardous Tankers, Transit Buses, and Delivery Couriers.
- **Narrator**: "Welcome to the technical demonstration of PROJECT-035: AI Driver Drowsiness and Cognitive Fatigue Vigilance Detection System. Designed for high-risk commercial logistics and passenger transit corridors, this system delivers real-time in-cabin driver monitoring using Near-Infrared optical tracking and PyTorch deep neural networks on dedicated Port 5035."

---

### [00:30 - 01:00] Phase 2: 68-Point Facial Landmark HUD & NIR Calibration
- **Visual**: The viewport focuses smoothly on the in-cabin optical sensor feed. The simulated infrared camera canvas renders the driver's head orientation and a 68-point facial mesh. The operator selects `DRV-804: Kavita Rao (Peterbilt 579 Cryogenic Tanker)`, dynamically loading personalized baseline biometrics (Baseline EAR: 0.36, Baseline MAR: 0.15).
- **Narrator**: "In Phase 2, we inspect the optical Near-Infrared sensor HUD. Operating at 30 FPS, the system tracks 68 facial landmark coordinates, isolating eyelid and lip contours regardless of ambient illumination or night conditions. Selecting commercial driver DRV-804 instantly calibrates the detection engine to personalized biometric baselines stored in our SQLite database."

---

### [01:00 - 01:30] Phase 3: Attentive Driving State & Multi-Modal Telemetry
- **Visual**: Programmatic trigger `runAnalysis('alert')` streams nominal telemetry: Eye Aspect Ratio at 0.360, Mouth Aspect Ratio at 0.160, PERCLOS at 3.5%, and Head Pitch at +1.2°. The status banner displays `Alert & Attentive`, with Driver Vigilance Index at 94.5% and Microsleep Risk at an optimal 0.02.
- **Narrator**: "Phase 3 demonstrates nominal, attentive driving. With wide eyelid openings and steady forward gaze, the Eye Aspect Ratio reads 0.360 while PERCLOS remains at an optimal 3.5%. The PyTorch DriverFatigueClassifierNet assigns the state to 'Alert' with 97.25% model certainty, and the regressor records a healthy 94.5% vigilance score."

---

### [01:30 - 02:00] Phase 4: Stage-1 Drowsiness Advisory & Warning Chimes
- **Visual**: The operator triggers `runAnalysis('drowsy')`. EAR drops to 0.220 as eyelids droop; MAR expands to 0.420 indicating frequent yawning; head pitch tilts forward to -8.5°. The status banner transitions to amber `Moderate Fatigue Advisory`, vigilance score drops to 62.0%, and an 880Hz acoustic warning chime plays.
- **Narrator**: "In Phase 4, we observe the onset of driver fatigue during late-night transit. Notice the eyelid drooping as EAR declines to 0.220 and yawning expands mouth aspect ratio to 0.420. The system activates Stage-1 Advisory: displaying an amber notification and firing progressive warning chimes to prompt an early rest break before hazardous sleep occurs."

---

### [02:00 - 02:30] Phase 5: Critical Microsleep Emergency Intervention
- **Visual**: Programmatic trigger `simulateFatigueSpike()` executes an acute micro-sleep event: EAR plummets to 0.140, blink duration exceeds 800ms, PERCLOS reaches 58.0%, and head nods down to -22.0°. A high-priority red strobe alert banner flashes across the screen (`⚠️ CRITICAL FATIGUE WARNING`), accompanied by continuous emergency alarms and simulated haptic seat pulses. The operator clicks `Acknowledge`.
- **Narrator**: "Phase 5 demonstrates an acute micro-sleep emergency. Eye closure exceeds 800 milliseconds and PERCLOS surges to 58%, accompanied by severe forward head nodding. The system immediately fires Stage-3 Emergency Intervention: high-contrast strobe visual alarms, emergency acoustic sirens, and simulated seat vibrations, mandating an immediate safe corridor exit."

---

### [02:30 - 03:00] Phase 6: Fleet Trip Telematics & Cryptographic Audit Ledger
- **Visual**: The view scrolls smoothly to the fleet trip sessions and safety alerts ledger tables. Trip IDs, assigned drivers, elapsed durations, distances, vigilance averages, and safety grades (A+ to B) are rendered from SQLite in WAL mode. The recent alerts ledger displays acknowledged interventions with SHA-256 cryptographic verification hashes.
- **Narrator**: "Finally, in Phase 6, we review the enterprise fleet telematics and compliance ledger. All trip metrics, active interventions, and operator acknowledgments are committed with ACID guarantees to an SQLite database in Write-Ahead Logging mode. Every safety intervention is sealed with a SHA-256 cryptographic hash, ensuring tamper-proof auditability under FMCSA and DOT regulations."
