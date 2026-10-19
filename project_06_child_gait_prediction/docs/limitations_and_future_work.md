# Limitations and Future Work - Child Gait Prediction System

## 1. Current System Limitations

1. **Clinical Cohort Size**:
   The real motion capture dataset comprises 21 trials across 14 pediatric subjects. While participant-level zero-leakage cross-validation prevents overfitting, expanding data collection to hundreds of participants across multiple hospital gait labs is necessary for broad regulatory validation.
2. **Three-Class Taxonomy**:
   The current taxonomy targets Normal, Diplegic, and Hemiplegic gaits. Less common pediatric neuromuscular conditions, such as ataxic gait, dystonia, and idiopathic toe walking, require separate modeling.
3. **Manual Parameter Ingestion**:
   Kinetic parameters currently require discrete entry or CSV file upload. Direct integration with wearable IMU Bluetooth streams is not yet automated.

---

## 2. Roadmap & Future Improvements

1. **Computer Vision Pose Estimation**:
   Integrate 2D/3D markerless video pose tracking (e.g., MediaPipe, OpenPose) to automatically compute joint kinematics directly from commodity smartphone recordings.
2. **Smart Insole IoT Integration**:
   Connect Bluetooth Low Energy (BLE) pressure-sensing insoles to stream continuous plantar pressure matrices directly to the FastAPI backend.
3. **Multi-Center Clinical Trials**:
   Partner with pediatric orthopedic centers to validate the model across pre-operative and post-operative surgical cohorts (e.g. single-event multilevel surgery - SEMLS).
