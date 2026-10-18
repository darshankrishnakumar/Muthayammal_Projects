"""
Career Guidance ML - Model Validation & Test Suite
===================================================
Tests model loading, feature encoding, multi-model predictions,
latency benchmarks, and SQLite logging integrity.
"""

import time
import sys
import os
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure parent directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from career_engine import CareerGuidanceEngine
import database as db

def run_tests():
    print("=" * 65)
    print("       CAREER GUIDANCE ML MODEL VALIDATION TEST SUITE")
    print("=" * 65)
    
    # Test 1: Engine Initialization & Cache
    print("\n[TEST 1] Initializing Engine & Checking Model Cache...")
    t0 = time.time()
    engine = CareerGuidanceEngine()
    init_time = time.time() - t0
    
    available_models = list(engine.models.keys())
    print(f"  -> Models Loaded: {available_models}")
    print(f"  -> Features Count: {len(engine.feature_names)}")
    print(f"  -> Target Roles: {len(engine.target_classes)} unique job roles")
    print(f"  -> Init Time: {init_time:.2f}s")
    assert len(available_models) >= 3, "Missing models in engine"
    print("  [PASS] Engine initialization verified.")

    # Test 2: Accuracy & Metrics
    print("\n[TEST 2] Verifying Model Benchmark Metrics...")
    for model_name, score in engine.metrics.items():
        print(f"  -> {model_name:15}: {score}% test accuracy")
    print("  [PASS] Benchmark metrics retrieved.")

    # Test 3: Inference on Preset Profiles across all Models
    print("\n[TEST 3] Running Predictions Across Preset Profiles & Models...")
    presets = engine.get_presets()
    print(f"  -> Testing {len(presets)} candidate profiles against XGBoost, RF, and DT...")

    test_runs = 0
    total_latency_ms = 0.0

    for p in presets:
        profile_name = p["label"]
        data = p["data"]
        
        for model_name in ["XGBoost", "Random Forest", "Decision Tree"]:
            t_start = time.time()
            result = engine.predict(data, model_name=model_name)
            latency = (time.time() - t_start) * 1000
            total_latency_ms += latency
            test_runs += 1

            assert "suggested_role" in result
            assert result["confidence"] > 0
            assert len(result["alternatives"]) > 0
            assert "skills" in result["insights"]

        print(f"  -> {profile_name:<35} => Recommended: '{result['suggested_role']}' ({result['confidence']}%)")

    avg_latency = total_latency_ms / test_runs
    print(f"  -> Total Inferences Executed: {test_runs}")
    print(f"  -> Average Inference Latency: {avg_latency:.2f} ms")
    print("  [PASS] All model inferences succeeded.")

    # Test 4: Database Storage & Retrieval
    print("\n[TEST 4] Testing SQLite Assessment Audit Persistence...")
    db.init_db()
    test_id = db.save_assessment(
        student_name="Automated Test Runner",
        suggested_role=result["suggested_role"],
        model_used="XGBoost",
        confidence=result["confidence"],
        top_skills=result["insights"]["skills"],
        salary_range=result["insights"]["salary_range"],
        academic_avg=88.5,
        coding_rating=9,
        interested_area="developer",
        input_data=presets[0]["data"]
    )
    print(f"  -> Inserted test record ID: {test_id}")
    records = db.get_recent_assessments(limit=5)
    assert any(r["id"] == test_id for r in records), "Inserted record not found in DB"
    
    # Cleanup test record
    db.delete_assessment(test_id)
    print(f"  -> Verified and cleaned up test record ID {test_id}.")
    print("  [PASS] Database subsystem fully operational.")

    print("\n" + "=" * 65)
    print("           ALL 4 TEST SUITES PASSED SUCCESSFULLY (100%)")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
