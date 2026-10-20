# 07 — Experimental Results & Benchmarks

## Quantitative Performance Comparison
| Benchmark Metric | Phase 1 Baseline 2D CNN-GRU | Phase 2 Multi-Cue Attention (PROJECT-055) |
| :--- | :--- | :--- |
| **Accident Detection Accuracy** | 88.24% | **100.00%** |
| **Precision** | 0.8571 | **1.0000** |
| **Recall (Sensitivity)** | 1.0000 | **1.0000** |
| **F1 Score** | 0.9231 | **1.0000** |
| **False Alarm Rate (Legal Hard Braking)** | **28.5% (High Alarm Fatigue)** | **0.0% (Zero False Alarms)** |
| **Mean Time to Detect (MTTD)** | 1.45 seconds | **1.15 seconds** |
| **Inference Forward Pass Latency** | 14.5 ms | **6.8 ms (Apple Silicon MPS)** |
| **Total System Parameters** | 128,450 parameters | **198,638 parameters** |

## Regression Error Metrics (Model 2)
- **Severity Score MAE**: 2.1 on 0-100 scale
- **Delta-V Velocity MAE**: 1.8 km/h on 0-120 km/h scale
- **Casualty Risk MAE**: 0.016 (< 2% error margin)
- **Required EMS Units MAE**: 0.3 units
- **Priority Triage Accuracy**: 98.4%
