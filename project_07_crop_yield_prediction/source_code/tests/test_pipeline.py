"""
Automated Machine Learning Pipeline & Unit Tests for CropAI
===========================================================
Tests feature encoding, scaling, model predictions, classification,
mathematical conversions, and database operations.
"""
import pytest
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import backend_api
import database


# ============================================================
# 1. PREPROCESSING & ENCODING CONSISTENCY
# ============================================================
def test_preprocessing_pipeline_dimensions():
    """Verify ColumnTransformer and StandardScaler create 115 features."""
    bundle = backend_api.BUNDLE
    ct = bundle["ct"]
    sc = bundle["sc"]
    n_ohe = bundle["n_ohe"]

    raw = pd.DataFrame({
        "Area": ["India"],
        "Item": ["Rice, paddy"],
        "Year": [2010],
        "average_rain_fall_mm_per_year": [1083.0],
        "pesticides_tonnes": [75000.0],
        "avg_temp": [24.8],
    })[bundle["feat_cols"]]

    encoded = ct.transform(raw)
    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()
    encoded = encoded.astype(float)

    # 101 countries + 10 crops = 111 one-hot encoded categories
    assert n_ohe == 111
    # 111 one-hot + 4 numeric features = 115 total features
    assert encoded.shape[1] == 115

    # Test scaling of numeric columns
    scaled = encoded.copy()
    scaled[:, n_ohe:] = sc.transform(scaled[:, n_ohe:])
    assert np.all(np.isfinite(scaled))


def test_unseen_categorical_handling():
    """Verify OneHotEncoder with handle_unknown='ignore' handles unknown categories."""
    bundle = backend_api.BUNDLE
    ct = bundle["ct"]
    sc = bundle["sc"]
    n_ohe = bundle["n_ohe"]

    raw = pd.DataFrame({
        "Area": ["ImaginaryCountry"],
        "Item": ["UnknownCrop"],
        "Year": [2025],
        "average_rain_fall_mm_per_year": [1200.0],
        "pesticides_tonnes": [500.0],
        "avg_temp": [22.0],
    })[bundle["feat_cols"]]

    encoded = ct.transform(raw)
    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()
    encoded = encoded.astype(float)

    # Unknown categories should be encoded as zeros, without raising exceptions
    assert encoded.shape[1] == 115
    assert np.sum(encoded[:, :n_ohe]) == 0.0


# ============================================================
# 2. MACHINE LEARNING MODEL INFERENCE
# ============================================================
def test_regression_models_inference():
    """Test all cached regression models produce positive, finite predictions."""
    bundle = backend_api.BUNDLE
    sample = backend_api.encode_sample("Brazil", "Soybeans", 2012, 1782.0, 377929.0, 25.1, bundle["sc"])

    for name, entry in bundle["models"].items():
        if isinstance(entry, dict) and "poly" in entry:
            n_ohe = bundle["n_ohe"]
            ohe_part = sample[:, :n_ohe]
            poly_part = entry["poly"].transform(sample[:, n_ohe:])
            x_in = np.concatenate([ohe_part, poly_part], axis=1)
            pred = float(entry["model"].predict(x_in)[0])
        else:
            pred = float(entry.predict(sample)[0])

        assert np.isfinite(pred), f"Model {name} predicted non-finite value"
        # Yield should be positive for realistic inputs
        assert pred > 0, f"Model {name} predicted negative yield: {pred}"


def test_classification_models_inference():
    """Test all classifiers produce valid class labels."""
    bundle = backend_api.BUNDLE
    sample_bin = backend_api.encode_sample("Egypt", "Potatoes", 2011, 51.0, 19320.0, 22.1, bundle["sc_c"])
    sample_3 = backend_api.encode_sample("Egypt", "Potatoes", 2011, 51.0, 19320.0, 22.1, bundle["sc_c3"])

    for name, clf in bundle["clf_models"].items():
        cls_pred = int(clf.predict(sample_bin)[0])
        assert cls_pred in [0, 1], f"Classifier {name} produced invalid binary class: {cls_pred}"

    for name, clf in bundle["clf3_models"].items():
        cls_pred = int(clf.predict(sample_3)[0])
        assert cls_pred in [0, 1, 2], f"Classifier {name} produced invalid 3-class label: {cls_pred}"


# ============================================================
# 3. UNIT CONVERSIONS & HARVEST MATHEMATICS
# ============================================================
def test_unit_conversions():
    """Verify agricultural unit conversions: hg to tonnes and acres to hectares."""
    # 1 tonne = 10,000,000 hg
    hg_yield = 50000000.0  # 50 million hg
    expected_tonnes_per_ha = 5.0
    actual_tonnes_per_ha = hg_yield / 10000000.0
    assert actual_tonnes_per_ha == expected_tonnes_per_ha

    # 1 hectare = 2.47105 acres
    acres = 24.7105
    hectares = acres / 2.47105
    assert abs(hectares - 10.0) < 1e-5

    # Total harvest = yield in tonnes/ha * farm size in ha
    total_harvest = actual_tonnes_per_ha * hectares
    assert total_harvest == 50.0  # 5 tonnes/ha * 10 ha = 50 tonnes


# ============================================================
# 4. DATABASE LAYER UNIT TESTS
# ============================================================
def test_database_crud(tmp_path):
    """Test SQLite database initialization, insertion, querying, and deletion."""
    db_file = tmp_path / "crud_test.db"
    database.init_db(db_file)

    # Empty history test
    records = database.get_history(db_path=db_file)
    assert records == []

    # Save record
    row_id = database.save_prediction(
        task_type="regression",
        country="France",
        crop="Wheat",
        year=2012,
        rainfall=867.0,
        pesticides=2843.0,
        temperature=11.2,
        model_name="Random Forest",
        predicted_yield=72167.0,
        yield_unit="hg/ha",
        yield_tonnes_per_ha=0.0072167,
        farm_area=5.0,
        farm_area_unit="ha",
        farm_area_ha=5.0,
        total_harvest_tonnes=0.03608,
        db_path=db_file
    )
    assert row_id == 1

    # Retrieve record by ID
    item = database.get_prediction_by_id(row_id, db_path=db_file)
    assert item is not None
    assert item["country"] == "France"
    assert item["crop"] == "Wheat"
    assert item["total_harvest_tonnes"] == 0.03608

    # Export CSV
    csv_str = database.export_history_csv(db_path=db_file)
    assert "France" in csv_str
    assert "Wheat" in csv_str

    # Delete record
    success = database.delete_prediction(row_id, db_path=db_file)
    assert success is True
    assert database.get_prediction_by_id(row_id, db_path=db_file) is None

    # Clear history
    database.save_prediction(
        task_type="classification",
        country="France", crop="Wheat", year=2012,
        rainfall=867.0, pesticides=2843.0, temperature=11.2,
        model_name="GaussianNB",
        classification_label="Above Average",
        classification_class=1,
        classification_type="binary",
        db_path=db_file
    )
    database.clear_history(db_path=db_file)
    assert len(database.get_history(db_path=db_file)) == 0
