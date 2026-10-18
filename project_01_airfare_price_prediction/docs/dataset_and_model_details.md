# Dataset & Model Specifications

## 1. Dataset Provenance & Overview
- **Source**: Kaggle Flight Fare Prediction Dataset (Indian Domestic Aviation Market).
- **Physical File**: `source_code/datasets/Data_Train.xlsx`
- **Total Records**: 10,683 observations.
- **Attributes**:
  - `Airline`: Airline name (IndiGo, Air India, Jet Airways, SpiceJet, etc.).
  - `Date_of_Journey`: Date in DD/MM/YYYY format.
  - `Source`: Starting airport city.
  - `Destination`: Arrival airport city.
  - `Route`: Flight trajectory and waypoints.
  - `Dep_Time`: Departure timestamp.
  - `Arrival_Time`: Arrival timestamp.
  - `Duration`: Flight time in hours and minutes.
  - `Total_Stops`: Categorical stop description (`non-stop`, `1 stop`, `2 stops`, etc.).
  - `Additional_Info`: Service tier or baggage specifications.
  - `Price`: Target fare in Indian Rupees (₹).

---

## 2. Feature Engineering Pipeline
Inputs undergo strict transformation through a `scikit-learn` `ColumnTransformer` saved at `source_code/models/airfare_preprocessor.joblib`:
1. **Numerical Features (StandardScaler)**:
   - `duration_mins`: Total flight duration normalized.
   - `journey_day`, `journey_month`: Extracted from departure calendar.
   - `dep_hour`, `dep_min`: Departure time breakdown.
   - `arr_hour`, `arr_min`: Arrival time breakdown.
   - `total_stops`: Discrete numerical count of stopovers (0, 1, 2, 3, 4).
2. **Categorical Features (OneHotEncoder, `handle_unknown='ignore'`)**:
   - `Airline` (8 classes)
   - `Source` (5 classes)
   - `Destination` (6 classes)
   - `Additional_Info` (5 classes)
3. **Output Dimension**: Feature space $\mathbf{x} \in \mathbb{R}^{31}$.

---

## 3. Deep Neural Network Architecture (PyTorch BiLSTM)
- **File**: `source_code/models/airfare_lstm_model.pth` (576 KB)
- **Model Definition**:
```python
class BiLSTMAirfarePredictor(nn.Module):
    def __init__(self, input_dim=31, hidden_dim=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        # x shape: (batch_size, seq_len=1, input_dim=31)
        lstm_out, _ = self.lstm(x)
        out = lstm_out[:, -1, :]  # Take final hidden state
        return self.fc(out)
```
- **Training Hyperparameters**:
  - Optimizer: AdamW ($\text{lr} = 0.001$, weight decay $= 10^{-4}$)
  - Loss Function: Smooth L1 Loss (Huber Loss, $\beta = 1.0$)
  - Batch Size: 64
  - Epochs: 40 with Early Stopping ($\text{patience} = 7$)
  - Train/Test Split: 80% / 20% stratified random split ($N_{\text{train}} = 8,546$, $N_{\text{test}} = 2,137$)

---

## 4. Benchmark Random Forest Regressor
- **File**: `source_code/models/airfare_rf_model.joblib` (29 MB)
- **Configuration**:
  - `n_estimators`: 100
  - `max_depth`: 15
  - `min_samples_split`: 4
  - `random_state`: 42

---

## 5. Quantitative Evaluation Metrics
Metrics evaluated strictly on held-out test split ($N = 2,137$):

| Metric | PyTorch BiLSTM | Random Forest (Benchmark) |
|---|---|---|
| **$R^2$ Score (Coefficient of Determination)** | **0.7566** | 0.8321 |
| **Mean Absolute Error (MAE)** | **₹1,362.47** | ₹1,136.58 |
| **Root Mean Squared Error (RMSE)** | **₹2,275.89** | ₹1,890.12 |
| **Mean Absolute Percentage Error (MAPE)** | **12.4%** | 10.1% |
| **Inference Latency (Single Record)** | **~14.5 ms** | ~8.2 ms |
