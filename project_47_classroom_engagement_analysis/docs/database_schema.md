# Database Schema Specification: classroom.db (PROJECT-047)

## Overview
SQLite relational database operating with Write-Ahead Logging (`PRAGMA journal_mode=WAL`) on Port 5047.

### 1. `classroom_sessions` Table
Stores monitored academic courses, instructors, and lecture halls.
- `id` (INTEGER, PK): Primary key index.
- `session_id` (VARCHAR(50), UNIQUE, INDEX): E.g., `SESS-CS301`.
- `course_code` (VARCHAR(50)): E.g., `CS-301`, `MATH-210`, `AI-405`, `BIO-108`.
- `course_name` (VARCHAR(100)): Full academic title.
- `instructor_name` (VARCHAR(100)): Lead professor / lecturer.
- `classroom_id` (VARCHAR(50)): Lecture hall venue.
- `is_active` (BOOLEAN): Active operational status.

### 2. `engagement_snapshots` Table
Stores comprehensive timestamped multimodal telemetry and neural forecasts.
- `id` (INTEGER, PK): Primary key index.
- `snapshot_id` (VARCHAR(50), UNIQUE, INDEX): E.g., `ENG-2026-00101`.
- `session_id` (VARCHAR(50)): Foreign key linkage to `classroom_sessions`.
- `lecture_title` (VARCHAR(100)): Lecture topic narrative.
- `student_count` (INTEGER): Enrolled student attendance.
- `mean_engagement_score` (FLOAT): Continuous score [0.0, 100.0]%.
- `attentive_pct` (FLOAT): Attentive student percentage.
- `bored_pct` (FLOAT): Bored student percentage.
- `distracted_pct` (FLOAT): Distracted student percentage.
- `drowsy_pct` (FLOAT): Drowsy / fatigued student percentage.
- `head_pose_board_focus_pct` (FLOAT): Gaze alignment with board/screen.
- `hand_raise_count` (INTEGER): Active student participation gestures.
- `pedagogical_recommendation` (VARCHAR(100)): Discrete intervention directive.
- `drowsiness_risk_score` (FLOAT): Forecasted micro-sleep risk [0.0, 100.0]%.
- `intervention_urgency_index` (FLOAT): Instructional pivot urgency [0.0, 100.0]%.
- `participation_rate_forecast` (FLOAT): Estimated response rate [0.0, 100.0]%.
- `evidence_hash` (VARCHAR(64)): Deterministic SHA-256 evidence fingerprint.
- `timestamp` (DATETIME): UTC timestamp of snapshot.

### 3. `audit_ledger` Table
Stores the continuous cryptographic SHA-256 block hash chain.
- `id` (INTEGER, PK): Internal record key.
- `block_index` (INTEGER): Sequential block number starting at Genesis Block #0.
- `timestamp` (VARCHAR(50)): ISO 8601 UTC timestamp string.
- `action_type` (VARCHAR(64)): Event type (`SYSTEM_INIT`, `ENGAGEMENT_EVALUATION`, etc.).
- `details` (TEXT): Audit event narrative and telemetry parameters.
- `previous_hash` (VARCHAR(64)): Hash of preceding block (Block #0 = 64 zeros).
- `current_hash` (VARCHAR(64)): SHA-256 hash of `action|details|timestamp|previous_hash`.
