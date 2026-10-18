# PROJECT 55 — PHASE 1 SPECIFICATION
## Problem Definition, Scope, and Data Pipeline Specification

### 1. Project Title & System Identity
- **Project Title**: AI-Based Accident Detection and Emergency Alert System Using Computer Vision
- **Project Identifier**: Project 55 (55 of 55)
- **Deployment Tier**: Enterprise Operational Traffic Management & Emergency Services Integration

---

### 2. Operational Scenario & System Boundaries
1. **Target Users**:
   - **Emergency Medical & Dispatch Teams (911 / 112 / CAD Operators)**: Require instant prioritized incident alerts with location, severity level, and visual evidence snapshot.
   - **Traffic Management Center (TMC) Operators**: Monitor highway/arterial CCTV networks, verify alerts, and manage lane closures or rescue dispatch.
   - **Autonomous Fleet / Connected Vehicle Centers**: Ingest dashcam feeds from fleet trucks/vehicles for rapid on-scene distress reporting.
2. **System Boundaries**:
   - **Inputs**: Real-time or recorded digital video feeds (RTSP streams, MP4/AVI files, simulated roadside/dashcam feeds) with frame rates from 15 to 30 FPS at 720p/1080p resolution.
   - **Outputs**: Accident detection confidence score ($0.0 \le c \le 1.0$), multi-cue attribution breakdown, visual annotated bounding boxes and trajectory trails, estimated severity (Minor, Moderate, Severe, Critical), precise GPS/camera location, and CAD-compliant JSON dispatch payloads.
   - **Out of Scope (Explicit Boundaries)**: Direct robotic dispatch actuation (requires human operator verification or automated API trigger confirmation), physical onboard airbag sensor hardware replacement (this is purely visual/video-based sensing).

---

### 3. Core Functional & Non-Functional Requirements
#### Functional Requirements (FR)
- **FR-1 Multi-Cue Anomaly Analysis**: The system MUST detect accidents using 5 combined physical cues:
  1. *Trajectory Deviation*: Sudden departure from lane or normal heading vector.
  2. *Sudden Deceleration*: Rate of speed drop exceeding $-5.0\text{ m/s}^2$ ($g$-force anomaly).
  3. *Abnormal Orientation*: Vehicle angle shift exceeding $45^\circ$, rollover, or perpendicular roadway blocking.
  4. *Collision Motion Patterns*: Converging optical flow vectors and centroid distance collapse below collision threshold.
  5. *Post-Collision Immobility*: Vehicle remaining stationary for $\ge 3$ seconds immediately following an anomaly spike.
- **FR-2 Temporal Deep Learning Classification**: Consecutive frames within a temporal window (e.g., 16 frames) must be analyzed sequentially to capture event dynamics rather than single-frame artifacts.
- **FR-3 Severity & Location Estimation**: Automatically calculate severity index based on deceleration magnitude, rollover status, vehicle count, and post-collision immobility. Associate event with camera GPS and roadway zone.
- **FR-4 Automated Emergency Notification**: Produce an automated dispatch package containing event ID, timestamp, GPS, severity rating, confidence score, and annotated snapshot.
- **FR-5 Operator Dashboard**: Provide an interactive web dashboard with live video stream playback, real-time alert feed, multi-cue telemetry HUD, triage controls (Acknowledge, Dispatch, Mark False Alarm), and performance analytics.

#### Non-Functional Requirements (NFR)
- **NFR-1 Latency**: End-to-end inference and alert generation latency MUST be under $1,500\text{ ms}$ on target hardware.
- **NFR-2 False Alarm Rate (FAR)**: Multi-cue filtering must suppress false alarms from ordinary hard braking or traffic jams to $< 4.0\%$.
- **NFR-3 High Availability**: Stateless API design with SQLite/PostgreSQL persistence capable of continuous 24/7 background stream processing.
- **NFR-4 Extensibility**: Modular separation of computer vision pipeline, temporal deep learning model, business logic, and web interface.

---

### 4. Input/Output Data Dictionary

| Field | Type | Description | Range / Format |
| :--- | :--- | :--- | :--- |
| `frame_id` | Integer | Monotonic video frame index | $0, 1, 2, \dots$ |
| `timestamp` | ISO 8601 String | UTC timestamp of frame capture | `YYYY-MM-DDTHH:MM:SS.sssZ` |
| `camera_id` | String | Unique identifier for camera or dashcam | e.g. `CAM-HWY-101-N` |
| `location_gps` | GeoJSON Object | Latitude, Longitude, and Roadway metadata | `{"lat": 37.7749, "lon": -122.4194, "zone": "Lane 2"}` |
| `boxes` | List of Float Arrays | Detected vehicle bounding boxes $[x_1, y_1, x_2, y_2]$ | Normalized $[0.0, 1.0]$ |
| `velocities` | List of Float | Estimated vehicle speeds in px/s or km/h | $\ge 0.0$ |
| `decelerations` | List of Float | Rate of velocity decrease ($\Delta v / \Delta t$) | Negative or zero |
| `orientations` | List of Float | Vehicle heading angles in degrees | $[-180.0, 180.0]^\circ$ |
| `collision_pattern_score` | Float | Convergence and optical flow collision index | $[0.0, 1.0]$ |
| `immobility_duration_sec` | Float | Elapsed seconds vehicle remained immobile | $\ge 0.0\text{ s}$ |
| `accident_confidence` | Float | Temporal model predicted probability | $[0.0, 1.0]$ |
| `severity` | Enum | Assessed emergency impact level | `Minor`, `Moderate`, `Severe`, `Critical` |
| `dispatch_status` | Enum | Incident state in command center | `New`, `Acknowledged`, `Dispatched`, `False Alarm`, `Resolved` |

---

### 5. Data Preparation & Preprocessing Pipeline
1. **Resolution & Normalization**:
   - Resized to standard model input dimensions ($224 \times 224$ for temporal CNN-RNN feature backbone, $640 \times 640$ for vehicle tracking).
   - Pixel intensities normalized to zero mean and unit variance ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$).
2. **Temporal Windowing**:
   - Sliding window of $T=16$ consecutive frames with stride $s=4$ frames.
3. **Data Augmentations for Real-World Robustness**:
   - Random brightness/contrast adjustments ($\pm 25\%$) simulating day, dusk, and night conditions.
   - Gaussian blur and simulated rain/fog artifacts.
   - Camera jitter and perspective shift perturbations.
4. **Leakage-Free Splitting**:
   - Split dataset by unique video sequence ID (70% Train, 15% Validation, 15% Test) ensuring no overlapping video clips between splits.
