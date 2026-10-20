# Classroom Telemetry Dataset Documentation (PROJECT-047)

## Overview
- **File**: `data/classroom_telemetry_6000.csv`
- **Record Count**: 6,000 multimodal physical classroom telemetry records.
- **Attributes**: 16 tabular columns capturing affective, postural, and pedagogical metrics.

## Field Schema
1. `snapshot_id`: Unique session snapshot identifier (`ENG-2026-10000` to `ENG-2026-15999`).
2. `course_code`: `CS-301`, `MATH-210`, `AI-405`, `BIO-108`.
3. `course_name`: Academic course title.
4. `instructor_name`: Lead faculty member.
5. `student_count`: Active attendance count (24 to 45 students).
6. `mean_engagement_score`: Continuous engagement score [0.0, 100.0]%.
7. `attentive_pct`: Attentive student percentage [0.0, 100.0]%.
8. `bored_pct`: Bored student percentage [0.0, 100.0]%.
9. `distracted_pct`: Distracted / device use percentage [0.0, 100.0]%.
10. `drowsy_pct`: Fatigued / slumping percentage [0.0, 100.0]%.
11. `head_pose_board_focus_pct`: Gaze alignment percentage [0.0, 100.0]%.
12. `hand_raise_count`: Active participation gesture count [0, 15].
13. `pedagogical_recommendation`: Target instructional directive.
14. `drowsiness_risk_score`: Predicted micro-sleep risk [0.0, 100.0]%.
15. `intervention_urgency_index`: Instructional urgency score [0.0, 100.0]%.
16. `participation_rate_forecast`: Expected response rate [0.0, 100.0]%.
