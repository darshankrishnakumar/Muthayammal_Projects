# Walkthrough Script: INDUSTRIAL FIRE & SMOKE DETECTION USING REAL-TIME VIDEO SURVEILLANCE (PROJECT-040)

**Project Title**: Industrial Fire & Smoke Detection with Dual-Stream Spatio-Temporal Deep Learning  
**Target Duration**: Exactly 180.000 seconds (03:00) | 720 frames @ 4 fps input / 24 fps output  
**Assigned Port**: 5040 | Database: SQLite 3 in WAL Mode | Models: DualStreamFireSmokeNet & FirePropagationThermalRiskRegressorNet

---

## Phase 1: [00:00 - 00:30] Central Surveillance Command Dashboard & Port 5040 Status
- **Spoken Narration / Visual Focus**: Welcome to Project 40 of the 55 Engineering Capstone series: Industrial Fire and Smoke Detection with Dual-Stream Spatio-Temporal Deep Learning. The platform is running as an asynchronous microservice on dedicated Port 5040. The top telemetry bar displays over 6,000 scanned records, active facility hazard zones, and healthy operational statuses for both PyTorch models—DualStreamFireSmokeNet and the FirePropagationThermalRiskRegressor.

## Phase 2: [00:30 - 01:00] 1080p CCTV Simulation & 5-20 Hz FFT Spectrum Analyzer
- **Spoken Narration / Visual Focus**: We observe the real-time CCTV surveillance simulation engine rendering physics-based buoyant flame turbulence and expanding smoke plume dispersion at 60 FPS. Simultaneously, the temporal signal processing subsystem evaluates the 5-20 Hz Fast Fourier Transform (FFT) power spectrum, isolating the 15.8 Hz turbulent vortex shedding peak characteristic of buoyant hydrocarbon combustion.

## Phase 3: [01:00 - 01:30] Boiler Room Optical Flame Detection & Temperature Rise
- **Spoken Narration / Visual Focus**: We transition to the Industrial Plant Boiler Room monitored via CCTV-BOI-01. Upon detecting active combustion, the dual-stream network achieves 98.5% confidence in classifying FLAME_DETECTED. The neural regressor predicts a core flame temperature of 485.0 C with an evacuation urgency score of 78.5, automatically arming the High-Pressure Water Mist and CO2 deluge suppression interlocks.

## Phase 4: [01:30 - 02:00] Hazmat Chemical Storage Dual-Hazard Emergency & Deluge
- **Spoken Narration / Visual Focus**: Next, we evaluate a catastrophic escalation in Warehouse Sector B Chemical Storage. The system instantaneously triggers a TIER_3_CRITICAL alarm for DUAL_FIRE_SMOKE_HAZARD with 99.4% confidence. The regressor estimates flame temperatures exceeding 745.0 C, a toxic CO concentration of 580 ppm, and an evacuation urgency of 96.0/100, executing an emergency deluge dispatch directive.

## Phase 5: [02:00 - 02:30] Data Center Server Hall Early Smoke & Clean Agent Interlock
- **Spoken Narration / Visual Focus**: In Data Center Server Hall 3, early smoldering cable insulation is detected via expanding plume diffusion at 2.4 m/s without open flame. The system classifies SMOKE_DETECTED (Tier 1 Early) and arms the water-free Inergen IG-541 clean agent suppression system, simultaneously commanding HVAC dampers to seal the server hall and protect critical IT hardware.

## Phase 6: [02:30 - 03:00] Cryptographic Audit Ledger & Incident Telemetry Register
- **Spoken Narration / Visual Focus**: Finally, we inspect the persistent relational incident register and cryptographic audit ledger. Every alarm dispatch and suppression release is cryptographically sealed with SHA-256 block hash chaining beginning from the Genesis block. Backed by SQLite Write-Ahead Logging and a 100% verified 33-test automated QA suite, Project 40 delivers production-grade industrial life safety.
