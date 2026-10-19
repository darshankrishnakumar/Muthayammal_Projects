# Commercial Driver Fatigue Telemetry Dataset Guide

## 1. Overview
The benchmark dataset (`driver_fatigue_telemetry_6000.csv`) comprises 6,000 multi-modal temporal survey records captured across 5 distinct commercial driver personas operating heavy commercial equipment under realistic highway and urban conditions.

## 2. Monitored Commercial Driver Personas
1. **DRV-801 (Marcus Vance)**: Freightliner Cascadia Class 8 Semi-Trailer; Route: I-80 Cross-Country Interstate; Shift: Nocturnal Long-Haul (22:00 - 08:00).
2. **DRV-802 (Elena Rostova)**: New Flyer Xcelsior Transit Bus; Route: Metro Route 44 Express; Shift: Morning Commuter Peak (05:30 - 14:00).
3. **DRV-803 (Devon Miller)**: Toyota Camry Hybrid; Route: Metropolitan Rideshare Corridor; Shift: Evening Congestion (16:00 - 00:00).
4. **DRV-804 (Kavita Rao)**: Peterbilt 579 Cryogenic Tanker; Route: Gulf Coast Chemical Transit; Shift: Graveyard Hazardous Cargo (00:00 - 09:00).
5. **DRV-805 (Lucas Silva)**: Mercedes-Benz Sprinter Cargo Van; Route: Urban Last-Mile Logistics; Shift: Afternoon Multidrop (12:00 - 20:00).

## 3. Physical Feature Schema
| Feature | Type | Range | Description |
|---|---|---|---|
| `ear` | Float | 0.12 - 0.42 | Eye Aspect Ratio (Droop < 0.22, Open ~ 0.35) |
| `mar` | Float | 0.08 - 0.78 | Mouth Aspect Ratio (Yawn > 0.45, Nominal ~ 0.16) |
| `blink_duration_ms` | Float | 100 - 950 ms | Total blink duration (Microsleep > 400ms) |
| `blink_frequency_cpm` | Float | 6 - 48 /min | Blinks per minute |
| `head_pitch_deg` | Float | -28° to +22° | Forward nodding angle (Nod < -15°) |
| `head_yaw_deg` | Float | -35° to +35° | Lateral glance angle |
| `head_roll_deg` | Float | -22° to +22° | Lateral head tilt |
| `perclos_pct` | Float | 2.0% - 68.0% | Percentage of eye closure > 80% (NHTSA) |
| `drowsiness_state` | Categorical | 4 Classes | Alert, Slightly Drowsy, Moderately Drowsy, Severely Drowsy |
| `vigilance_score` | Float | 5.0% - 99.5% | Continuous Driver Vigilance Index |
| `microsleep_risk` | Float | 0.0 - 1.0 | Continuous probability of imminent micro-sleep |
