import os
import sys
import unittest
import json
import base64
import io
import numpy as np
import cv2
from PIL import Image

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app, decode_image, analyze_image_forensics, run_vision_inference, WEAPON_CLASSES
import database

class TestWeaponDetectionSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        database.init_db()

    def _generate_test_image_b64(self, width=320, height=240, color=(128, 128, 128)):
        img = Image.new('RGB', (width, height), color=color)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    # ─────────────────────────────────────────────────────────────
    # 1. Computer Vision & Preprocessing Tests
    # ─────────────────────────────────────────────────────────────
    def test_01_decode_image_valid(self):
        b64 = self._generate_test_image_b64(300, 200)
        cv_img, pil_img = decode_image(b64)
        self.assertEqual(cv_img.shape, (200, 300, 3))
        self.assertEqual(pil_img.size, (300, 200))

    def test_02_decode_image_with_data_prefix(self):
        b64 = "data:image/jpeg;base64," + self._generate_test_image_b64(100, 100)
        cv_img, pil_img = decode_image(b64)
        self.assertEqual(cv_img.shape, (100, 100, 3))

    def test_03_analyze_image_forensics(self):
        img_np = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(img_np, (100, 100), 40, (255, 255, 255), -1)
        forensics = analyze_image_forensics(img_np)
        self.assertIn('resolution', forensics)
        self.assertIn('sharpness', forensics)
        self.assertIn('brightness', forensics)
        self.assertIn('contrast', forensics)
        self.assertIn('edge_density_pct', forensics)
        self.assertGreater(forensics['sharpness'], 0)

    def test_04_run_vision_inference_output_format(self):
        img_np = np.zeros((300, 300, 3), dtype=np.uint8)
        # Draw simulated high-contrast shape
        cv2.rectangle(img_np, (50, 50), (200, 100), (255, 255, 255), 2)
        detections, latency_ms = run_vision_inference(img_np, conf_threshold=0.3)
        self.assertIsInstance(detections, list)
        self.assertIsInstance(latency_ms, float)
        self.assertGreater(latency_ms, 0)

    def test_05_weapon_classes_taxonomy(self):
        self.assertIn('handgun', WEAPON_CLASSES)
        self.assertIn('knife', WEAPON_CLASSES)
        self.assertIn('assault_rifle', WEAPON_CLASSES)
        self.assertIn('explosive', WEAPON_CLASSES)
        for w_cls, meta in WEAPON_CLASSES.items():
            self.assertIn('category', meta)
            self.assertIn('threat', meta)
            self.assertIn('color', meta)

    # ─────────────────────────────────────────────────────────────
    # 2. SQLite Database Layer Tests
    # ─────────────────────────────────────────────────────────────
    def test_06_database_connection(self):
        conn = database.get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_07_database_get_cctv_cameras(self):
        cams = database.get_cctv_cameras()
        self.assertGreaterEqual(len(cams), 4)
        cam_ids = [c['id'] for c in cams]
        self.assertIn('CAM-01', cam_ids)
        self.assertIn('CAM-02', cam_ids)

    def test_08_database_get_threat_definitions(self):
        threats = database.get_threat_definitions()
        self.assertGreaterEqual(len(threats), 5)
        classes = [t['weapon_class'] for t in threats]
        self.assertIn('handgun', classes)
        self.assertIn('knife', classes)

    def test_09_database_add_and_retrieve_incident(self):
        test_inc = {
            'id': 'INC-UNIT-TEST-001',
            'timestamp': '2026-10-19T12:00:00Z',
            'camera_id': 'CAM-01',
            'alert_level': 'HIGH',
            'weapon_detected': True,
            'detections': [{'class': 'knife', 'confidence': 0.91, 'severity': 'HIGH'}],
            'status': 'ACTIVE_ALERT',
            'notes': 'Unit test incident insertion',
            'image_metrics': {'sharpness': 120.5}
        }
        database.add_incident(test_inc)
        all_incidents = database.get_all_incidents()
        ids = [i['id'] for i in all_incidents]
        self.assertIn('INC-UNIT-TEST-001', ids)

    def test_10_database_update_incident_status(self):
        database.update_incident_status('INC-UNIT-TEST-001', 'RESOLVED', 'Issue resolved by security')
        all_incidents = database.get_all_incidents()
        target = next((i for i in all_incidents if i['id'] == 'INC-UNIT-TEST-001'), None)
        self.assertIsNotNone(target)
        self.assertEqual(target['status'], 'RESOLVED')
        self.assertEqual(target['notes'], 'Issue resolved by security')

    def test_11_database_log_audit_and_retrieve(self):
        database.log_audit('TEST_AUDIT_ACTION', 'Unit test audit event logging')
        logs = database.get_audit_logs(limit=10)
        self.assertGreaterEqual(len(logs), 1)
        actions = [l['action'] for l in logs]
        self.assertIn('TEST_AUDIT_ACTION', actions)

    # ─────────────────────────────────────────────────────────────
    # 3. REST API Endpoint Tests
    # ─────────────────────────────────────────────────────────────
    def test_12_api_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'HEALTHY')
        self.assertIn('yolo_loaded', data)
        self.assertIn('device', data)
        self.assertIn('cameras_online', data)

    def test_13_api_cctv_cameras_endpoint(self):
        res = self.client.get('/api/cctv/cameras')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 4)

    def test_14_api_threats_endpoint(self):
        res = self.client.get('/api/threats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 5)

    def test_15_api_audit_endpoint(self):
        res = self.client.get('/api/audit?limit=20')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_16_api_samples_catalog(self):
        res = self.client.get('/api/samples')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 5)

    def test_17_api_samples_test_handgun(self):
        res = self.client.post('/api/samples/test/SMP-01')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('incident_id', data)
        self.assertIn('alert_level', data)
        self.assertIn('sample_meta', data)

    def test_18_api_samples_test_knife(self):
        res = self.client.post('/api/samples/test/SMP-02')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('incident_id', data)

    def test_19_api_samples_test_rifle(self):
        res = self.client.post('/api/samples/test/SMP-03')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('incident_id', data)

    def test_20_api_samples_test_explosive(self):
        res = self.client.post('/api/samples/test/SMP-04')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('incident_id', data)

    def test_21_api_samples_test_civilian_safe(self):
        res = self.client.post('/api/samples/test/SMP-05')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('incident_id', data)

    def test_22_api_samples_test_invalid_sample_id(self):
        res = self.client.post('/api/samples/test/SMP-INVALID-99')
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertIn('error', data)

    def test_23_api_detect_valid_payload(self):
        b64 = self._generate_test_image_b64(250, 250)
        res = self.client.post('/api/detect', json={
            'image': b64,
            'camera_id': 'CAM-01',
            'confidence_threshold': 0.4
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('detections', data)
        self.assertIn('forensics', data)
        self.assertIn('incident_id', data)

    def test_24_api_detect_missing_image(self):
        res = self.client.post('/api/detect', json={'camera_id': 'CAM-01'})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('error', data)

    def test_25_api_detect_invalid_image_encoding(self):
        res = self.client.post('/api/detect', json={'image': 'not_valid_base64_data'})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('error', data)

    def test_26_api_detections_history(self):
        res = self.client.get('/api/detections/history?limit=10')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 10)

    def test_27_api_incidents_all_from_database(self):
        res = self.client.get('/api/incidents')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 5)

    def test_28_api_incident_status_update(self):
        res = self.client.get('/api/incidents')
        incidents = res.get_json()
        self.assertGreater(len(incidents), 0)
        target_id = incidents[0]['id']

        patch_res = self.client.patch(f'/api/incidents/{target_id}/status', json={
            'status': 'RESOLVED',
            'notes': 'Verified resolved via API test'
        })
        self.assertEqual(patch_res.status_code, 200)
        self.assertTrue(patch_res.get_json()['success'])

    def test_29_api_stats_endpoint(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_scans', data)
        self.assertIn('threats_detected', data)
        self.assertIn('clear_scans', data)
        self.assertIn('class_breakdown', data)
        self.assertIn('severity_breakdown', data)
        self.assertIn('hourly_activity', data)

    def test_30_api_model_metrics_and_benchmarks(self):
        res = self.client.get('/api/model/metrics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('model_name', data)
        self.assertIn('parameters', data)
        self.assertIn('metrics', data)
        self.assertIn('confusion_matrix', data)
        self.assertIn('architecture_breakdown', data)

        res_bench = self.client.get('/api/benchmarks')
        self.assertEqual(res_bench.status_code, 200)
        self.assertEqual(res_bench.get_json()['model_name'], data['model_name'])

    def test_31_api_emergency_lockdown_toggle(self):
        # Engage lockdown
        res1 = self.client.post('/api/emergency/lockdown', json={'active': True, 'reason': 'Drill alert'})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1['lockdown_active'])

        # Disengage lockdown
        res2 = self.client.post('/api/emergency/lockdown', json={'active': False, 'reason': 'All clear'})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertFalse(data2['lockdown_active'])

    def test_32_api_export_report_endpoint(self):
        res = self.client.get('/api/export/report')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('report_metadata', data)
        self.assertIn('incident_records', data)
        self.assertEqual(data['report_metadata']['project'], 'Project 20: YOLOv8 Weapon Detection Suite')

    def test_33_frontend_static_index(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'YOLOv8', res.data)

if __name__ == '__main__':
    unittest.main()
