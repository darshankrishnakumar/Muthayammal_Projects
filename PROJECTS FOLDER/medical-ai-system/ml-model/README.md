# 1D CNN Machine Learning Environment for ECG Arrhythmia Classification

Dedicated Python machine learning environment for ECG signal preprocessing, dataset ingestion (MIT-BIH Arrhythmia Database), and 1D Convolutional Neural Network (CNN) model development.

---

## 1. Directory Structure

```
ml-model/
├── .venv/                   # Dedicated Python virtual environment
├── dataset/
│   └── mit-bih/             # MIT-BIH Arrhythmia Database recordings
├── preprocessing/           # ECG filtering, baseline removal, R-peak detection, beat segmentation
├── training/                # 1D CNN model architecture definition & training pipelines
├── saved-model/             # Trained model checkpoints & exported formats (Keras / TF.js)
├── evaluation/              # Model evaluation metrics, confusion matrices, ROC curves
├── verify_env.py            # Software environment verification script
├── requirements.txt         # Pinned compatible package versions
├── .gitignore
└── README.md
```

---

## 2. Environment Details

* **Operating System**: Microsoft Windows 11 Home Single Language (64-bit, x64 architecture)
* **Python Version**: Python 3.14.6 (64-bit)
* **Virtual Environment Path**: `ml-model/.venv/`

### Installed Packages & Verified Versions

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`tensorflow`** | `2.22.0rc0` | 1D CNN model building, Keras API, training & forward inference |
| **`numpy`** | `2.5.3` | High-performance array operations on raw ECG voltage arrays |
| **`pandas`** | `3.0.6` | Dataset metadata tables, annotation handling & metrics logs |
| **`wfdb`** | `4.3.1` | Reading PhysioNet / MIT-BIH ECG recordings and beat annotation files |
| **`scipy`** | `1.18.1` | Butterworth bandpass filtering, notch filter (50/60 Hz), resampling |
| **`scikit-learn`** | `1.9.1` | Stratified train/val/test splitting, precision, recall, F1-scores |
| **`matplotlib`** | `3.11.2` | Plotting ECG wave traces, loss curves, and training history |
| **`seaborn`** | `0.13.2` | Confusion matrix heatmaps and class distribution visualizations |

---

## 3. Virtual Environment Setup & Activation

### Windows (PowerShell / Command Prompt)

```powershell
# Navigate to the ml-model directory
cd "c:\Users\hackd\Downloads\medical ai .16\ml-model"

# Create virtual environment (if creating fresh)
python -m venv .venv

# Activate virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# (Or in Command Prompt cmd.exe)
.\.venv\Scripts\activate.bat
```

> **Note for PowerShell execution policy:** If script execution is restricted, run using the virtual environment's Python executable directly:
> ```powershell
> & ".\.venv\Scripts\python.exe" script_name.py
> ```

### macOS / Linux (Reference)

```bash
cd ml-model
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4. Package Installation & Verification

### Install Dependencies
To install the verified dependencies from `requirements.txt`:

```powershell
# Windows
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# macOS / Linux
python -m pip install -r requirements.txt
```

### Run Environment Verification Test
Execute the test script to verify that all imports work and that a sample 1D CNN forward pass succeeds:

```powershell
# Windows
.\.venv\Scripts\python.exe verify_env.py

# macOS / Linux
python verify_env.py
```

---

## 5. Development Workflow & Next Steps

1. **Preprocessing (`preprocessing/`)**:
   * Implement 0.5–45 Hz bandpass filtering using `scipy.signal` to remove baseline wander and high-frequency EMG noise.
   * Parse MIT-BIH annotations via `wfdb.rdann` and extract segmented heartbeat windows (e.g., 187 sample points centered on R-peaks).
2. **Dataset Loading (`dataset/mit-bih/`)**:
   * Download MIT-BIH Arrhythmia Database records (records 100 to 234) into `dataset/mit-bih/`.
3. **Model Architecture (`training/`)**:
   * Construct 1D CNN using `tf.keras.layers.Conv1D`, `MaxPooling1D`, `BatchNormalization`, `Dropout`, and `Dense`.
   * Target classes (AAMI EC57 standards): Normal (N), Supraventricular ectopic (S), Ventricular ectopic (V), Fusion (F), Unknown (Q).
4. **Model Export (`saved-model/`)**:
   * Save trained model in Keras format (`.keras`) and prepare for conversion to TensorFlow.js for browser/backend inference.
