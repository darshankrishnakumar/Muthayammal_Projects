import os
import sys
import io
import pytest
from PIL import Image

# Ensure source_code is on path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import database as db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "Egg Sex Prediction" in data["service"]
    assert data["database"]["status"] == "operational"

def test_samples_endpoint(client):
    res = client.get("/api/samples")
    assert res.status_code == 200
    data = res.get_json()
    assert "samples" in data
    assert len(data["samples"]) >= 10
    first = data["samples"][0]
    assert "id" in first
    assert "url" in first
    assert "expected_sex" in first

def test_serve_sample_image(client):
    res = client.get("/sample_image/F01_standard_female.png")
    assert res.status_code == 200
    assert "image/png" in res.content_type

def test_predict_sample_female(client):
    res = client.post("/api/predict", data={"sample_id": "F01_standard_female.png"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    res_obj = data["result"]
    assert "Female" in res_obj["prediction"]
    assert res_obj["confidence_pct"] > 50.0
    assert "morphology" in res_obj
    assert res_obj["morphology"]["shape_index"] > 74.0

def test_predict_sample_male(client):
    res = client.post("/api/predict", data={"sample_id": "M01_pointed_apex_male.png"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    res_obj = data["result"]
    assert "Male" in res_obj["prediction"]
    assert res_obj["confidence_pct"] > 50.0
    assert "morphology" in res_obj
    assert res_obj["morphology"]["shape_index"] < 74.0

def test_predict_multipart_upload(client):
    # Create test image in memory
    img = Image.new("L", (128, 128), color=255)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    res = client.post(
        "/api/predict",
        data={"file": (img_byte_arr, "test_egg.png")},
        content_type="multipart/form-data"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "result" in data
    assert "prediction" in data["result"]

def test_predict_missing_payload(client):
    res = client.post("/api/predict", data={})
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_predict_nonexistent_sample(client):
    res = client.post("/api/predict", data={"sample_id": "nonexistent_egg_999.png"})
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data

def test_evaluate_dataset(client):
    res = client.get("/api/evaluate_dataset")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["total_samples"] >= 10
    assert data["accuracy_pct"] == 100.0
    assert "confusion_matrix" in data

def test_submit_all_endpoint(client):
    res = client.post("/api/submit_all")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["accuracy_pct"] == 100.0

def test_history_endpoint(client):
    res = client.get("/api/history?limit=10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "records" in data
    assert len(data["records"]) <= 10

def test_stats_endpoint(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "stats" in data
    assert data["stats"]["total_records"] > 0
