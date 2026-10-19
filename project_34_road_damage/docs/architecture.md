# System Architecture: ROAD-AI (PROJECT-034)

## 1. High-Level Architectural Flow
ROAD-AI is an autonomous Civil Transportation Infrastructure inspection system designed to detect, classify, and evaluate road surface distress across municipal and highway networks.

```
+-----------------------------------------------------------------------------------+
|                           MUNICIPAL ROAD SURVEY NETWORK                           |
|   Highway Sector A4 | Urban Arterial 12 | Industrial Ring | Residential | Mountain|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         UAV / VEHICULAR SENSOR INGESTION                          |
|   Surface Area (m²) | Pothole Depth (cm) | Crack Width (mm) | Traffic Volume (VPD)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    PYTHON / FLASK REST MICROSERVICE (PORT 5034)                   |
|                                                                                   |
|  +-------------------------------------+   +------------------------------------+  |
|  |   RoadDamageYOLOClassifierNet       |   |   PavementConditionRegressorNet    |  |
|  |   Deep Residual MLP (BatchNorm/GELU)|   |   Dual-Head LayerNorm MLP          |  |
|  |   Accuracy: 76.08% | 5 Defect Modes |   |   PCI Score (0-100) & IRI Roughness|  |
|  +-------------------------------------+   +------------------------------------+  |
|                                         |                                         |
|  +-------------------------------------+   +------------------------------------+  |
|  |   Relational SQLite (WAL Mode)      |   |   Smart City Municipal Survey HUD  |  |
|  |   5 Schemas + Immutable Audit Trail |   |   HTML5 Canvas Bounding Box Display|  |
|  +-------------------------------------+   +------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 2. Core Defect Taxonomies
1. **D40 - Deep Pothole**: Severe depression penetrating sub-base layer. $140/m² cold/hot patch repair.
2. **D20 - Alligator Cracking**: Interconnected fatigue cracking network. $95/m² full-depth reclamation.
3. **D00 - Longitudinal Crack**: Seam-parallel linear cracks. $45/m² rubberized bitumen seal.
4. **D10 - Transverse Crack**: Centerline-perpendicular thermal shrinkage cracks. $50/m² sealant injection.
5. **D43 - Rutting & Wheel Depression**: Permanent wheel-path rutting. $110/m² asphalt milling & overlay.

## 3. Data Persistence Layer
- SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
- 5 Relational Schemas: `road_sectors`, `damage_inspections`, `pavement_defects`, `municipal_work_orders`, `audit_log`.
