# Setup and Execution Guide: Customer Churn Intelligence System (PROJECT-008)

## 1. System Requirements & Prerequisites
- **Operating System**: macOS Sonoma / Linux Ubuntu 22.04+ / Windows 11 (WSL2 recommended)
- **Python**: Python 3.10+ (tested on Python 3.10, 3.11, 3.12)
- **Node.js**: v18.0.0+ (required for Puppeteer automated screen capture and video recording)
- **FFmpeg**: Required for headless MP4 video rendering (`brew install ffmpeg` on macOS)
- **Memory (RAM)**: Minimum 4 GB, Recommended 8 GB
- **Disk Space**: ~500 MB for models, database, and test assets

## 2. Environment Setup

### 2.1 Clone and Navigate to Directory
```bash
git clone https://github.com/darshankrishnakumar/Muthayammal_Projects.git
cd Muthayammal_Projects/project_08_customer_churn_prediction
```

### 2.2 Create and Activate Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install shap lifelines flask scikit-learn matplotlib pandas numpy pytest
```

## 3. Database Initialization & Pre-Seeding
The application manages its own SQLite database automatically:
- Database location: `source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/predictions.db`
- Auto-seeding: Upon initial startup, `seed_db.py` inspects `predictions.db` and loads 15 verified benchmark subscriber records from `Telco-Customer-Churn.csv` if the table is empty.

## 4. Running the Application

### 4.1 Launch Microservice Backend & Web UI
Execute the main application script:
```bash
python3 source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/app.py
```
By default, the microservice listens on **Port 5008**:
```
http://127.0.0.1:5008
```

To configure custom port or network interfaces:
```bash
PORT=5008 HOST=0.0.0.0 python3 source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/app.py
```

### 4.2 Interactive Web Navigation
Navigate your browser to `http://127.0.0.1:5008`:
- **Dashboard (`/`)**: Executive statistics, churn rate donut chart, recent evaluations.
- **Predict Churn (`/predict`)**: Input subscriber demographics, services, contract terms, and compute risk.
- **Model Performance (`/model-performance`)**: View confusion matrix, ROC curve, and classification metrics.
- **History (`/history`)**: Inspect historical SQLite audit records.

## 5. Automated Testing & Verification
Execute the automated test suite with pytest:
```bash
pytest source_code/tests/ -v
```
Expected output: **23 passing tests (100% pass rate)** in under 3.0 seconds.
