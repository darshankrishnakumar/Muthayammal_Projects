import os
import json
import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datetime import datetime

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))

class AirfareLSTMRegressor(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super(AirfareLSTMRegressor, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True,
                            bidirectional=True, dropout=dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )
    def forward(self, x):
        out, (hn, cn) = self.lstm(x)
        last_out = out[:, -1, :]
        pred = self.fc(last_out)
        return pred.squeeze(-1)

class AirfareInferenceEngine:
    def __init__(self):
        self.models_dir = MODELS_DIR
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_artifacts()

    def _load_artifacts(self):
        prep_path = os.path.join(self.models_dir, 'airfare_preprocessor.joblib')
        if not os.path.exists(prep_path):
            raise FileNotFoundError(f'Preprocessor not found at {prep_path}')
        self.preprocessor = joblib.load(prep_path)

        rf_path = os.path.join(self.models_dir, 'airfare_rf_model.joblib')
        self.rf_model = joblib.load(rf_path) if os.path.exists(rf_path) else None

        lstm_path = os.path.join(self.models_dir, 'airfare_lstm_model.pth')
        checkpoint = torch.load(lstm_path, map_location=self.device, weights_only=False)
        self.input_size = checkpoint['input_size']
        self.seq_len = checkpoint['seq_len']
        self.pad_dim = checkpoint['pad_dim']
        
        self.lstm_model = AirfareLSTMRegressor(
            input_size=self.input_size,
            hidden_size=checkpoint.get('hidden_size', 64),
            num_layers=checkpoint.get('num_layers', 2),
            dropout=0.0
        ).to(self.device)
        self.lstm_model.load_state_dict(checkpoint['model_state_dict'])
        self.lstm_model.eval()

        metrics_path = os.path.join(self.models_dir, 'airfare_metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path) as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {}

    def predict_flight_fare(self, airline: str, source: str, destination: str,
                            journey_date: str, dep_time: str, arrival_time: str,
                            total_stops: int):
        # 1. Parse date and times
        dt_journey = datetime.strptime(journey_date, '%Y-%m-%d')
        j_day = dt_journey.day
        j_month = dt_journey.month
        j_weekday = dt_journey.weekday()

        dep_dt = datetime.strptime(dep_time, '%H:%M')
        arr_dt = datetime.strptime(arrival_time, '%H:%M')

        dep_hour = dep_dt.hour
        dep_min = dep_dt.minute
        arr_hour = arr_dt.hour
        arr_min = arr_dt.minute

        # Calculate duration in minutes (accounting for overnight)
        if arr_dt >= dep_dt:
            duration_mins = (arr_dt - dep_dt).seconds // 60
        else:
            duration_mins = (24 * 60 - (dep_hour * 60 + dep_min)) + (arr_hour * 60 + arr_min)
        if duration_mins == 0:
            duration_mins = 120 # Minimum sensible flight window fallback

        # 2. DataFrame for preprocessor
        input_dict = {
            'Airline': [airline],
            'Source': [source],
            'Destination': [destination],
            'Journey_day': [j_day],
            'Journey_month': [j_month],
            'Journey_weekday': [j_weekday],
            'Dep_hour': [dep_hour],
            'Dep_min': [dep_min],
            'Arrival_hour': [arr_hour],
            'Arrival_min': [arr_min],
            'Duration_mins': [duration_mins],
            'Total_Stops_Code': [total_stops]
        }
        df_in = pd.DataFrame(input_dict)
        X_proc = self.preprocessor.transform(df_in)

        # 3. Random Forest prediction
        rf_price = float(self.rf_model.predict(X_proc)[0]) if self.rf_model else 0.0

        # 4. PyTorch LSTM prediction
        pad_width = self.pad_dim - X_proc.shape[1]
        if pad_width > 0:
            X_pad = np.pad(X_proc, ((0, 0), (0, pad_width)), mode='constant')
        else:
            X_pad = X_proc
        X_seq = X_pad.reshape(-1, self.seq_len, self.input_size)
        tensor_x = torch.tensor(X_seq, dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            lstm_price = float(self.lstm_model(tensor_x).cpu().item())

        # Bounds & sanity clamp
        lstm_price = max(1800.0, lstm_price)
        rf_price = max(1800.0, rf_price)

        # Ensemble Recommendation: 60% LSTM + 40% Random Forest
        recommended_fare = 0.60 * lstm_price + 0.40 * rf_price

        # Route Insights
        is_weekend = j_weekday in [5, 6]
        pricing_tier = "Premium / High Season" if recommended_fare > 10000 else ("Standard Fare" if recommended_fare > 5000 else "Budget / Economy")

        return {
            'predicted_price_lstm': round(lstm_price, 2),
            'predicted_price_rf': round(rf_price, 2),
            'recommended_fare': round(recommended_fare, 2),
            'recommended_fare_usd': round(recommended_fare / 83.5, 2),
            'duration_formatted': f"{duration_mins // 60}h {duration_mins % 60}m",
            'duration_mins': duration_mins,
            'is_weekend': is_weekend,
            'pricing_tier': pricing_tier,
            'confidence_interval': {
                'low': round(max(1500.0, recommended_fare - 1200.0), 2),
                'high': round(recommended_fare + 1200.0, 2)
            },
            'model_evaluation_metrics': self.metrics.get('models', {})
        }

if __name__ == '__main__':
    engine = AirfareInferenceEngine()
    res = engine.predict_flight_fare(
        airline='IndiGo', source='Banglore', destination='Delhi',
        journey_date='2026-11-15', dep_time='09:00', arrival_time='11:45', total_stops=0
    )
    print('Sample Prediction:', json.dumps(res, indent=2))
