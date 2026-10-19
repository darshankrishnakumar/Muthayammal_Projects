import os
import sys
import pytest
import numpy as np
import torch
import joblib
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import CrimeRiskDNN

@pytest.fixture
def model():
    m = CrimeRiskDNN(input_dim=11, num_classes=4)
    weights_path = os.path.join(BASE_DIR, "models", "crime_risk_dnn.pt")
    assert os.path.exists(weights_path)
    m.load_state_dict(torch.load(weights_path, map_location="cpu"))
    m.eval()
    return m

@pytest.fixture
def artifacts():
    art_path = os.path.join(BASE_DIR, "models", "crime_pipeline_artifacts.joblib")
    assert os.path.exists(art_path)
    return joblib.load(art_path)

def test_pytorch_model_architecture(model):
    assert isinstance(model, CrimeRiskDNN)
    # Check layer sequence
    layers = list(model.net.children())
    assert len(layers) == 11
    assert isinstance(layers[0], torch.nn.Linear)

    assert layers[0].in_features == 11
    assert layers[-1].out_features == 4

def test_forward_pass_dimensions(model):
    dummy_input = torch.randn(5, 11)
    with torch.no_grad():
        out = model(dummy_input)
    assert out.shape == (5, 4)
    probs = torch.softmax(out, dim=1)
    assert torch.allclose(probs.sum(dim=1), torch.ones(5), atol=1e-5)

def test_dnn_gradient_flow():
    m = CrimeRiskDNN(input_dim=11, num_classes=4)
    m.train()
    x = torch.randn(8, 11, requires_grad=True)
    target = torch.tensor([0, 1, 2, 3, 0, 1, 2, 3], dtype=torch.long)
    criterion = torch.nn.CrossEntropyLoss()
    logits = m(x)
    loss = criterion(logits, target)
    loss.backward()
    for name, param in m.named_parameters():
        assert param.grad is not None
        assert not torch.isnan(param.grad).any()

def test_artifacts_integrity(artifacts):
    assert "scaler" in artifacts
    assert "rf_crime" in artifacts
    assert "districts" in artifacts
    assert len(artifacts["districts"]) >= 8
    assert len(artifacts["risk_classes"]) == 4

def test_scaler_transform(artifacts):
    scaler = artifacts["scaler"]
    test_raw = np.array([[23, 5, 10, 1, 0, 5, 8.5, 2, 2, 41.88, -87.63]])
    scaled = scaler.transform(test_raw)
    assert scaled.shape == (1, 11)
    assert not np.isnan(scaled).any()

def test_high_threat_prediction(model, artifacts):
    scaler = artifacts["scaler"]
    le_risk = artifacts["le_risk"]
    # Late night nightclub high density
    raw = np.array([[23, 5, 10, 1, 0, 5, 9.5, 1, 1, 41.88, -87.63]])
    scaled = scaler.transform(raw)
    with torch.no_grad():
        logits = model(torch.tensor(scaled, dtype=torch.float32))
        pred_idx = torch.argmax(logits, dim=1).item()
        cat = le_risk.inverse_transform([pred_idx])[0]
    assert cat in ["CRITICAL", "HIGH"]

def test_low_threat_prediction(model, artifacts):
    scaler = artifacts["scaler"]
    le_risk = artifacts["le_risk"]
    # Daytime quiet residential low density
    raw = np.array([[11, 1, 5, 0, 3, 2, 1.5, 5, 4, 41.87, -87.69]])
    scaled = scaler.transform(raw)
    with torch.no_grad():
        logits = model(torch.tensor(scaled, dtype=torch.float32))
        pred_idx = torch.argmax(logits, dim=1).item()
        cat = le_risk.inverse_transform([pred_idx])[0]
    assert cat in ["LOW", "MODERATE"]

def test_random_forest_classification(artifacts):
    rf = artifacts["rf_crime"]
    dummy = np.zeros((2, 11))
    preds = rf.predict(dummy)
    assert len(preds) == 2

def test_dataset_csv_integrity():
    csv_path = os.path.join(BASE_DIR, "data", "urban_crime_incidents.csv")
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    assert len(df) == 5000
    assert "incident_id" in df.columns
    assert "risk_category" in df.columns
    assert "primary_type" in df.columns
