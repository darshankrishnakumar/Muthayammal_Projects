# 02. System Requirements Specification (PROJECT-028)

## Functional Requirements (FR)
- **FR-1 [Continuous Telemetry Ingestion]:** Ingest and standardize 10 atmospheric and meteorological features: PM2.5, PM10, NO2, SO2, CO, O3, Temperature, Humidity, Wind Speed, and Planetary Boundary Layer Height.
- **FR-2 [24-Hour Sequence-to-Sequence Forecasting]:** Execute PyTorch Bi-LSTM forward pass over 24-hour lookback windows to predict multi-step 24-hour future trajectories.
- **FR-3 [EPA AQI Hazard Categorization]:** Classify atmospheric vectors into 6 official EPA categories: Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous.
- **FR-4 [Meteorological Coupling]:** Incorporate boundary layer height and horizontal wind dispersion velocities into pollution dilution estimates.
- **FR-5 [Clinical Advisory Synthesis]:** Automatically trigger lifestyle and medical advisories (N95 respirators, HEPA filtration, exercise postponement) based on AQI thresholds.
- **FR-6 [Relational ACID Persistence]:** Log every forecast execution, 24-hour predictions, and audit events to SQLite `air_quality.db`.
- **FR-7 [Interactive Metro Dashboard]:** Host a responsive web interface on Port 5028 supporting station switching across 10 international metropolises.

## Non-Functional Requirements (NFR)
- **NFR-1 [Inference Latency]:** Total neural inference turnaround for 24-hour sequence forecasting must complete under 20 milliseconds on commodity CPU hardware.
- **NFR-2 [Classification Accuracy]:** Environmental hazard classification accuracy must exceed 90.0% on unseen test splits.
- **NFR-3 [Database Concurrency]:** SQLite database must operate in WAL mode with a 30-second busy timeout to eliminate write lock contention.
- **NFR-4 [Scalability]:** Architecture must support modular addition of new monitoring stations without requiring model re-architecting.
