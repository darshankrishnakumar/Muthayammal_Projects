# Maintenance & Operational Manual: ROAD-AI

## 1. Daily Road Survey Workflow
1. Municipal survey operators select a target corridor from the sector dropdown.
2. Ingest UAV aerial or vehicular dashcam telemetry.
3. Review detected bounding boxes and class tags on the HTML5 Road Canvas:
   - Verify D40 potholes are prioritized for emergency patch cold rolling.
   - Inspect alligator cracking zones (D20) for full-depth reclamation.
4. Review Pavement Condition Index (PCI) and International Roughness Index (IRI).

## 2. Pavement Condition Thresholds
- **GOOD (STRUCTURALLY SOUND)** (PCI >= 70): Pavement exhibits minor weathering. Schedule standard preventive crack sealing.
- **FAIR (MAINTENANCE REQUIRED)** (45 <= PCI < 70): Intermediate structural distress. Schedule asphalt overlay within 90 days.
- **POOR (CRITICAL RESURFACING)** (PCI < 45): Critical sub-base failure. Dispatch emergency work order for cold milling and full-depth reconstruction.

## 3. Municipal Work Order (MWO) Creation
Click `+ New MWO` on the dashboard or execute:
```bash
curl -X POST http://127.0.0.1:5034/api/work-orders   -H "Content-Type: application/json"   -d '{"sector_id": "SEC-NORTH-01", "priority": "HIGH", "remediation_scope": "Emergency asphalt patch on D40 potholes", "assigned_contractor": "Apex Highway Maintenance Corp", "budget_allocated_usd": 6500}'
```
