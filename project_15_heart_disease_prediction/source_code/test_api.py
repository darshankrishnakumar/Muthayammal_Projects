import json
import os
import sys

# Add directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app

data = {
    "Age": 50,
    "Sex": 1,
    "ChestPainType": 0,
    "RestingBP": 120,
    "Cholesterol": 200,
    "FastingBS": 0,
    "RestingECG": 0,
    "MaxHR": 150,
    "ExerciseAngina": 0,
    "Oldpeak": 0.0,
    "ST_Slope": 1
}

client = app.test_client()
res = client.post("/api/predict", json=data)
print("STATUS:", res.status_code)
print("RESPONSE:", res.get_json())
assert res.status_code == 200
assert "prediction" in res.get_json()
print("TEST PASSED: Model prediction endpoint successfully verified.")

