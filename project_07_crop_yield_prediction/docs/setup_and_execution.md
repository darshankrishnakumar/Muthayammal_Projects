# Setup and Execution Guide: Crop Yield Prediction System (PROJECT-007)

## 1. System Requirements & Prerequisites
- **Operating System**: macOS Sonoma / Linux Ubuntu 22.04+ / Windows 11 (WSL2 recommended)
- **Python**: Python 3.10+ (tested on Python 3.10, 3.11, 3.12)
- **Node.js**: v18.0.0+ (for building React frontend or executing headless browser recordings)
- **Memory (RAM)**: Minimum 4 GB, Recommended 8 GB (for loading 209 MB scikit-learn models cache)
- **Disk Space**: ~1.5 GB free disk space for repository, virtual environment, and cached models

## 2. Environment Setup

### 2.1 Clone and Navigate to Directory
```bash
git clone https://github.com/darshankrishnakumar/Muthayammal_Projects.git
cd Muthayammal_Projects/project_07_crop_yield_prediction
```

### 2.2 Create and Activate Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r source_code/requirements.txt
```

Core dependencies installed:
- `flask`, `flask-cors`: Web server and REST API framework
- `scikit-learn==1.3.2`: ML models and preprocessing pipelines
- `pandas>=2.0.0`, `numpy>=1.24.0`: Tabular data processing and numerical arrays
- `joblib>=1.3.0`: High-performance serialized model persistence
- `pytest>=7.4.0`: Automated unit and integration testing suite

## 3. Database Initialization & Data Assets
The agricultural records database is embedded directly as:
- `source_code/data/yield_df.csv`: Complete FAO & World Bank dataset containing 28,242 records across 101 countries, 10 crop species, rainfall, pesticides, and temperatures.
- Relational SQLite database initialized automatically on startup (`crop_yield.db`) storing transactional query predictions, historical batch queries, and feedback logs.

## 4. Running the Application

### 4.1 Start the Microservice Backend & Frontend Server
The system runs as an integrated full-stack server serving the interactive React SPA and Flask REST API:
```bash
python3 source_code/backend_api.py
```
By default, the server listens on `http://127.0.0.1:5007`.

To configure custom host or port:
```bash
PORT=5007 HOST=0.0.0.0 python3 source_code/backend_api.py
```

### 4.2 Accessing the Interactive Web UI
Open your modern web browser (Google Chrome, Mozilla Firefox, Safari, or Microsoft Edge) and navigate to:
```
http://127.0.0.1:5007
```

Key features accessible via the navigation bar:
- **Dashboard (`#dashboard`)**: System KPIs, total records, average global yield, model benchmark leaderboard.
- **Predictions (`#predictions`)**: Single and batch crop yield prediction, confidence intervals, crop recommendations.
- **Exploration (`#exploration`)**: Data exploration, national yield trends, climate correlation matrices.
- **Visualizations (`#visualizations`)**: Model feature importance, residual distribution, regression diagnostics.

## 5. Automated Verification & Testing
Execute the complete regression and API test suite:
```bash
pytest source_code/tests/ -v
```
Expected output: 28 passing tests across model inference, boundary testing, API contracts, and database persistence.
