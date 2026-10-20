# Video Walkthrough Script: AI Waste Classification & Autonomous Sorting System

**Project**: PROJECT-036  
**Target Duration**: 180.000s (03:00)  
**Resolution**: 1280x800 Widescreen  
**Endpoint**: `http://127.0.0.1:5036/`

---

### [00:00 - 00:30] Phase 1: MRF Sorting Command Dashboard & Health
- **Visual**: The video opens on the SORT-AI industrial CleanTech dashboard running on assigned Port 5036. The status pill displays `Active (:5036)` with a pulsating emerald indicator. The header and conveyor selector bar demonstrate multi-line operations across Municipal Containers (A1), Fiber Recovery (B2), and Organic (C3).
- **Narrator**: "Welcome to the technical demonstration of PROJECT-036: AI Waste Classification and Autonomous Sorting System. Designed for modern Material Recovery Facilities, this system combines optical Near-Infrared hyperspectral feature extraction and deep residual neural networks to automate high-speed material diversion on Port 5036."

---

### [00:30 - 01:00] Phase 2: Optical Conveyor Simulation Canvas & Lines
- **Visual**: The viewport focuses smoothly on the high-speed conveyor viewport. The animated canvas renders continuous rollers moving at 1.2 m/s beneath an active Near-Infrared optical scanning laser. The operator switches to `CONV-B2: Commercial Fiber Line (OCC & Deinked Paper)`, updating line velocity to 1.8 m/s and loading OptoGrip sensor calibration.
- **Narrator**: "In Phase 2, we inspect the optical inspection conveyor. Operating at 30 FPS, the system tracks moving objects beneath a hyperspectral NIR laser beam. Switching to Conveyor B2 configures the pipeline for high-speed commercial fiber recovery at 1.8 meters per second, synchronizing downstream mechanical diversion actuators."

---

### [01:00 - 01:30] Phase 3: Polymer Classification & Pneumatic Air Jet
- **Visual**: Programmatic trigger `classifyItem('plastic_bottle')` introduces a PET beverage container onto the belt. Spectroscopic gauges update: Density at 0.95 g/cm³, NIR Reflectance at 0.720, and Opacity at 35.0%. The result banner displays `Plastic` with 98.8% certainty, and the `Bin-A` pneumatic air-jet indicator lights up.
- **Narrator**: "Phase 3 demonstrates polymer classification. As a plastic container crosses the optical sensor, the system evaluates density at 0.95 g/cm³ and NIR reflectance at 0.720. The PyTorch WasteMaterialClassifierNet identifies it as Plastic with 98.8% confidence, firing Pneumatic Air Jet Number 1 to blast the container into Bin-A within 35 milliseconds."

---

### [01:30 - 02:00] Phase 4: Metallic Separation & Eddy Current Diverter
- **Visual**: The operator triggers `classifyItem('aluminum_can')`. Density shifts to 2.70 g/cm³, NIR reflectance peaks at 0.940, and optical opacity reaches 99.5%. The classification engine predicts `Metal` with 99.2% confidence. The `Bin-C` indicator flashes active, showing Eddy Current Diverter engagement.
- **Narrator**: "In Phase 4, we evaluate metallic item separation. An aluminum can presents characteristic high density and 99.5% optical opacity. The neural regressor predicts a 96.0% recyclability score with minimal contamination, triggering the Eddy Current Diverter to project the item into the non-ferrous recovery stream."

---

### [02:00 - 02:30] Phase 5: Corrugated Cardboard Recovery & Star Screen
- **Visual**: Programmatic trigger `classifyItem('corrugated_box')` scans an Old Corrugated Cardboard box. Surface roughness increases to 19.5 um with opacity at 98.5%. The system predicts `Cardboard` with 98.5% confidence and routes the item to `Bin-E` via Rotary Star Screen #5.
- **Narrator**: "Phase 5 demonstrates fibrous cardboard recovery. The laser displacement sensor detects high surface roughness at 19.5 micrometers. With a 92.0% recyclability index, the item is diverted via high-angle rotary star-screens into Bin-E for immediate baling and dispatch to downstream paper mills."

---

### [02:30 - 03:00] Phase 6: Commercial Dispatched Batches & Audit Ledger
- **Visual**: The view scrolls smoothly to the dispatched commercial recycling batches and cryptographic audit ledger tables. Batches dispatched to International Paper Mill and Alcoa Aluminum are rendered with purity grades (Grade A/A+). The audit table displays SHA-256 cryptographic hashes for every classified item.
- **Narrator**: "Finally, in Phase 6, we review the commercial batch dispatch logs and regulatory audit ledger. All sorting operations and purity certifications are committed with ACID guarantees to an SQLite database in Write-Ahead Logging mode. Every classification is sealed with a SHA-256 cryptographic hash, ensuring complete compliance under EPA Title 40 CFR and ASTM D5231 recycling standards."
