# Regulatory Compliance & Civil Engineering Standards (ASTM / DOT / FHWA)

## 1. Regulatory Context
ROAD-AI complies strictly with international and federal civil transportation standards:
- **ASTM D6433-20**: Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys.
- **ASTM E1926-08**: Standard Practice for Computing International Roughness Index (IRI) of Roads from Longitudinal Profile Measurements.
- **AASHTO Guide for Design of Pavement Structures**: American Association of State Highway and Transportation Officials.
- **FHWA Highway Performance Monitoring System (HPMS)**: Federal Highway Administration guidelines for state road network reporting.

## 2. PCI Deduct Value Calibration
The PCI calculation mirrors ASTM D6433 deduct curves, penalizing distress based on physical depth, affected area, and heavy commercial axle ratios.

## 3. Municipal Non-Repudiation Audit Trail
The system maintains an immutable audit log in SQLite table `audit_log` with ISO-8601 UTC timestamps, logging all inspection passes and contractor work order allocations.
