"""
Apple Health Intelligence AI - Automated Test Suite
====================================================
Comprehensive Unit and Integration Tests:
1. Dataset loading, auditing, and verification logic
2. Preprocessing & augmentation transforms
3. Model architecture and output dimensions
4. Checkpoint saving, integrity, and configuration checks
5. Fruit condition (Fresh vs Rotten) inference & routing
6. Leaf disease classification (backward compatibility)
7. Grad-CAM saliency generation and layer activation extraction
8. Uncertainty and out-of-distribution rejection
9. Corrupted/unsupported input handling
10. Flask REST API endpoints (health, samples, json predict, multipart file upload)
"""

import os
import io
import sys
import json
import base64
import unittest
from pathlib import Path

# Add project root and scripts to sys.path
root_dir = Path(__file__).resolve().parent.parent
for p in [str(root_dir), str(root_dir / "scripts")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F

from apple_cnn_engine import get_engine, CLASS_NAMES, CLASS_DISPLAY, TaskClassifier
from app import app
from scripts.prepare_datasets import verify_image, compute_file_hash, DatasetPreparer
from scripts.train_model import get_transforms


class TestDatasetIntegrity(unittest.TestCase):
    def test_verify_image_valid(self):
        img_path = root_dir / "sample_images/normal_apple_sample.jpg"
        if img_path.exists():
            is_valid, err, size = verify_image(str(img_path))
            self.assertTrue(is_valid)
            self.assertIsNotNone(size)

    def test_duplicate_detection_hash(self):
        img_path = root_dir / "sample_images/normal_apple_sample.jpg"
        if img_path.exists():
            h1 = compute_file_hash(str(img_path))
            h2 = compute_file_hash(str(img_path))
            self.assertEqual(h1, h2)
            self.assertEqual(len(h1), 32)

    def test_processed_splits_exist_and_balanced(self):
        proc_dir = root_dir / "datasets/processed/fruit_condition"
        self.assertTrue((proc_dir / "train" / "Fresh").exists())
        self.assertTrue((proc_dir / "train" / "Rotten").exists())
        self.assertTrue((proc_dir / "val" / "Fresh").exists())
        self.assertTrue((proc_dir / "val" / "Rotten").exists())
        self.assertTrue((proc_dir / "test" / "Fresh").exists())
        self.assertTrue((proc_dir / "test" / "Rotten").exists())

        train_fresh = len(list((proc_dir / "train" / "Fresh").glob("*.*")))
        train_rot = len(list((proc_dir / "train" / "Rotten").glob("*.*")))
        self.assertGreater(train_fresh, 10)
        self.assertGreater(train_rot, 10)
        # Verify balance
        self.assertEqual(train_fresh, train_rot)

    def test_manifest_and_summary_files_exist(self):
        summary_path = root_dir / "datasets/processed/fruit_condition/dataset_summary.json"
        manifest_path = root_dir / "datasets/processed/fruit_condition/manifest.json"
        self.assertTrue(summary_path.exists(), "dataset_summary.json must exist")
        self.assertTrue(manifest_path.exists(), "manifest.json must exist")
        
        with open(summary_path) as f:
            summary = json.load(f)
            self.assertEqual(summary["task_name"], "fruit_condition")
            self.assertIn("Fresh", summary["classes"])
            self.assertIn("Rotten", summary["classes"])


class TestModelArchitectureAndTransforms(unittest.TestCase):
    def test_transforms_dimensions_and_normalization(self):
        train_tf, eval_tf = get_transforms()
        test_img = Image.new("RGB", (300, 400), color=(128, 64, 32))
        tensor = eval_tf(test_img)
        self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_binary_fruit_model_output_shape(self):
        model = TaskClassifier(num_classes=2)
        dummy_input = torch.randn(2, 3, 224, 224)
        output = model(dummy_input)
        self.assertEqual(output.shape, torch.Size([2, 2]))

    def test_multiclass_leaf_model_output_shape(self):
        model = TaskClassifier(num_classes=4)
        dummy_input = torch.randn(2, 3, 224, 224)
        output = model(dummy_input)
        self.assertEqual(output.shape, torch.Size([2, 4]))


class TestModelCheckpoints(unittest.TestCase):
    def setUp(self):
        self.models_dir = root_dir / "models"

    def test_fruit_checkpoint_exists_and_loads(self):
        ckpt_path = self.models_dir / "apple_fruit_condition_v1.pth"
        self.assertTrue(ckpt_path.exists(), "Fruit condition checkpoint must exist")
        data = torch.load(str(ckpt_path), map_location="cpu")
        self.assertIn("model_state_dict", data)
        self.assertIn("classes", data)
        self.assertEqual(data["classes"], ['Fresh', 'Rotten'])

    def test_fruit_config_metadata(self):
        cfg_path = self.models_dir / "apple_fruit_condition_v1_config.json"
        self.assertTrue(cfg_path.exists())
        with open(cfg_path) as f:
            cfg = json.load(f)
            self.assertEqual(cfg["task_name"], "fruit_condition")
            self.assertEqual(cfg["classes"], ["Fresh", "Rotten"])
            self.assertEqual(cfg["input_dimensions"], [3, 224, 224])

    def test_leaf_checkpoint_exists_and_loads(self):
        ckpt_path = self.models_dir / "apple_leaf_disease_v1.pth"
        self.assertTrue(ckpt_path.exists(), "Leaf disease checkpoint must exist")
        data = torch.load(str(ckpt_path), map_location="cpu")
        self.assertIn("model_state_dict", data)
        self.assertIn("classes", data)
        self.assertEqual(data["classes"], ['Apple_Scab', 'Black_Rot', 'Cedar_Apple_Rust', 'Healthy'])


class TestInferenceAndExplainability(unittest.TestCase):
    def setUp(self):
        self.engine = get_engine()

    def test_fresh_fruit_prediction_and_routing(self):
        p = root_dir / "sample_images/normal_apple_sample.jpg"
        if p.exists():
            img = Image.open(p)
            res = self.engine.predict(img, model_type="transfer", specimen_override="apple_fruit")
            self.assertEqual(res["specimen_type"], "apple_fruit")
            self.assertEqual(res["predicted_class"], "Fresh")
            self.assertGreater(res["confidence"], 50.0)
            self.assertIn("gradcam_image", res)
            self.assertTrue(res["gradcam_image"].startswith("data:image/jpeg;base64,"))
            self.assertIn("activations", res)

    def test_rotten_fruit_prediction_and_routing(self):
        p = root_dir / "sample_images/rot_apple_sample.jpg"
        if p.exists():
            img = Image.open(p)
            res = self.engine.predict(img, model_type="transfer", specimen_override="apple_fruit")
            self.assertEqual(res["specimen_type"], "apple_fruit")
            self.assertEqual(res["predicted_class"], "Rotten")
            self.assertGreater(res["confidence"], 50.0)
            self.assertIn("gradcam_image", res)

    def test_leaf_prediction_and_routing(self):
        p = root_dir / "sample_images/scab_leaf_sample.jpg"
        if p.exists():
            img = Image.open(p)
            res = self.engine.predict(img, model_type="transfer")
            self.assertEqual(res["specimen_type"], "apple_leaf")
            self.assertIn(res["predicted_class"], ["Apple_Scab", "Black_Rot", "Cedar_Apple_Rust", "Healthy"])
            self.assertIn("decision_support", res)

    def test_uncertainty_handling_on_noise(self):
        noise_arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise_arr)
        res = self.engine.predict(noise_img, model_type="transfer")
        self.assertIn("is_uncertain", res)
        self.assertTrue(res["is_uncertain"])
        self.assertIsNotNone(res["uncertainty_reason"])


