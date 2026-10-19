import os
import sys
import unittest
import json

# Ensure project backend is in Python path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
from nids_model import get_nids_engine
from app import app

class TestNetworkIntrusionSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.seed_database(force=True)
        cls.engine = get_nids_engine()
        cls.client = app.test_client()

    # 1. Health & Core Configuration
    def test_01_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['port'], 5026)
        self.assertIn('Dual-Engine Deep Learning', data['architecture'])
        self.assertIn('network_nids.db', data['database_backend'])
        self.assertIn('NSL-KDD', data['dataset_benchmark'])

    # 2. Model Metadata
    def test_02_model_metadata(self):
        res = self.client.get('/api/model/metadata')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data['features']), 12)
        self.assertEqual(len(data['classes']), 7)
        self.assertGreaterEqual(data['metrics']['test_accuracy'], 0.98)
        self.assertIn('anomaly_reconstruction_threshold', data)

    # 3. Model Inference: Normal Benign Flow
    def test_03_inference_normal_flow(self):
        flow = {
            'duration': 1.5, 'src_bytes': 850, 'dst_bytes': 6400,
            'count': 3, 'srv_count': 3, 'serror_rate': 0.0, 'rerror_rate': 0.0,
            'same_srv_rate': 1.0, 'diff_srv_rate': 0.0, 'dst_host_count': 100,
            'dst_host_srv_count': 95, 'dst_host_same_src_port_rate': 0.02
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'Normal')
        self.assertFalse(res['is_attack'])
        self.assertEqual(res['firewall_action'], 'ACCEPT / ROUTE')
        self.assertLess(res['reconstruction_error'], res['threshold'] * 2.0)

    # 4. Model Inference: DoS SYN Flood
    def test_04_inference_syn_flood(self):
        flow = {
            'duration': 0.001, 'src_bytes': 64, 'dst_bytes': 0,
            'count': 450, 'srv_count': 450, 'serror_rate': 1.0, 'rerror_rate': 0.0,
            'same_srv_rate': 1.0, 'diff_srv_rate': 0.0, 'dst_host_count': 255,
            'dst_host_srv_count': 255, 'dst_host_same_src_port_rate': 0.98
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'DoS_SYN_Flood')
        self.assertTrue(res['is_attack'])
        self.assertEqual(res['severity'], 'CRITICAL')
        self.assertEqual(res['firewall_action'], 'BLOCK / DROP')

    # 5. Model Inference: Port Scan Probe
    def test_05_inference_port_scan(self):
        flow = {
            'duration': 0.05, 'src_bytes': 48, 'dst_bytes': 0,
            'count': 180, 'srv_count': 2, 'serror_rate': 0.1, 'rerror_rate': 0.95,
            'same_srv_rate': 0.02, 'diff_srv_rate': 0.98, 'dst_host_count': 255,
            'dst_host_srv_count': 2, 'dst_host_same_src_port_rate': 0.0
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'Probe_PortScan')
        self.assertTrue(res['is_attack'])
        self.assertEqual(res['category'], 'Reconnaissance')

    # 6. Model Inference: SSH Brute Force
    def test_06_inference_ssh_brute_force(self):
        flow = {
            'duration': 1.2, 'src_bytes': 540, 'dst_bytes': 420,
            'count': 65, 'srv_count': 65, 'serror_rate': 0.0, 'rerror_rate': 0.55,
            'same_srv_rate': 1.0, 'diff_srv_rate': 0.0, 'dst_host_count': 40,
            'dst_host_srv_count': 40, 'dst_host_same_src_port_rate': 0.5
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'R2L_SSH_BruteForce')
        self.assertTrue(res['is_attack'])
        self.assertEqual(res['severity'], 'CRITICAL')

    # 7. Model Inference: Mirai Botnet C2
    def test_07_inference_mirai_botnet(self):
        flow = {
            'duration': 35.0, 'src_bytes': 128, 'dst_bytes': 128,
            'count': 2, 'srv_count': 1, 'serror_rate': 0.0, 'rerror_rate': 0.0,
            'same_srv_rate': 0.5, 'diff_srv_rate': 0.5, 'dst_host_count': 5,
            'dst_host_srv_count': 1, 'dst_host_same_src_port_rate': 1.0
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'Botnet_Mirai_C2')
        self.assertTrue(res['is_attack'])

    # 8. Model Inference: U2R Buffer Overflow
    def test_08_inference_buffer_overflow(self):
        flow = {
            'duration': 8.5, 'src_bytes': 4500, 'dst_bytes': 3200,
            'count': 3, 'srv_count': 1, 'serror_rate': 0.0, 'rerror_rate': 0.0,
            'same_srv_rate': 1.0, 'diff_srv_rate': 0.0, 'dst_host_count': 12,
            'dst_host_srv_count': 2, 'dst_host_same_src_port_rate': 0.05
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'U2R_BufferOverflow')
        self.assertTrue(res['is_attack'])

    # 9. Model Inference: Zero-Day Anomaly Detection
    def test_09_inference_zero_day_anomaly(self):
        flow = {
            'duration': 0.15, 'src_bytes': 28500, 'dst_bytes': 80,
            'count': 15, 'srv_count': 1, 'serror_rate': 0.45, 'rerror_rate': 0.45,
            'same_srv_rate': 0.15, 'diff_srv_rate': 0.85, 'dst_host_count': 25,
            'dst_host_srv_count': 1, 'dst_host_same_src_port_rate': 0.2
        }
        res = self.engine.evaluate(flow)
        self.assertEqual(res['attack_type'], 'ZeroDay_Anomaly')
        self.assertTrue(res['is_attack'])
        self.assertTrue(res['threshold_exceeded'])
        self.assertGreater(res['reconstruction_error'], res['threshold'])

    # 10. Database Connection & Schema Verification
    def test_10_database_schema(self):
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r['name'] for r in cur.fetchall()]
        conn.close()
        for expected in ['network_flows', 'quarantine_ledger', 'firewall_rules', 'audit_log']:
            self.assertIn(expected, tables)

    # 11. Database Transactional Flow Insertion
    def test_11_insert_flow(self):
        flow_record = {
            'src_ip': '192.168.1.188', 'dst_ip': '10.0.0.5', 'protocol': 'TCP',
            'service': 'HTTP', 'flag': 'SF', 'duration': 1.1, 'src_bytes': 450,
            'dst_bytes': 2300, 'count': 2, 'srv_count': 2, 'serror_rate': 0.0,
            'rerror_rate': 0.0, 'same_srv_rate': 1.0, 'attack_name': 'Normal',
            'attack_type': 'Normal', 'category': 'Benign', 'severity': 'SAFE',
            'confidence': 99.4, 'is_attack': 0, 'firewall_action': 'ALLOW',
            'flow_summary': 'TCP HTTP [SF] • 450b in / 2300b out'
        }
        flow_id = database.insert_flow(flow_record)
        self.assertIsInstance(flow_id, int)
        self.assertGreater(flow_id, 0)

    # 12. Retrieve Recent Flows
    def test_12_get_recent_flows(self):
        flows = database.get_recent_flows(limit=10)
        self.assertIsInstance(flows, list)
        self.assertGreaterEqual(len(flows), 1)
        self.assertIn('src_ip', flows[0])
        self.assertIn('firewall_action', flows[0])

    # 13. Dashboard Stats Rollup
    def test_13_dashboard_stats(self):
        stats = database.get_dashboard_stats()
        self.assertIn('total_flows_inspected', stats)
        self.assertIn('attacks_intercepted', stats)
        self.assertIn('threat_ratio_percent', stats)
        self.assertIn('active_quarantine_count', stats)
        self.assertGreaterEqual(stats['total_flows_inspected'], 1)

    # 14. API Stats Endpoint
    def test_14_api_stats_endpoint(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('system_throughput_pps', data)
        self.assertIn('bandwidth_mbps', data)
        self.assertIn('category_breakdown', data)

    # 15. Real-time Stream Simulation Next Flow
    def test_15_stream_next_flow(self):
        res = self.client.get('/api/stream/next')
        self.assertEqual(res.status_code, 200)
        flow = res.get_json()
        self.assertIn('id', flow)
        self.assertIn('src_ip', flow)
        self.assertIn('confidence', flow)
        self.assertIn('reconstruction_error', flow)
        self.assertIn('firewall_action', flow)

    # 16. Attack Simulation: SYN Flood
    def test_16_simulate_syn_flood(self):
        res = self.client.post('/api/simulate/attack', json={'attack_type': 'SYN_Flood'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'DoS_SYN_Flood')
        self.assertTrue(data['is_attack'])
        self.assertEqual(data['severity'], 'CRITICAL')

    # 17. Attack Simulation: Port Scan
    def test_17_simulate_port_scan(self):
        res = self.client.post('/api/simulate/attack', json={'attack_type': 'Port_Scan'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'Probe_PortScan')
        self.assertTrue(data['is_attack'])

    # 18. Attack Simulation: SSH Brute Force
    def test_18_simulate_ssh_brute_force(self):
        res = self.client.post('/api/simulate/attack', json={'attack_type': 'SSH_BruteForce'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'R2L_SSH_BruteForce')
        self.assertTrue(data['is_attack'])

    # 19. Attack Simulation: Mirai Botnet
    def test_19_simulate_mirai_botnet(self):
        res = self.client.post('/api/simulate/attack', json={'attack_type': 'Mirai_Botnet'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'Botnet_Mirai_C2')
        self.assertTrue(data['is_attack'])

    # 20. Attack Simulation: Zero Day
    def test_20_simulate_zero_day(self):
        res = self.client.post('/api/simulate/attack', json={'attack_type': 'Zero_Day'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'ZeroDay_Anomaly')
        self.assertTrue(data['is_attack'])
        self.assertTrue(data['threshold_exceeded'])

    # 21. Custom Flow Analysis Endpoint
    def test_21_custom_flow_analysis(self):
        custom_flow = {
            'src_ip': '10.10.10.50',
            'dst_ip': '10.0.0.5',
            'protocol': 'TCP',
            'service': 'HTTPS',
            'flag': 'SF',
            'duration': 2.4,
            'src_bytes': 1500,
            'dst_bytes': 9800,
            'count': 3,
            'srv_count': 3,
            'serror_rate': 0.0,
            'rerror_rate': 0.0,
            'same_srv_rate': 1.0,
            'diff_srv_rate': 0.0,
            'dst_host_count': 60,
            'dst_host_srv_count': 55,
            'dst_host_same_src_port_rate': 0.03
        }
        res = self.client.post('/api/analyze/flow', json=custom_flow)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['attack_type'], 'Normal')
        self.assertFalse(data['is_attack'])

    # 22. Custom Flow Analysis Invalid Payload
    def test_22_custom_flow_empty_payload(self):
        res = self.client.post('/api/analyze/flow', json={})
        self.assertEqual(res.status_code, 400)

    # 23. Add IP Quarantine
    def test_23_add_quarantine(self):
        test_ip = '198.51.100.77'
        res = self.client.post('/api/quarantine', json={'ip': test_ip, 'reason': 'Test Intrusion Ban'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'QUARANTINED')

    # 24. Get Quarantined IPs
    def test_24_get_quarantined_ips(self):
        res = self.client.get('/api/quarantine')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        ips = [item['ip'] for item in data]
        self.assertIn('198.51.100.77', ips)

    # 25. Unblock IP Quarantine
    def test_25_unquarantine_ip(self):
        test_ip = '198.51.100.77'
        res = self.client.delete('/api/quarantine', json={'ip': test_ip})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'UNBLOCKED')

    # 26. Unblock Non-Existent IP
    def test_26_unquarantine_missing_ip(self):
        res = self.client.delete('/api/quarantine', json={'ip': '203.0.113.999'})
        self.assertEqual(res.status_code, 404)

    # 27. Firewall Rules Generation
    def test_27_firewall_rules(self):
        res = self.client.get('/api/firewall/rules')
        self.assertEqual(res.status_code, 200)
        rules = res.get_json()
        self.assertIn('blocked_ips_count', rules)
        self.assertIn('iptables_script', rules)
        self.assertIn('ufw_script', rules)
        self.assertIn('aws_nacl_config', rules)

    # 28. Traffic Log Retrieval
    def test_28_traffic_log(self):
        res = self.client.get('/api/traffic/log?limit=5')
        self.assertEqual(res.status_code, 200)
        flows = res.get_json()
        self.assertLessEqual(len(flows), 5)

    # 29. Edge Case: Extreme Low Boundary Values
    def test_29_edge_case_zero_flow(self):
        flow = {
            'duration': 0.0, 'src_bytes': 0, 'dst_bytes': 0,
            'count': 0, 'srv_count': 0, 'serror_rate': 0.0, 'rerror_rate': 0.0,
            'same_srv_rate': 0.0, 'diff_srv_rate': 0.0, 'dst_host_count': 0,
            'dst_host_srv_count': 0, 'dst_host_same_src_port_rate': 0.0
        }
        res = self.engine.evaluate(flow)
        self.assertIn('attack_type', res)
        self.assertIsInstance(res['confidence'], float)

    # 30. Edge Case: Extreme High Burst Values
    def test_30_edge_case_massive_burst(self):
        flow = {
            'duration': 999.0, 'src_bytes': 10000000, 'dst_bytes': 50000000,
            'count': 10000, 'srv_count': 10000, 'serror_rate': 1.0, 'rerror_rate': 1.0,
            'same_srv_rate': 1.0, 'diff_srv_rate': 1.0, 'dst_host_count': 1000,
            'dst_host_srv_count': 1000, 'dst_host_same_src_port_rate': 1.0
        }
        res = self.engine.evaluate(flow)
        self.assertTrue(res['is_attack'])
        self.assertEqual(res['severity'], 'CRITICAL')

    # 31. Latent Bottleneck Vector Shape
    def test_31_latent_representation(self):
        flow = {'duration': 1.0, 'src_bytes': 500, 'dst_bytes': 1000}
        res = self.engine.evaluate(flow)
        self.assertEqual(len(res['latent_representation']), 4)

    # 32. Static Frontend Serving
    def test_32_serve_index(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI Network Intrusion Detection System', res.data)

if __name__ == '__main__':
    unittest.main()
