import os
import sys
import pytest
import torch
import sqlite3
import json
import numpy as np
from PIL import Image

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(SRC_DIR, "backend")
MODELS_DIR = os.path.join(SRC_DIR, "models")
DATA_DIR = os.path.join(SRC_DIR, "data")
sys.path.insert(0, BACKEND_DIR)

from main import MesoInception4, MesoInceptionBlock, extract_forensic_features, analyze_facial_image

class TestDeepfakeModelAndVision:
    def test_meso_inception_block_forward(self):
        block = MesoInceptionBlock(in_channels=3, c1=1, c2=4, c3=4)
        x = torch.randn(2, 3, 64, 64)
        out = block(x)
        assert out.shape == (2, 9, 64, 64)

    def test_mesonet4_forward_shape(self):
        model = MesoInception4(in_channels=3, num_classes=2)
        x = torch.randn(2, 3, 256, 256)
        logits = model(x)
        assert logits.shape == (2, 2)

    def test_mesonet4_gradient_flow(self):
        model = MesoInception4(in_channels=3, num_classes=2)
        x = torch.randn(2, 3, 256, 256)
        target = torch.tensor([0, 1], dtype=torch.long)
        criterion = torch.nn.CrossEntropyLoss()

        logits = model(x)
        loss = criterion(logits, target)
        loss.backward()

        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"Gradient missing for {name}"

    def test_extract_forensic_features(self):
        img = Image.new("RGB", (256, 256), color=(200, 150, 120))
        feats = extract_forensic_features(img)

        assert "fft_high_freq_ratio" in feats
        assert "boundary_gradient_discontinuity" in feats
        assert "color_chroma_variance" in feats
        assert "laplacian_blur_metric" in feats
        assert "eye_asymmetry_index" in feats
        assert feats["tensor"].shape == (1, 3, 256, 256)

    def test_analyze_facial_image_function(self):
        img = Image.new("RGB", (256, 256), color=(180, 140, 110))
        res = analyze_facial_image(img, "unit_test_face.jpg")

        assert "prediction" in res
        assert "confidence" in res
        assert "is_deepfake" in res
        assert "moderation_verdict" in res
        assert "forensic_indicators" in res
        assert res["latency_ms"] >= 0

    def test_model_checkpoint_integrity(self):
        ckpt_path = os.path.join(MODELS_DIR, "mesonet_deepfake_model.pt")
        assert os.path.exists(ckpt_path)
        ckpt = torch.load(ckpt_path, map_location="cpu")
        assert "model_state_dict" in ckpt
        assert "hyperparameters" in ckpt
        assert ckpt["hyperparameters"]["num_classes"] == 2

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
        db_path = os.path.join(DATA_DIR, "deepfake_detector.db")
        assert os.path.exists(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(forensic_scans)")
        cols = {row[1] for row in cur.fetchall()}
        required = {"id", "timestamp", "filename", "prediction", "is_deepfake", "confidence", "fft_anomaly_score", "boundary_discontinuity", "moderation_verdict", "latency_ms"}
        assert required.issubset(cols), f"Missing columns: {required - cols}"

        cur.execute("SELECT COUNT(*) FROM forensic_scans")
        count = cur.fetchone()[0]
        assert count > 0, "No records in forensic_scans"
        conn.close()

    def test_dataset_csv_integrity(self):
        csv_path = os.path.join(DATA_DIR, "deepfake_dataset.csv")
        assert os.path.exists(csv_path)
        with open(csv_path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1001 # Header + 1000 rows
