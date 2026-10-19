# Dataset Card: PhysioNet MIT-BIH Arrhythmia Database

## 1. Dataset Overview
- **Source**: PhysioNet MIT-BIH Arrhythmia Database (Massachusetts Institute of Technology & Beth Israel Hospital).
- **Records**: 48 half-hour two-lead ambulatory ECG recordings collected from 47 subjects.
- **Sampling Frequency**: 360 Hz per channel with 11-bit resolution over a 10 mV range.
- **Total Annotated Heartbeats**: 109,449 beats annotated by independent clinical cardiologists.

## 2. AAMI EC57 Standardization Mapping
To enable consistent automated evaluation, detailed PhysioNet annotations are mapped into five AAMI standard diagnostic superclasses:

| AAMI Class | Description | PhysioNet Beat Annotations Included |
|---|---|---|
| **Class N** | Normal Sinus Rhythm | Normal beat (NOR), Left bundle branch block (LBBB), Right bundle branch block (RBBB), Atrial escape (AE), Nodal escape (NE) |
| **Class S** | Supraventricular Ectopic Beat | Atrial premature beat (APB), Aberrated APB (aAPB), Nodal premature (NP), Supraventricular premature (SVP) |
| **Class V** | Ventricular Ectopic Beat | Premature ventricular contraction (PVC), Ventricular escape beat (VE) |
| **Class F** | Fusion Beat | Fusion of ventricular and normal beat (fVN) |
| **Class Q** | Unknown / Paced Beat | Paced beat (P), Fusion of paced and normal (fPN), Unclassifiable beat (U) |

## 3. Data Preprocessing & Conditioning
1. **Filtering**: 2nd-order bidirectional Butterworth bandpass filter (0.5 - 40.0 Hz) to eliminate baseline drift and powerline hum.
2. **QRS Detection**: Canonical Pan-Tompkins energy-derivative detector localizing R-peaks.
3. **Segmentation**: Slicing fixed windows of 187 samples centered on detected R-peaks (-93 to +93 samples @ 360 Hz).
4. **Normalization**: Per-beat Z-score standardization ($x_{norm} = \frac{x - \mu}{\sigma}$).
