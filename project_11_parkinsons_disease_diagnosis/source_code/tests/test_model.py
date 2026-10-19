import os
import sys
import pytest
import torch
import sqlite3
import json
import numpy as np

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(SRC_DIR, "backend")
MODELS_DIR = os.path.join(SRC_DIR, "models")
DATA_DIR = os.path.join(SRC_DIR, "data")
sys.path.insert(0, BACKEND_DIR)

from main import Inception1DBlock, InceptionRNNParkinsons, run_clinical_assessment

class TestParkinsonsModelAndArchitecture:
    def test_inception_1d_block_forward(self):
        block = Inception1DBlock(in_channels=16, out_channels=32)
        x = torch.randn(4, 16, 12)
        out = block(x)
        assert out.shape == (4, 32, 12)

    def test_inception_rnn_forward_shape(self):
        model = InceptionRNNParkinsons(in_features=12, inc_channels=32, rnn_hidden=32, num_classes=2)
        x = torch.randn(4, 12)
        logits, updrs = model(x)
        assert logits.shape == (4, 2)
        assert updrs.shape == (4,)

    def test_inception_rnn_gradient_flow(self):
        model = InceptionRNNParkinsons(in_features=12, inc_channels=32, rnn_hidden=32, num_classes=2)
        x = torch.randn(2, 12)
        target = torch.tensor([0, 1], dtype=torch.long)
        criterion = torch.nn.CrossEntropyLoss()

        logits, updrs = model(x)
        loss = criterion(logits, target) + updrs.sum()
        loss.backward()

        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"Gradient missing for {name}"

    def test_run_clinical_assessment_function(self):
        feats = {
            "MDVP:Fo(Hz)": 160.0,
            "MDVP:Jitter(%)": 0.004,
            "MDVP:Shimmer": 0.02,
            "HNR": 23.5,
            "PPE": 0.15
        }
        res = run_clinical_assessment(feats, "UNIT-TEST-PT")
        assert "diagnosis" in res
        assert "confidence" in res
        assert "predicted_updrs_score" in res
        assert "clinical_recommendation" in res
        assert "biomarker_radar" in res
        assert res["latency_ms"] >= 0

    def test_model_checkpoint_integrity(self):
        ckpt_path = os.path.join(MODELS_DIR, "inception_rnn_model.pt")
        assert os.path.exists(ckpt_path)
        ckpt = torch.load(ckpt_path, map_location="cpu")
        assert "model_state_dict" in ckpt
        assert "hyperparameters" in ckpt
        assert "features" in ckpt
        assert len(ckpt["features"]) == 12

    def test_metrics_json_integrity(self):
        metrics_file = os.path.join(MODELS_DIR, "model_metrics.json")
        assert os.path.exists(metrics_file)
        with open(metrics_file, "r") as f:
            data = json.load(f)
        assert "accuracy" in data
        assert "f1_score" in data
        assert "roc_auc" in data
        assert data["accuracy"] > 0.90

    def test_sqlite_database_scans_table(self):
        db_path = os.path.join(DATA_DIR, "parkinsons_diagnosis.db")
        assert os.path.exists(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(clinical_diagnoses)")
        cols = {row[1] for row in cur.fetchall()}
        required = {"id", "timestamp", "patient_id", "diagnosis", "is_parkinsons", "confidence", "predicted_updrs", "vocal_jitter", "vocal_shimmer", "hnr", "clinical_recommendation", "latency_ms"}
        assert required.issubset(cols), f"Missing columns: {required - cols}"

        cur.execute("SELECT COUNT(*) FROM clinical_diagnoses")
        count = cur.fetchone()[0]
        assert count > 0
        conn.close()

    def test_dataset_csv_integrity(self):
        csv_path = os.path.join(DATA_DIR, "parkinsons_telemonitoring.csv")
        assert os.path.exists(csv_path)
        with open(csv_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 196 # Header + 195 rows
