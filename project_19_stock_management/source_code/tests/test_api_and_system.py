import os
import sys
import unittest
import json
import numpy as np

# Ensure backend directory is in path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app, db, Product, Category, Supplier, Sale, StockMovement, run_seed
from ml_engine import MLEngine, LSTMForecaster

class TestStockManagementSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()
            run_seed()
        cls.engine = MLEngine.get_instance()

    # ─── 1. ARTIFACT & ASSET INTEGRITY TESTS ───────────────────────────────────

    def test_01_requirements_exist(self):
        root_req = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'requirements.txt'))
        self.assertTrue(os.path.isfile(root_req), "requirements.txt must exist at project root")

    def test_02_presentation_exists(self):
        pres_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'presentations', 'project_presentation.pptx'))
        self.assertTrue(os.path.isfile(pres_path), "project_presentation.pptx must exist in presentations/")

    def test_03_trained_models_exist(self):
        models_dir = os.path.join(BACKEND_DIR, 'models')
        self.assertTrue(os.path.exists(os.path.join(models_dir, 'lstm_demand_forecaster.pt')), "PyTorch LSTM weights missing")
        self.assertTrue(os.path.exists(os.path.join(models_dir, 'rf_demand_regressor.joblib')), "Random Forest weights missing")
        self.assertTrue(os.path.exists(os.path.join(models_dir, 'gbm_demand_regressor.joblib')), "GBM weights missing")
        self.assertTrue(os.path.exists(os.path.join(models_dir, 'scaler.joblib')), "Feature scaler missing")
        self.assertTrue(os.path.exists(os.path.join(models_dir, 'metrics.json')), "Metrics json missing")

    def test_04_historical_dataset_exists(self):
        csv_path = os.path.join(BACKEND_DIR, 'data', 'warehouse_historical_demand.csv')
        self.assertTrue(os.path.exists(csv_path), "Historical demand CSV dataset missing")
        self.assertGreater(os.path.getsize(csv_path), 50000, "Dataset file must be >50KB")

    # ─── 2. ML & NEURAL INFERENCE ENGINE TESTS ────────────────────────────────

    def test_05_ml_engine_singleton(self):
        eng2 = MLEngine.get_instance()
        self.assertIs(self.engine, eng2, "MLEngine must be a singleton instance")

    def test_06_model_benchmarks_structure(self):
        benchmarks = self.engine.get_model_benchmarks()
        self.assertIn("pytorch_lstm", benchmarks)
        self.assertIn("random_forest", benchmarks)
        self.assertIn("gradient_boosting", benchmarks)
        self.assertIn("arima_baseline", benchmarks)
        self.assertGreater(benchmarks["pytorch_lstm"]["r2_score"], 0.85)

    def test_07_predict_multi_model_execution(self):
        dummy_feat = [3, 10, 0, 0, 1.2, 25.0, 24.0, 26.0, 22.0, 24.5, 3.2, 23.8]
        p_lstm, p_rf, p_gbm, p_ens = self.engine.predict_multi_model(dummy_feat)
        self.assertGreater(p_lstm, 0.0)
        self.assertGreater(p_rf, 0.0)
        self.assertGreater(p_gbm, 0.0)
        self.assertGreater(p_ens, 0.0)

    def test_08_forecast_7day_series(self):
        res = self.engine.forecast_7day()
        self.assertIn("forecast_series", res)
        self.assertEqual(len(res["forecast_series"]), 7)
        for s in res["forecast_series"]:
            self.assertIn("day", s)
            self.assertIn("date", s)

    def test_09_forecast_confidence_interval(self):
        res = self.engine.forecast_7day()
        for s in res["forecast_series"]:
            if s["predicted"] is not None:
                self.assertIsNotNone(s["upper_bound"])
                self.assertIsNotNone(s["lower_bound"])
                self.assertGreaterEqual(s["upper_bound"], s["predicted"])
                self.assertLessEqual(s["lower_bound"], s["predicted"])

    def test_10_inventory_optimization_rop(self):
        with app.app_context():
            p = Product.query.first()
            opt = self.engine.compute_inventory_optimization(p, current_stock=5, lead_time_days=3)
            self.assertIn("reorder_point", opt)
            self.assertIn("safety_stock", opt)
            self.assertGreater(opt["reorder_point"], 0)
            self.assertGreater(opt["safety_stock"], 0)
            self.assertEqual(opt["urgency"], "CRITICAL" if p.quantity == 0 else "HIGH" if p.quantity <= opt["reorder_point"]*0.6 else "MODERATE")

    def test_11_inventory_optimization_eoq(self):
        with app.app_context():
            p = Product.query.first()
            opt = self.engine.compute_inventory_optimization(p, current_stock=2, lead_time_days=4)
            self.assertIn("economic_order_quantity", opt)
            self.assertGreater(opt["economic_order_quantity"], 0)
            self.assertIn("suggested_reorder", opt)
            self.assertGreaterEqual(opt["suggested_reorder"], opt["economic_order_quantity"])

    def test_12_stockout_risk_bounds(self):
        with app.app_context():
            p = Product.query.first()
            opt_low = self.engine.compute_inventory_optimization(p, current_stock=0)
            opt_high = self.engine.compute_inventory_optimization(p, current_stock=500)
            self.assertGreaterEqual(opt_low["stockout_risk_percentage"], 90.0)
            self.assertLessEqual(opt_high["stockout_risk_percentage"], 10.0)

    # ─── 3. REST API ENDPOINT INTEGRATION TESTS ───────────────────────────────

    def test_13_api_health(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'running')
        self.assertIn('Enterprise Stock Management', data['service'])

    def test_14_api_dashboard(self):
        res = self.client.get('/api/dashboard')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_products', data)
        self.assertIn('total_valuation', data)
        self.assertIn('weekly_sales', data)
        self.assertGreater(data['total_products'], 0)

    def test_15_api_products_list(self):
        res = self.client.get('/api/products')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn('sku', first)
        self.assertIn('price', first)
        self.assertIn('quantity', first)

    def test_16_api_forecast_endpoint(self):
        res = self.client.get('/api/forecast')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('forecast_series', data)
        self.assertIn('reorder_alerts', data)
        self.assertIn('models_evaluated', data)
        self.assertIn('confidence_score', data)

    def test_17_api_forecast_models(self):
        res = self.client.get('/api/forecast/models')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('models', data)
        self.assertIn('active_model', data)
        self.assertIn('features', data)
        self.assertEqual(len(data['features']), 12)

    def test_18_api_forecast_product_specific(self):
        res = self.client.get('/api/forecast/product/SKU-001')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('product', data)
        self.assertIn('forecast', data)
        self.assertIn('inventory_optimization', data)
        self.assertEqual(data['product']['sku'], 'SKU-001')

    def test_19_api_forecast_nonexistent_product(self):
        res = self.client.get('/api/forecast/product/INVALID-SKU-999')
        self.assertEqual(res.status_code, 404)

    def test_20_api_hardware_scan_lookup(self):
        payload = {'code': '8901001001', 'action': 'LOOKUP', 'device_id': 'TEST-SCANNER'}
        res = self.client.post('/api/hardware/scan', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('product', data)
        self.assertEqual(data['product']['sku'], 'SKU-001')

    def test_21_api_hardware_scan_sale_checkout(self):
        with app.app_context():
            p = Product.query.filter_by(barcode='8901001001').first()
            init_qty = p.quantity

        payload = {'code': '8901001001', 'action': 'SALE', 'device_id': 'POS-TERM-01'}
        res = self.client.post('/api/hardware/scan', json=payload)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            p = Product.query.filter_by(barcode='8901001001').first()
            self.assertEqual(p.quantity, init_qty - 1)

    def test_22_api_hardware_scan_inward_restock(self):
        with app.app_context():
            p = Product.query.filter_by(barcode='8901001001').first()
            init_qty = p.quantity

        payload = {'code': '8901001001', 'action': 'INWARD', 'quantity': 15, 'device_id': 'DOCK-GATE-01'}
        res = self.client.post('/api/hardware/scan', json=payload)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            p = Product.query.filter_by(barcode='8901001001').first()
            self.assertEqual(p.quantity, init_qty + 15)

    def test_23_api_smart_scale_telemetry(self):
        with app.app_context():
            p = Product.query.filter_by(sku='SKU-001').first()
            p.quantity = 40
            db.session.commit()

        # Unit weight 0.25kg, 40 units = 10.0kg
        payload = {'sku': 'SKU-001', 'weight_kg': 10.0, 'unit_weight_kg': 0.25}
        res = self.client.post('/api/hardware/telemetry', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'MATCH')
        self.assertEqual(data['discrepancy'], 0)

    def test_24_api_reports_summary(self):
        res = self.client.get('/api/reports/summary')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_revenue', data)
        self.assertIn('total_units_sold', data)
        self.assertIn('total_inventory_valuation', data)
        self.assertIn('sales_by_category', data)

    def test_25_api_reports_export_csv(self):
        res = self.client.get('/api/reports/export?type=products')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'text/csv')
        csv_text = res.get_data(as_text=True)
        self.assertIn('SKU', csv_text)
        self.assertIn('Price', csv_text)

    def test_26_api_seed_endpoint(self):
        res = self.client.post('/api/seed')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('Seed data initialized', data['message'])

if __name__ == '__main__':
    unittest.main()
