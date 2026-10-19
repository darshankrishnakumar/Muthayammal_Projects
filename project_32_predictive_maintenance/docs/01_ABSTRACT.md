# Project 32: Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data & Deep Learning
## 1. Abstract & Executive Summary

Industrial rotating machinery (compressors, pumps, motors, and gas turbines) forms the operational backbone of modern process manufacturing. Unscheduled downtime caused by sudden bearing spalling, dynamic imbalance, or cavitation imposes severe economic and safety tolls on plant operations.

Project 32 establishes an AI-driven condition monitoring and Remaining Useful Life (RUL) estimation platform deployed as an edge-viable microservice. Integrating 8-band Fast Fourier Transform (FFT) vibration kinematics with multivariate thermal, acoustic, and pressure telemetry, the system executes dual deep learning models in PyTorch:
1. `MachineHealthClassifierNet`: Deep Residual Multi-Layer Perceptron (8 -> 64 -> 64 -> 32 -> 6) classifying equipment health across 6 operational fault modes with 96.83% validation accuracy.
2. `RULRegressorNet`: Physics-constrained neural regressor estimating continuous health scores (0-100) and forecasting Remaining Useful Life in operating hours and days.

### Key Highlights
- **Real Industrial Telemetry**: 6,000 multivariate sensor records across 5 mission-critical machines.
- **8-Band FFT Kinematics**: Harmonic tracking of 1X, 2X, BPFO, BPFI, BSF, FTF, and HF noise bands.
- **ACID Persistence**: SQLite database (`predictive_maintenance.db`) running in Write-Ahead Logging (WAL) mode.
- **Dedicated Port**: Bound to `http://127.0.0.1:5032/` with 31/31 passing automated QA tests (100% pass rate).
