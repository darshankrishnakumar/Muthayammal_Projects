import os
import sys
import json
import unittest
import numpy as np
import torch

# Ensure backend modules are importable
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
from gnn_model import gnn_engine, FinancialGCN
from app import app

class TestFinancialFraudGNNSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        cls.client = app.test_client()
        cls.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # ─── 1. GNN MODEL ARCHITECTURE & SERIALIZATION TESTS ───

    def test_gnn_model_architecture(self):
        """Verify 2-layer GCN model layer dimensions and parameters."""
        model = FinancialGCN(nfeat=8, nhid=16, nclass=2)
        self.assertEqual(model.gc1.weight.shape, (8, 16))
        self.assertEqual(model.gc2.weight.shape, (16, 2))

    def test_gnn_weights_file_exists(self):
        """Verify serialized PyTorch model weights file exists and is non-empty."""
        weights_path = os.path.join(BACKEND_DIR, "gnn_weights.pt")
        self.assertTrue(os.path.isfile(weights_path), "gnn_weights.pt must exist")
        self.assertGreater(os.path.getsize(weights_path), 500)

    def test_gnn_metadata_json_exists(self):
        """Verify GNN metadata JSON exists and contains essential schema fields."""
        meta_path = os.path.join(BACKEND_DIR, "gnn_model_metadata.json")
        self.assertTrue(os.path.isfile(meta_path), "gnn_model_metadata.json must exist")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIn("model_architecture", meta)
        self.assertIn("metrics", meta)
        self.assertIn("feature_names", meta)
        self.assertEqual(meta["input_features"], 8)
        self.assertEqual(meta["hidden_embedding_dim"], 16)

    def test_gnn_metadata_metrics_threshold(self):
        """Verify trained model achieves collegiate-grade accuracy on the test partition."""
        with open(os.path.join(BACKEND_DIR, "gnn_model_metadata.json"), "r") as f:
            meta = json.load(f)
        metrics = meta["metrics"]
        self.assertGreaterEqual(metrics["test_accuracy"], 0.90)
        self.assertGreaterEqual(metrics["test_f1"], 0.90)

    def test_feature_matrix_extraction(self):
        """Verify feature extraction transforms nodes into (N, 8) and (N, N) normalized matrices."""
        nodes = database.get_all_nodes()[:20]
        edges = database.get_all_edges()[:40]
        X_norm, A_hat, in_deg, out_deg, inflows, outflows = gnn_engine.extract_graph_features(nodes, edges)
        self.assertEqual(X_norm.shape, (20, 8))
        self.assertEqual(A_hat.shape, (20, 20))
        self.assertEqual(len(in_deg), 20)
        self.assertEqual(len(out_deg), 20)

    def test_symmetric_normalized_adjacency(self):
        """Verify normalized adjacency matrix is symmetric and has non-negative diagonal elements."""
        nodes = database.get_all_nodes()[:15]
        edges = database.get_all_edges()[:30]
        _, A_hat, _, _, _, _ = gnn_engine.extract_graph_features(nodes, edges)
        self.assertTrue(np.allclose(A_hat, A_hat.T, atol=1e-5), "Normalized adjacency matrix must be symmetric")
        self.assertTrue(np.all(np.diag(A_hat) > 0.0), "Self-loops must ensure positive diagonals")

    def test_gnn_forward_pass_predictions(self):
        """Verify forward pass generates risk scores [0, 1] and 8-dim latent embeddings."""
        nodes = database.get_all_nodes()[:25]
        edges = database.get_all_edges()[:50]
        predictions = gnn_engine.predict_graph(nodes, edges)
        self.assertEqual(len(predictions), 25)
        for p in predictions:
            self.assertIn("risk", p)
            self.assertGreaterEqual(p["risk"], 0.0)
            self.assertLessEqual(p["risk"], 1.0)
            self.assertIn("gnn_embedding", p)
            self.assertEqual(len(p["gnn_embedding"]), 8)

    def test_gnn_explain_node_signatures(self):
        """Verify GNN forensic explanation engine flags structural anomalies correctly."""
        smurf_node = {"id": "MULE-TEST", "country": "US", "risk": 0.95}
        inbound = []
        outbound = [{"id": f"TX-{i}"} for i in range(6)]
        expl = gnn_engine.explain_node(smurf_node, inbound, outbound)
        self.assertEqual(expl["classification_verdict"], "FLAGGED MONEY MULE")
        self.assertTrue(any("Smurfing" in sig for sig in expl["detected_signatures"]))

    # ─── 2. SQLITE RELATIONAL PERSISTENCE TESTS ───

    def test_sqlite_database_tables_exist(self):
        """Verify all mandatory tables exist in SQLite fraud_graph.db."""
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()
        for expected in ["accounts", "transactions", "syndicates", "frozen_sanctions", "system_audit"]:
            self.assertIn(expected, tables)

    def test_sqlite_accounts_count(self):
        """Verify accounts table contains at least 500 seeded entity records."""
        nodes = database.get_all_nodes()
        self.assertGreaterEqual(len(nodes), 500)

    def test_sqlite_transactions_count(self):
        """Verify transactions table contains at least 1,500 seeded edge records."""
        edges = database.get_all_edges()
        self.assertGreaterEqual(len(edges), 1500)

    def test_sqlite_syndicates_count(self):
        """Verify pre-seeded syndicates exist in the database."""
        syndicates = database.get_all_syndicates()
        self.assertGreaterEqual(len(syndicates), 3)

    def test_sqlite_account_freeze_and_unfreeze(self):
        """Verify transactional freeze and unfreeze mechanics."""
        test_acc = "ACC-0101"
        # Freeze
        res_freeze = database.freeze_account(test_acc, reason="Unit Test Verification", frozen_by="QA Robot")
        self.assertTrue(res_freeze)
        frozen_ids = database.get_frozen_account_ids()
        self.assertIn(test_acc, frozen_ids)
        node_after = database.get_node_by_id(test_acc)
        self.assertEqual(node_after["status"], "FROZEN")

        # Unfreeze
        res_unfreeze = database.unfreeze_account(test_acc, unfrozen_by="QA Robot")
        self.assertTrue(res_unfreeze)
        frozen_ids_after = database.get_frozen_account_ids()
        self.assertNotIn(test_acc, frozen_ids_after)
        node_unfrozen = database.get_node_by_id(test_acc)
        self.assertEqual(node_unfrozen["status"], "ACTIVE")

    def test_sqlite_audit_logging(self):
        """Verify audit trail logging for security compliance."""
        database.freeze_account("ACC-0102", reason="Audit Log Verification", frozen_by="Security Auditor")
        logs = database.get_audit_logs(limit=10)
        self.assertTrue(any(log["entity_id"] == "ACC-0102" and log["action"] == "ACCOUNT_FREEZE" for log in logs))
        database.unfreeze_account("ACC-0102", unfrozen_by="Security Auditor")

    def test_sqlite_dynamic_ring_injection(self):
        """Verify dynamic ring injection adds accounts, edges, and syndicate record."""
        ring_id = 999
        nodes = [
            {"id": f"TEST-RING-{ring_id}A", "name": "Test Shell A", "type": "Shell LLC", "balance": 50000.0, "country": "VG", "risk": 0.90},
            {"id": f"TEST-RING-{ring_id}B", "name": "Test Proxy B", "type": "Money Mule Proxy", "balance": 50000.0, "country": "CY", "risk": 0.88}
        ]
        edges = [
            {"id": f"TX-TEST-{ring_id}-1", "source": f"TEST-RING-{ring_id}A", "target": f"TEST-RING-{ring_id}B", "amount": 50000.0, "note": "Test Layering", "channel": "WIRE", "is_suspicious": 1, "pattern": "TEST_CYCLE"}
        ]
        syn_info = {
            "syndicate_id": f"SYN-TEST-{ring_id}",
            "name": "Test Syndicate Dynamic",
            "pattern": "Test Pattern",
            "threat_level": "HIGH",
            "risk_score": 0.89,
            "involved_volume_usd": 50000.0,
            "nodes": [n["id"] for n in nodes],
            "edges": [e["id"] for e in edges],
            "description": "Test dynamic injection verification"
        }
        database.insert_dynamic_ring(nodes, edges, syn_info)
        node_check = database.get_node_by_id(f"TEST-RING-{ring_id}A")
        self.assertIsNotNone(node_check)

    # ─── 3. REST API ENDPOINT TESTS ───

    def test_api_health_endpoint(self):
        """GET /api/health should return 200 with service health and model metadata."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("GCN", data["model"])
        self.assertGreater(data["nodes_tracked"], 500)
        self.assertGreater(data["edges_tracked"], 1500)

    def test_api_graph_endpoint(self):
        """GET /api/graph should return 200 with nodes array, edges array, and metadata."""
        res = self.client.get("/api/graph")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIn("metadata", data)
        self.assertGreater(len(data["nodes"]), 500)
        self.assertGreater(len(data["edges"]), 1500)

    def test_api_graph_metadata(self):
        """GET /api/graph metadata contains topological density and dimension info."""
        res = self.client.get("/api/graph")
        meta = res.get_json()["metadata"]
        self.assertIn("graph_density", meta)
        self.assertEqual(meta["gnn_layers"], 2)
        self.assertEqual(meta["embedding_dim"], 16)

    def test_api_syndicates_endpoint(self):
        """GET /api/graph/syndicates should return list of detected syndicates with risk score."""
        res = self.client.get("/api/graph/syndicates")
        self.assertEqual(res.status_code, 200)
        syndicates = res.get_json()
        self.assertIsInstance(syndicates, list)
        self.assertGreaterEqual(len(syndicates), 3)
        for s in syndicates:
            self.assertIn("syndicate_id", s)
            self.assertIn("pattern", s)
            self.assertIn("risk_score", s)

    def test_api_node_details_valid(self):
        """GET /api/node/<nid> should return 200 with forensic dossier and GNN explanation."""
        res = self.client.get("/api/node/RING-201")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("account", data)
        self.assertIn("inbound_transactions", data)
        self.assertIn("outbound_transactions", data)
        self.assertIn("gnn_message_passing", data)
        self.assertEqual(data["account"]["id"], "RING-201")

    def test_api_node_details_404(self):
        """GET /api/node/UNKNOWN_ID should return 404."""
        res = self.client.get("/api/node/UNKNOWN_ACCOUNT_XYZ")
        self.assertEqual(res.status_code, 404)

    def test_api_account_freeze_endpoint(self):
        """POST /api/account/freeze freezes account and returns success."""
        res = self.client.post("/api/account/freeze", json={"account_id": "ACC-0103"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "FROZEN")

    def test_api_account_unfreeze_endpoint(self):
        """POST /api/account/unfreeze unfreezes account and returns success."""
        res = self.client.post("/api/account/unfreeze", json={"account_id": "ACC-0103"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "UNFROZEN")

    def test_api_simulate_ring_endpoint(self):
        """POST /api/simulate/ring injects dynamic ring and returns 200 with added entities."""
        res = self.client.post("/api/simulate/ring")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("ring_id", data)
        self.assertEqual(len(data["nodes_added"]), 3)
        self.assertEqual(len(data["edges_added"]), 3)

    def test_api_export_sar_endpoint(self):
        """GET /api/export/sar returns FinCEN regulatory SAR format with suspect entities."""
        res = self.client.get("/api/export/sar")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sar_filing_id", data)
        self.assertIn("filing_institution", data)
        self.assertIn("summary", data)
        self.assertIn("primary_suspect_entities", data)
        self.assertIn("transaction_audit_trail", data)

    def test_api_gnn_layers_endpoint(self):
        """GET /api/gnn/layers returns model architecture and weight matrix specifications."""
        res = self.client.get("/api/gnn/layers")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["feature_dimension"], 8)
        self.assertEqual(data["hidden_dimension"], 16)
        self.assertEqual(data["output_classes"], 2)

    def test_api_audit_logs_endpoint(self):
        """GET /api/audit/logs returns recent system audit log events."""
        res = self.client.get("/api/audit/logs")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)

    # ─── 4. DELIVERABLES VERIFICATION TESTS ───

    def test_deliverables_verification(self):
        """Verify all required student capstone deliverables exist."""
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(self.root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

if __name__ == "__main__":
    unittest.main()
