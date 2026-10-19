# Maintenance & Operational Manual: AERO-RUL

## 1. Routine Fleet Monitoring Workflow
1. Dispatchers review the real-time Fleet Health score and Grounded AOG counter on the dashboard header.
2. Select any turbofan subsystem from the top card carousel to inspect real-time degradation metrics.
3. Review C-MAPSS physical sensor gauges:
   - Verify EGT margin remains positive (+15°C or higher).
   - Check broadband vibration levels are below 1.5g RMS.
4. Inspect the Weibull Degradation Decay Curve for inflection points approaching the 30% safety threshold.

## 2. Airworthiness Action Directives
- **AIRWORTHY / OPTIMAL**: Normal line operation. Component permitted for continued on-wing flight hours. Standard scheduled A-check maintenance applies.
- **MAINTENANCE DUE SOON**: Schedule borescope inspection within the next 75 flight cycles. Elevate trend monitoring frequency on FADEC downloads.
- **GROUNDED / MANDATORY SHOP VISIT**: Immediate Aircraft on Ground (AOG) alert. Issue engine teardown directive. Perform non-destructive eddy-current and ultrasonic crack detection on blade roots and bearing races.

## 3. Maintenance Shop Order (MSO) Creation
Click `+ New MSO` in the dashboard or execute:
```bash
curl -X POST http://127.0.0.1:5033/api/shop-orders   -H "Content-Type: application/json"   -d '{"component_id": "COMP-TURB-01", "priority": "HIGH", "defect_summary": "EGT margin drop to 12C", "assigned_technician": "Lead Inspector", "estimated_downtime_hrs": 24.0}'
```
