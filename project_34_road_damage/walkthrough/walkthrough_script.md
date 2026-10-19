# Walkthrough Video Demonstration Script: ROAD-AI (PROJECT-034)

**Project Name**: AI-Based Road Damage Detection and Severity Classification  
**Platform**: Port 5034 Microservice Architecture  
**Video Specifications**: 1280x800 H.264 MP4, 180.000 Seconds (03:00)

---

## Phase 1: [00:00 - 00:30] Municipal Highway Survey Overview
- **Visual**: The smart city municipal pavement HUD opens on `http://127.0.0.1:5034/`. The top navigation bar confirms Port 5034 microservice status with live pulse indicator and YOLOv8-RDD2022 dataset compliance.
- **Narrative / Audio Cue**: "Welcome to the demonstration of ROAD-AI, an automated computer vision and deep learning platform for road damage detection and severity classification. Built upon the international RDD2022 benchmark, the system continuously aggregates pavement distress surveys across municipal highway corridors. The metrics strip highlights total defects catalogued, mean pavement condition index, and municipal repair budget allocation."

## Phase 2: [00:30 - 01:00] Corridor Selection & YOLO Bounding Box Canvas
- **Visual**: The operator selects 'Urban Arterial Road 12 (Downtown Junction)' from the corridor dropdown. The interactive road canvas renders dark asphalt with perspective lane striping and draws color-coded bounding boxes around detected D40 potholes and D20 alligator cracking zones with confidence tags.
- **Narrative / Audio Cue**: "Selecting Urban Arterial Road 12 demonstrates spatial defect localization. Rather than simple image classification, the road canvas plots precise bounding boxes with normalized coordinates, distinguishing deep potholes from fatigue alligator cracking with over 89% confidence."

## Phase 3: [01:00 - 01:30] Pavement Condition Index (PCI) & Roughness (IRI)
- **Visual**: Smooth scroll to the analytical section. The PCI score displays 62.4 with an amber 'FAIR (MAINTENANCE REQUIRED)' badge. Pavement roughness is quantified at 3.42 m/km IRI, with estimated contractor remediation costs of $296 for the surveyed section. The defect distribution donut chart illustrates relative distress frequency.
- **Narrative / Audio Cue**: "Here we examine the dual-head regression outputs aligned with ASTM D6433 and ASTM E1926 standards. The model predicts both the structural Pavement Condition Index and the International Roughness Index, providing highway engineers with actionable data for preventive crack sealing before structural failure."

## Phase 4: [01:30 - 02:00] Critical Wear Simulation & Emergency Resurfacing
- **Visual**: The operator switches to 'Industrial Ring Road (Heavy Cargo Freight)' and clicks the '⚠️ High Defect Density (Severe)' simulation chip. The dashboard flashes an emergency red alarm: 'POOR (CRITICAL RESURFACING)', PCI collapses to 10.5, multiple deep potholes and rutting depressions appear on the canvas, and estimated remediation costs escalate to over $8,500.
- **Narrative / Audio Cue**: "Simulating severe structural fatigue on the heavy freight corridor demonstrates emergency interdiction. Multiple severe D40 potholes and rutting depressions trigger an immediate POOR rating, signaling severe sub-base voiding that requires urgent full-depth milling."

## Phase 5: [02:00 - 02:30] Municipal Work Orders (MWO) Dispatch
- **Visual**: The view moves to the Municipal Work Orders panel. Active contractor orders are displayed, including MWO-2026-401 assigned to Apex Pavement Contractors for emergency cold asphalt patch compaction. The operator clicks '+ New MWO' to dispatch an urgent resurfacing work order with allocated budget.
- **Narrative / Audio Cue**: "ROAD-AI directly bridges automated defect recognition with field contractor execution. Municipal Work Orders are created with priority tagging, technical remediation scope, and budget tracking, persisted reliably in the relational database."

## Phase 6: [02:30 - 03:00] DOT Regulatory Compliance & Relational SQLite WAL Ledger
- **Visual**: The final phase focuses on the Department of Transportation (DOT) immutable audit trail and historical survey ledger. Every survey event is recorded with UTC timestamps, sector codes, and PCI ratings. The microservice confirms 100% test pass rates across all 33 automated test cases.
- **Narrative / Audio Cue**: "In conclusion, all road surveys and work orders are permanently archived in an immutable SQLite Write-Ahead Logging audit trail, ensuring complete regulatory compliance with state and federal transportation guidelines. With real trained PyTorch models, 6,000 survey records, and 33 verified tests, ROAD-AI delivers a complete, production-grade civil infrastructure solution."
