# Dataset Directory

Place your real child gait dataset here (e.g., `dataset.csv`).

### Expected / Target Gait Parameters:
1. `heel_pressure` (Heel Pressure, e.g. in kPa)
2. `toe_pressure` (Toe Pressure, e.g. in kPa)
3. `tilt_angle` (Tilt Angle, e.g. in degrees)
4. `step_duration` (Step Duration, e.g. in seconds)
5. `stride_length` (Stride Length, e.g. in cm)
6. `walking_speed` (Walking Speed, e.g. in m/s)

### Target Column (Class Labels):
- `gait_pattern` or `label` containing: `Normal`, `Diplegic`, `Hemiplegic`

*Note: If your dataset uses different column names or includes additional columns (such as age, gender, child_id), the inspection step in `src/preprocessing.py` will report them so they can be mapped accurately without fabricating data.*
