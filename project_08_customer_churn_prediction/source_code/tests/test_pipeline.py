import os
import sys
import unittest
import numpy as np
import pandas as pd
import pickle

CHURN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Customer-Survival-Analysis-and-Churn-Prediction-master'))
if CHURN_DIR not in sys.path:
    sys.path.insert(0, CHURN_DIR)

from app import model, survmodel, explainer, _CustomUnpickler
from database import init_db, get_db, save_prediction, get_recent_predictions, get_all_predictions, get_prediction_stats
from seed_db import seed_database_if_empty

class TestCustomerChurnPipeline(unittest.TestCase):
    def test_random_forest_model_structure(self):
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, 'predict_proba'))
        self.assertEqual(len(model.estimators_), 1000)

    def test_cox_survival_model_structure(self):
        self.assertIsNotNone(survmodel)
        self.assertTrue(hasattr(survmodel, 'hazards_'))
        self.assertTrue(hasattr(survmodel, 'baseline_cumulative_hazard_'))
        self.assertTrue(hasattr(survmodel, 'predict_survival_function'))
        self.assertEqual(len(survmodel.hazards_), 22)

    def test_shap_explainer_structure(self):
        self.assertIsNotNone(explainer)
        self.assertTrue(hasattr(explainer, 'shap_values'))

    def test_single_prediction_probability_bounds(self):
        # 23-dimensional feature vector for Random Forest
        sample_features = np.zeros((1, 23))
        sample_features[0, 4] = 12   # tenure = 12
        sample_features[0, 14] = 65.0  # monthly = 65
        sample_features[0, 15] = 780.0  # total = 780

        prob = model.predict_proba(sample_features)[0]
        self.assertEqual(len(prob), 2)
        self.assertAlmostEqual(np.sum(prob), 1.0, places=4)
        self.assertGreaterEqual(prob[1], 0.0)
        self.assertLessEqual(prob[1], 1.0)

    def test_survival_function_monotonicity(self):
        # Survival model input: 22 features (excluding tenure)
        feats = np.zeros((1, 22))
        feats[0, 13] = 70.0  # MonthlyCharges = 70.0
        feats[0, 14] = 420.0 # TotalCharges = 420.0

        sf = survmodel.predict_survival_function(feats)
        values = sf[0].values
        # A survival function must be non-increasing over time
        for i in range(len(values) - 1):
            self.assertGreaterEqual(values[i] + 1e-6, values[i+1], f"Survival increased at step {i}")

    def test_hazard_function_non_negative(self):
        # Survival model input: 22 features
        feats = np.zeros((1, 22))
        feats[0, 13] = 85.0
        ch = survmodel.predict_cumulative_hazard(feats)
        values = ch[0].values
        for val in values:
            self.assertGreaterEqual(val, 0.0, "Cumulative hazard must be non-negative")

    def test_shap_values_dimensionality(self):
        # SHAP TreeExplainer runs on 23-dim input
        feats = np.zeros((1, 23))
        feats[0, 4] = 10
        shap_vals = explainer.shap_values(feats)
        if isinstance(shap_vals, list):
            self.assertEqual(len(shap_vals), 2)
            self.assertEqual(shap_vals[1].shape, (1, 23))
        elif isinstance(shap_vals, np.ndarray) and shap_vals.ndim == 3:
            self.assertEqual(shap_vals.shape[1], 23)
        else:
            self.assertEqual(shap_vals.shape[1], 23)

    def test_database_persistence_crud(self):
        init_db()
        test_record = {
            'customer_id': 'TEST-UNIT-999',
            'prediction_date': '2026-10-19 14:00:00',
            'gender': 'Male',
            'senior_citizen': 0,
            'partner': 1,
            'dependents': 0,
            'tenure': 24,
            'phone_service': 1,
            'multiple_lines': 0,
            'internet_service': 'DSL',
            'online_security': 1,
            'online_backup': 0,
            'device_protection': 1,
            'tech_support': 1,
            'streaming_tv': 0,
            'streaming_movies': 0,
            'contract': 'One year',
            'paperless_billing': 1,
            'payment_method': 'Bank transfer (automatic)',
            'monthly_charges': 60.5,
            'total_charges': 1452.0,
            'prediction_status': 'Stay',
            'churn_probability': 0.18,
            'risk_level': 'Low Risk',
            'cltv': 2900.0,
            'action_suggested': 'Upsell value-added security package'
        }
        rec_id = save_prediction(test_record)
        self.assertIsNotNone(rec_id)
        self.assertGreater(rec_id, 0)

        recent = get_recent_predictions(5)
        self.assertGreaterEqual(len(recent), 1)
        found = any(r['customer_id'] == 'TEST-UNIT-999' for r in recent)
        self.assertTrue(found)

    def test_database_seeding_idempotence(self):
        init_db()
        stats_before = get_prediction_stats()
        seed_database_if_empty(model, survmodel, sample_size=10)
        stats_after = get_prediction_stats()
        self.assertGreaterEqual(stats_after['total'], stats_before['total'])

if __name__ == '__main__':
    unittest.main()
