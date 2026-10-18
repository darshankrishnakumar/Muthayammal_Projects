import os
import sys
import pytest
import torch
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.inference_engine import AirfareInferenceEngine, AirfareLSTMRegressor

def test_inference_engine_initialization():
    engine = AirfareInferenceEngine()
    assert engine.lstm_model is not None, "LSTM model should be loaded"
    assert engine.rf_model is not None, "Random Forest model should be loaded"
    assert engine.preprocessor is not None, "Preprocessor should be loaded"

def test_lstm_forward_pass_shape():
    engine = AirfareInferenceEngine()
    # Batch of 4 samples, 4 timesteps, input_size
    dummy_input = torch.randn(4, engine.seq_len, engine.input_size)
    with torch.no_grad():
        out = engine.lstm_model(dummy_input)
    assert out.shape == (4,), f"Expected output shape (4,), got {out.shape}"
    assert not torch.isnan(out).any(), "Model output should not contain NaNs"

def test_predict_flight_fare_valid():
    engine = AirfareInferenceEngine()
    res = engine.predict_flight_fare(
        airline="IndiGo",
        source="Banglore",
        destination="Delhi",
        journey_date="2026-11-20",
        dep_time="08:00",
        arrival_time="10:45",
        total_stops=0
    )
    assert "predicted_price_lstm" in res
    assert "predicted_price_rf" in res
    assert "recommended_fare" in res
    assert res["predicted_price_lstm"] > 1500, "Airfare should be realistically positive"
    assert res["duration_mins"] == 165, "Expected duration 165 minutes"
    assert res["pricing_tier"] in ["Budget / Economy", "Standard Fare", "Premium / High Season"]

def test_predict_flight_stops_penalty():
    engine = AirfareInferenceEngine()
    res_direct = engine.predict_flight_fare(
        airline="Air India", source="Delhi", destination="Cochin",
        journey_date="2026-12-05", dep_time="06:00", arrival_time="09:15", total_stops=0
    )
    res_stops = engine.predict_flight_fare(
        airline="Air India", source="Delhi", destination="Cochin",
        journey_date="2026-12-05", dep_time="06:00", arrival_time="14:15", total_stops=2
    )
    assert res_stops["duration_mins"] > res_direct["duration_mins"]
    assert res_stops["recommended_fare"] > 0
