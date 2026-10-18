# PROJECT 55 — RISK REGISTER AND OPERATIONAL LIMITATIONS
## Enterprise Governance, Safety Boundaries, and Failure Mode Analysis

---

### 1. Risk Register

| Risk ID | Risk Description | Severity | Probability | Inherent Impact | Mitigation Strategy | Operational Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Camera Occlusion / Physical Lens Obstruction** (mud, heavy insect debris, snow accumulation) | High | Medium | Video degradation leading to missed incidents or uncalibrated blur rejection | `VideoQualityChecker` detects variance collapse ($\text{Var} < 25.0$) and automatically trips `DEGRADED_FEED` alarm to TMC operators to schedule physical maintenance. | **Mitigated** |
| **RSK-02** | **Extreme Adverse Lighting** (direct low-angle solar glare, complete loss of street lighting at night) | High | Medium | Frame saturation or underexposure distorting spatial contours | Dual illumination bounds check ($15 \le \mu \le 245$) combined with multi-cue kinematic radar (which tracks relative trajectory and speed changes regardless of illumination). | **Mitigated** |
| **RSK-03** | **Network Disconnection / Stream Drop** (RTSP timeout, bandwidth throttle) | High | Low | Disruption of live stream ingestion | Automatic backoff reconnection in `video_service` and WebSocket keep-alive heartbeat with graceful failover to cached stream buffers. | **Mitigated** |
| **RSK-04** | **Dense Stop-and-Go Congestion False Triggers** | Medium | High | Frequent sudden braking in bumper-to-bumper rush hour | Multi-cue cross-attention requires trajectory divergence, orientation abnormality, or collision proximity shock to confirm accident; pure deceleration alone is rejected. | **Mitigated** |
| **RSK-05** | **Emergency Dispatch Flapping / Duplicate Calling** | Medium | Medium | Automated CAD receiving dozens of alerts for the same single crash | Incident state machine deduplication: once an incident is recorded on a camera feed, subsequent frames append to the same `incident_uuid` during a cooldown window (90s). | **Mitigated** |
| **RSK-06** | **Operator Alert Fatigue** | High | Medium | Too many ambiguous low-confidence warnings distracting dispatchers | Strict triage thresholding: confidence $\ge 0.65$ triggers CAD dispatch, $0.40 \le c < 0.65$ triggers passive Advisory review, and $< 0.40$ is filtered out silently. | **Mitigated** |

---

### 2. Operational Limitations & Edge Cases

1. **Sub-Minimal Vehicle Resolution**:
   - Vehicles occupying fewer than $20 \times 20$ pixels in extreme background distances cannot yield reliable orientation or structural deformation cues. 
   - *Operational Boundary*: Valid detection range is calibrated for the primary $150\text{ meters}$ roadway corridor from the camera mount.
2. **Dense Smoke / Chemical Hazmat Invisibility**:
   - Complete visual obscuration by dense smoke grenades, wildfire haze, or toxic chemical releases prevents optical flow calculation. In such scenarios, multimodal acoustic or radar sensor fusion is recommended as a secondary redundancy.
3. **Camera Vibration During High Winds**:
   - Roadway pole swaying in gale winds ($> 80\text{ km/h}$) introduces global optical flow background jitter.
   - *Mitigation*: The feature extractor uses percentile-based spatial filtering and vehicle-centric bounding box tracking to isolate vehicular motion from global camera sway.
4. **Pedestrian / Micromobility Collisions**:
   - The current baseline and Phase 2 focus are optimized for motor vehicles (cars, trucks, motorcycles, buses). Bicycles and pedestrian interactions have lower mass and different kinematic signatures, which are planned for Phase 3 expansion.

---

### 3. Ethical, Privacy, and Regulatory Considerations
- **Facial Anonymization & License Plate Shielding**: Visual evidence snapshots can be configured with automated Gaussian blur over detected facial regions and license plates to comply with GDPR, CCPA, and CJIS (Criminal Justice Information Services) standards.
- **Human-in-the-Loop Safeguard**: Automated CAD dispatches are transmitted with immediate priority ratings, but human TMC commanders retain the authority to acknowledge, upgrade, downgrade, or mark incidents as false alarms with full audit trail logging.
