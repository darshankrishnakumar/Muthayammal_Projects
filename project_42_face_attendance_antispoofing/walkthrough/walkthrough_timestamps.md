# Walkthrough Timestamps: AI-Driven Face Recognition Attendance & Anti-Spoofing (PROJECT-042)

**Total Duration**: Exactly 180.000000 Seconds (03:00.00)  
**Standard**: 720 Frames @ 4.0000 FPS = Exact 180.000000s Duration (H.264 MP4, YUV420p, 1280x800)  
**Microservice Endpoint**: `http://127.0.0.1:5042/`

---

| Timestamp Window | Phase Index | Demonstration Focus & Narrative Points | Visual Elements Captured |
|:---:|:---:|---|---|
| **00:00 - 00:30** | Phase 1 | **System Architecture & Port 5042 Gateway Launch**: Initializing FastAPI microservice on Port 5042 with SQLite Write-Ahead Logging (WAL) and dual PyTorch accelerators. | Top navigation bar with Port 5042 badge, WAL Active indicator, and 4 high-level KPI metric cards. |
| **00:30 - 01:00** | Phase 2 | **Deep Metric Learning & Regressor Architecture**: Overview of DeepAntiSpoofFaceNet (512-D ArcFace spherical hypersphere) and BiometricLivenessQualityRegressorNet. | Architecture diagrams, model parameter metadata, and 6,000-record physical telemetry dataset. |
| **01:00 - 01:30** | Phase 3 | **Real-Time Biometric HUD & 60 FPS Mesh Canvas**: Demonstrating the live HTML5 Canvas HUD with face wireframe, eye reticles, laser depth scanning, and optical flow vectors. | Interactive canvas with real-time laser scanning reticle, eye tracking points, and live frame counter. |
| **01:30 - 02:00** | Phase 4 | **Genuine Student Verification & Telemetry Flow**: Authenticating Alex Chen (STU-101), showing 96.5% ArcFace match, 2.53% spoof risk, micro-tremor streaming, and ACCESS GRANTED. | Turnstile unlocked status, green liveness badge, real-time Chart.js micro-tremor waveform update. |
| **02:00 - 02:30** | Phase 5 | **Presentation Attack Defense (Print & Replay)**: Simulating 2D photographic printout and 4K screen replay attacks; immediate drop in micro-tremor triggers SPOOF REJECTED. | Gate lock alarm, high spoof risk alert (>94.5%), depleted FFT high-frequency energy detection. |
| **02:30 - 03:00** | Phase 6 | **Cryptographic SHA-256 Audit Ledger & Verification**: Inspecting Genesis Block #0, unbroken hash chaining, single-bit tamper detection, and final verification summary. | Ledger explorer table displaying block indices, action types, truncated SHA-256 hashes, and 33/33 test summary. |

---

*Video File Location: `project_42_face_attendance_antispoofing/walkthrough/walkthrough_video.mp4`*  
*Verified Duration: `180.000000` seconds via `ffprobe`.*
