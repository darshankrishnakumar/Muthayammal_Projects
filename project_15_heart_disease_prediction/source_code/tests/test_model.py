import os
import sys
import pickle
import numpy as np
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

MODEL_PATH = os.path.join(BASE_DIR, "heart_model.pkl")

@pytest.fixture(scope="module")
def loaded_model():
    assert os.path.exists(MODEL_PATH), f"Model file not found at {MODEL_PATH}"
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

def test_model_type(loaded_model):
    from sklearn.ensemble import RandomForestClassifier
    assert isinstance(loaded_model, RandomForestClassifier)

def test_model_feature_count(loaded_model):
    if hasattr(loaded_model, "n_features_in_"):
        assert loaded_model.n_features_in_ == 11
    if hasattr(loaded_model, "feature_names_in_"):
        expected_features = [
            'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol',
            'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'
        ]
        assert list(loaded_model.feature_names_in_) == expected_features

def test_low_risk_prediction(loaded_model):
    # Typical low-risk profile: Young, normal BP, normal cholesterol, high max HR, no angina, upsloping ST
    patient = np.array([[35, 0, 1, 115, 180, 0, 0, 175, 0, 0.0, 0]])
    pred = loaded_model.predict(patient)[0]
    prob = loaded_model.predict_proba(patient)[0]
    assert int(pred) == 0
    assert prob[0] > prob[1]

def test_high_risk_prediction(loaded_model):
    # High-risk profile: Older, male, asymptomatic chest pain, high BP, high cholesterol, angina, depressed ST
    patient = np.array([[62, 1, 0, 155, 290, 1, 2, 110, 1, 3.5, 2]])
    pred = loaded_model.predict(patient)[0]
    prob = loaded_model.predict_proba(patient)[0]
    assert int(pred) == 1
    assert prob[1] > prob[0]

def test_prediction_output_shapes(loaded_model):
    batch = np.array([
        [40, 1, 0, 120, 200, 0, 0, 150, 0, 0.0, 1],
        [65, 1, 0, 160, 280, 1, 2, 100, 1, 2.8, 2]
    ])
    preds = loaded_model.predict(batch)
    probs = loaded_model.predict_proba(batch)
    assert len(preds) == 2
    assert probs.shape == (2, 2)
    assert np.allclose(probs.sum(axis=1), 1.0)

def test_decision_reproducibility(loaded_model):
    patient = np.array([[55, 1, 2, 130, 220, 0, 0, 140, 0, 1.0, 1]])
    pred1 = loaded_model.predict(patient)[0]
    pred2 = loaded_model.predict(patient)[0]
    prob1 = loaded_model.predict_proba(patient)[0]
    prob2 = loaded_model.predict_proba(patient)[0]
    assert pred1 == pred2
    assert np.allclose(prob1, prob2)

def test_risk_tier_calibration(loaded_model):
    def get_tier(prob_pct):
        if prob_pct >= 75.0:
            return "High"
        elif prob_pct >= 50.0:
            return "Elevated"
        elif prob_pct >= 25.0:
            return "Moderate"
        return "Low"

    assert get_tier(88.5) == "High"
    assert get_tier(65.0) == "Elevated"
    assert get_tier(40.0) == "Moderate"
    assert get_tier(15.0) == "Low"

def test_feature_sensitivity_exercise_angina(loaded_model):
    # Exercise-induced angina increases coronary disease probability
    patient_no_angina = np.array([[55, 1, 0, 130, 240, 0, 0, 135, 0, 1.5, 1]])
    patient_yes_angina = np.array([[55, 1, 0, 130, 240, 0, 0, 135, 1, 1.5, 1]])
    prob_no = loaded_model.predict_proba(patient_no_angina)[0][1]
    prob_yes = loaded_model.predict_proba(patient_yes_angina)[0][1]
    assert prob_yes >= prob_no
