# SORT-AI System Architecture & Industrial Conveyor Topology

## 1. High-Level Architecture
SORT-AI is an autonomous, multi-spectral robotic waste classification and diversion system engineered for Material Recovery Facilities (MRFs). It operates as an integrated pipeline executing high-speed optical Near-Infrared (NIR) sensing, deep residual neural network classification, multi-task recyclability regression, and high-speed pneumatic air-jet diversion on **Port 5036**.

```
[Infeed Municipal Recyclable Stream]
                │
                ▼
[High-Speed Optical Conveyor Belt (1.2 - 1.8 m/s)]
                │
    ┌───────────┴───────────────────────────┐
    ▼                                       ▼
[Hyperspectral NIR Spectrometer]     [High-Speed Color Vision]
  - 750nm - 1700nm Band Albedo         - 1280x800 @ 30 FPS
  - Substrate Absorption Fingerprint   - 2D Bounding Box Localization
    │                                       │
    └───────────────────┬───────────────────┘
                        ▼
   [8-D Normalized Spectroscopic Telemetry Vector]
     [Density, NIR Reflectance, Opacity, Roughness,
      Moisture, Rigidity, Magnetic, Carbon Footprint]
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
[WasteMaterialClassifierNet]     [RecyclabilityScoreRegressorNet]
  - Residual MLP (LayerNorm)       - Shared Representation Backbone
  - 6 Material Streams             - Recyclability Index (0-100%)
  - 98.83% Test Accuracy           - Contamination Risk [0.0, 1.0]
       │                                 │
       └────────────────┬────────────────┘
                        ▼
    [High-Speed Pneumatic & Mechanical Actuator Manifold]
     ├── Bin-A: Plastic (6-bar Pneumatic Air Jet #1)
     ├── Bin-B: Glass (Servo Mechanical Flipper #2)
     ├── Bin-C: Metal (Eddy Current Repulsive Rotor #3)
     ├── Bin-D: Paper (Overhead Vacuum Suction Gantry #4)
     ├── Bin-E: Cardboard (Rotary Star-Screen Disc Separator #5)
     └── Bin-F: Organic (Automated Trapdoor Drop #6)
                        │
                        ▼
[ACID SQLite Storage ('waste_sorting.db' in WAL Mode)]
  - Conveyor Line Configurations & Sensors
  - Real-Time Item Telemetry & Bins
  - Dispatched Commercial Batches
  - Cryptographic SHA-256 Audit Ledger
```

## 2. Sensor Hardware Specifications
- **Optical Camera**: 1/2.8" Global Shutter CMOS, 1280x800 resolution @ 30 FPS.
- **NIR Spectrometer**: SpectraCam NIR-850 hyperspectral array (850nm - 1700nm).
- **Weigh-in-Motion**: Dual strain-gauge dynamic load cells with 10g precision.
- **Magnetic Sensor**: High-frequency eddy current inductive sensor array.
