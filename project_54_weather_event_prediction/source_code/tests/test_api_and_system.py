import os
import sys
import pytest
import sqlite3
import torch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.core.config import settings
from backend.app.ml.bigru_weather_model import BiGRUWeatherNowcastingNet
from backend.app.ml.radar_precip_regressor_model import RadarPrecipitationAndExtremeWeatherRegressorNet

client = TestClient(app)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

class TestProject54CompleteSystem:
    # 1. Deliverables Verification
    def test_01_requirements_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "requirements.txt"))

    def test_02_env_example_file_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, ".env.example"))

    def test_03_walkthrough_script_exists(self):
        assert os.path.isfile(os.path.join(ROOT_DIR, "walkthrough", "walkthrough_script.md"))

    def test_04_dataset_6000_exists(self):
        csv_path = os.path.join(BASE_DIR, "data", "weather_telemetry_6000.csv")
        assert os.path.isfile(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 6001  # header + 6000 records

    def test_05_weights_bigru_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "bigru_weather_weights.pt"))
        assert os.path.isfile(os.path.join(BASE_DIR, "experiments", "phase2_model.pt"))

    def test_06_weights_radar_regressor_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "radar_precip_weights.pt"))

    def test_07_metadata_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "model_metadata.json"))

    def test_08_scalers_json_exists(self):
        assert os.path.isfile(os.path.join(BASE_DIR, "backend", "models", "weather_scalers.json"))

    # 2. Health & Gateway Verification
    def test_09_health_endpoint_status(self):
        res = client.get("/api/health/")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert data["project_id"] == "PROJECT-054"
        assert data["port"] == 5054
        assert data["database_wal_mode"] is True

    def test_10_health_models_parameters(self):
        res = client.get("/api/health/")
        data = res.json()
        assert "models" in data
        models = data["models"]
        assert models["bigru_parameters"] == 115270
        assert models["radar_regressor_parameters"] == 12615
        assert models["total_parameters"] == 127885

    # 3. Analytics & KPI Aggregations
    def test_11_analytics_summary(self):
        res = client.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_nowcast_runs"] >= 6000
        assert data["severe_weather_warnings"] > 0
        assert data["mean_cape_joules"] > 500.0
        assert data["model_performance"]["nowcasting_accuracy"] == 0.958
        assert data["model_performance"]["f1_score"] == 0.952

    def test_12_analytics_breakdown(self):
        res = client.get("/api/analytics/breakdown")
        assert res.status_code == 200
        data = res.json()
        assert "breakdown" in data
        assert len(data["breakdown"]) >= 4

    # 4. Presets & Pagination Queries
    def test_13_presets_availability(self):
        res = client.get("/api/weather/presets")
        assert res.status_code == 200
        data = res.json()
        assert len(data["presets"]) == 4

    def test_14_forecasts_pagination(self):
        res = client.get("/api/weather/forecasts?skip=0&limit=10")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 6000
        assert len(data["records"]) == 10

    def test_15_forecasts_filtering_by_station(self):
        st_name = "Coastal Maritime Radar Station 01"
        res = client.get(f"/api/weather/forecasts?station_name={st_name}&limit=5")
        assert res.status_code == 200
        data = res.json()
        for r in data["records"]:
            assert r["station_name"] == st_name

    # 5. Mesoscale Nowcasting & Extreme Weather Inference
    def test_16_nowcast_nominal_condition(self):
        payload = {
            "station_name": "Coastal Maritime Radar Station 01",
            "lead_time_hours": 3,
            "simulated_condition": "nominal"
        }
        res = client.post("/api/weather/nowcast", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "record" in data
        assert "metrics" in data
        m = data["metrics"]
        assert m["station_name"] == "Coastal Maritime Radar Station 01"
        assert m["event_class"] == "Normal Transition"
        assert m["alert_issued"] is False
        assert m["severe_weather_risk"] < 0.20

    def test_17_nowcast_severe_thunderstorm(self):
        payload = {
            "station_name": "Plains Supercell Radar Station 02",
            "lead_time_hours": 2,
            "simulated_condition": "severe_storm"
        }
        res = client.post("/api/weather/nowcast", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["station_name"] == "Plains Supercell Radar Station 02"
        assert m["alert_issued"] is True
        assert m["event_class"] == "Severe Thunderstorm"
        assert m["severe_weather_risk"] >= 0.70

    def test_18_nowcast_gale_wind_storm(self):
        payload = {
            "station_name": "Mountain Alpine Pass Radar Station 03",
            "lead_time_hours": 1,
            "simulated_condition": "gale"
        }
        res = client.post("/api/weather/nowcast", json=payload)
        assert res.status_code == 200
        data = res.json()
        m = data["metrics"]
        assert m["alert_issued"] is True
        assert m["event_class"] == "Gale Wind Storm"
        assert len(m["temporal_attention_weights"]) == 12

    # 6. Cryptographic Audit Ledger
    def test_19_audit_ledger_genesis_block(self):
        res = client.get("/api/weather/audit-logs?limit=5")
        assert res.status_code == 200
        data = res.json()
        assert data["chain_valid"] is True
        assert data["total_blocks"] >= 6001
        assert data["genesis_block_hash"] is not None

    def test_20_audit_ledger_continuous_chaining(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT block_index, previous_hash, block_hash FROM audit_ledger ORDER BY block_index ASC LIMIT 50;")
        rows = cur.fetchall()
        conn.close()

        assert rows[0][0] == 0  # Genesis
        for i in range(1, len(rows)):
            assert rows[i][1] == rows[i-1][2], f"Hash break at block {rows[i][0]}"

    def test_21_nowcast_appends_audit_block(self):
        res_before = client.get("/api/weather/audit-logs?limit=1")
        total_before = res_before.json()["total_blocks"]

        payload = {"station_name": "Urban Convective Basin Radar Station 04", "lead_time_hours": 3, "simulated_condition": "nominal"}
        res_nowcast = client.post("/api/weather/nowcast", json=payload)
        assert res_nowcast.status_code == 200

        res_after = client.get("/api/weather/audit-logs?limit=1")
        total_after = res_after.json()["total_blocks"]
        assert total_after == total_before + 1

    # 7. PyTorch Neural Engine Unit Tests
    def test_22_bigru_forward_pass_shape(self):
        model = BiGRUWeatherNowcastingNet(input_dim=7, hidden_dim=64, num_classes=5)
        model.eval()
        dummy_in = torch.randn(2, 12, 7)
        with torch.no_grad():
            logits = model(dummy_in)
        assert logits.shape == (2, 5)

    def test_23_bigru_parameter_count(self):
        model = BiGRUWeatherNowcastingNet(input_dim=7, hidden_dim=64, num_classes=5)
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 115270

    def test_24_radar_regressor_forward_pass_keys(self):
        model = RadarPrecipitationAndExtremeWeatherRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert "precipitation_rate_mmh" in out
        assert "cape_joules" in out
        assert "wind_gust_kmh" in out
        assert "severe_weather_risk" in out
        assert "severity_logits" in out

    def test_25_radar_regressor_output_ranges(self):
        model = RadarPrecipitationAndExtremeWeatherRegressorNet(input_dim=12)
        model.eval()
        dummy_in = torch.randn(4, 12)
        with torch.no_grad():
            out = model(dummy_in)
        assert torch.all(out["severe_weather_risk"] >= 0.0) and torch.all(out["severe_weather_risk"] <= 1.0)
        assert torch.all(out["precipitation_rate_mmh"] >= 0.0)
        assert torch.all(out["wind_gust_kmh"] >= 0.0)

    def test_26_radar_regressor_parameter_count(self):
        model = RadarPrecipitationAndExtremeWeatherRegressorNet(input_dim=12)
        total_p = sum(p.numel() for p in model.parameters())
        assert total_p == 12615

    # 8. Database ACID & Web Serving Tests
    def test_27_database_wal_pragma_verified(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        assert mode.lower() == "wal"

    def test_28_database_total_rows_at_least_6000(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM weather_forecast_records;")
        cnt = cur.fetchone()[0]
        conn.close()
        assert cnt >= 6000

    def test_29_database_no_null_evidence_hashes(self):
        db_path = settings.DATABASE_PATH
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM weather_forecast_records WHERE evidence_hash IS NULL OR length(evidence_hash) != 64;")
        bad_cnt = cur.fetchone()[0]
        conn.close()
        assert bad_cnt == 0

    def test_30_root_serves_html(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert "PROJECT 54" in res.text
        assert "Port: 5054" in res.text

    def test_31_root_contains_radar_container(self):
        res = client.get("/")
        assert res.status_code == 200
        assert "radar-vis-box" in res.text
        assert "audit-body" in res.text