class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("models", data)
        self.assertTrue(data["models"]["fruit_condition"]["active"])
        self.assertTrue(data["models"]["leaf_disease"]["active"])

    def test_samples_endpoint(self):
        res = self.client.get('/api/samples')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["samples"]), 0)

    def test_predict_with_sample_id(self):
        res = self.client.post('/api/predict', json={'sample_id': 'rot_fruit', 'model_type': 'transfer'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("data", data)
        self.assertIn("predicted_class", data["data"])
        self.assertEqual(data["data"]["predicted_class"], "Rotten")

    def test_predict_multipart_file_upload(self):
        test_img = Image.new("RGB", (100, 100), color=(200, 50, 50))
        buf = io.BytesIO()
        test_img.save(buf, format="JPEG")
        buf.seek(0)

        data = {
            'image': (buf, 'test_apple.jpg'),
            'model_type': 'transfer',
            'specimen': 'fruit'
        }
        res = self.client.post('/api/predict', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        resp = res.get_json()
        self.assertTrue(resp["success"])
        self.assertIn("predicted_class", resp["data"])

    def test_predict_corrupted_payload(self):
        res = self.client.post('/api/predict', json={'image': 'not_a_valid_base64_string!!!!'})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_predict_missing_image(self):
        res = self.client.post('/api/predict', json={})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])

    def test_db_status_endpoint(self):
        res = self.client.get('/api/db/status')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["database"]["connected"])
        self.assertIn("total_records", data["database"])

    def test_db_history_endpoint(self):
        res = self.client.get('/api/db/history?limit=5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("records", data)
        self.assertIsInstance(data["records"], list)

    def test_predict_auto_logs_to_db(self):
        res = self.client.post('/api/predict', json={'sample_id': 'rot_fruit', 'model_type': 'transfer'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("db_record_id", data["data"])
        self.assertIsNotNone(data["data"]["db_record_id"])
        self.assertGreater(data["data"]["db_record_id"], 0)


class TestDatabaseDirect(unittest.TestCase):
    def test_database_insert_and_query(self):
        from database import save_diagnosis, get_recent_diagnoses, get_db_stats
        initial_stats = get_db_stats()
        self.assertTrue(initial_stats["connected"])
        
        rec_id = save_diagnosis(
            specimen_type="apple_leaf",
            predicted_class="Apple_Scab",
            display_name="Apple Scab",
            confidence=95.5,
            model_used="MobileNetV2",
            severity="Moderate",
            is_uncertain=False,
            source="unit_test"
        )
        self.assertGreater(rec_id, 0)
        
        records = get_recent_diagnoses(limit=5)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0]["id"], rec_id)
        self.assertEqual(records[0]["predicted_class"], "Apple_Scab")
        self.assertEqual(records[0]["specimen_type"], "apple_leaf")


if __name__ == '__main__':
    unittest.main()
