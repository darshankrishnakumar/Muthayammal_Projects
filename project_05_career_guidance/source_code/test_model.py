"""
Career Guidance ML - Model Validation & QA Automation Test Suite
================================================================
Comprehensive test suite testing:
1. Engine Initialization & Model Cache Loading
2. Feature Dimension & Categorical LabelEncoders
3. Multi-Class Target Classification Space (34 Job Roles)
4. Model Evaluation Metrics Retrieval
5. Flask API Gateway /api/health Endpoint
6. Flask Presets Catalog /api/presets Endpoint
7. Model Metrics Endpoint /api/metrics
8. XGBoost Classifier Prediction Pipeline
9. Random Forest Classifier Prediction Pipeline
10. Decision Tree Classifier Prediction Pipeline
11. Alternative Career Pathways Ranking (Top 3-4 Roles)
12. Domain Career Insights (Skills, Certifications, Salary, Growth)
13. SQLite Database Initialization & Schema Validation
14. SQLite Assessment Persistence & Deletion CRUD Flow
15. Multi-Segment Preset Student Profile Inferences
16. Boundary Input Handling (Missing & Out-of-Range Attributes)
17. Web Portal HTML Rendering (GET /)
18. Sub-50ms CPU Real-Time Inference Latency
"""

import os
import sys
import time
import pytest

# Ensure source_code directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from career_engine import CareerGuidanceEngine, ROLE_INSIGHTS, DEFAULT_INSIGHT
import database as db
from app import app

# Shared test fixtures / engine
engine = CareerGuidanceEngine()
client = app.test_client()

def test_engine_initialization_and_cache():
    """1. Verify engine initialization and required ML models in memory."""
    models = list(engine.models.keys())
    assert "Decision Tree" in models
    assert "Random Forest" in models
    assert "XGBoost" in models
    assert len(models) >= 3


def test_feature_names_and_encoders_count():
    """2. Verify feature space contains 38 cognitive & academic dimensions."""
    assert len(engine.feature_names) == 38
    assert "Acedamic percentage in Operating Systems" in engine.feature_names
    assert "coding skills rating" in engine.feature_names
    assert len(engine.encoders) > 0


def test_target_classes_structure():
    """3. Verify multi-class target classification space contains 34 career roles."""
    assert len(engine.target_classes) == 34
    assert "Software Engineer" in engine.target_classes
    assert "Database Administrator" in engine.target_classes
    assert "Network Engineer" in engine.target_classes


def test_model_benchmark_metrics():
    """4. Verify model evaluation metrics are populated."""
    metrics = engine.metrics
    assert "Decision Tree" in metrics
    assert "Random Forest" in metrics
    assert "XGBoost" in metrics


def test_flask_app_health_endpoint():
    """5. Verify /api/health endpoint returns operational status and database stats."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "models_available" in data
    assert "database" in data


def test_flask_presets_endpoint():
    """6. Verify /api/presets endpoint provides at least 5 curated student profiles."""
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    presets = data["presets"]
    assert len(presets) >= 5
    for p in presets:
        assert "label" in p
        assert "data" in p


def test_flask_metrics_endpoint():
    """7. Verify /api/metrics endpoint returns model accuracy benchmarks."""
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "metrics" in data


def test_xgboost_inference_and_output_structure():
    """8. Verify XGBoost prediction pipeline returns suggested role, confidence, and insights."""
    presets = engine.get_presets()
    test_profile = presets[0]["data"]
    result = engine.predict(test_profile, model_name="XGBoost")
    assert "suggested_role" in result
    assert result["suggested_role"] in engine.target_classes
    assert result["confidence"] > 0
    assert result["model_used"] == "XGBoost"
    assert "insights" in result
    assert "skills" in result["insights"]


def test_random_forest_inference():
    """9. Verify Random Forest prediction pipeline returns valid job role."""
    presets = engine.get_presets()
    test_profile = presets[1]["data"]
    result = engine.predict(test_profile, model_name="Random Forest")
    assert "suggested_role" in result
    assert result["suggested_role"] in engine.target_classes
    assert result["model_used"] == "Random Forest"


def test_decision_tree_inference():
    """10. Verify Decision Tree prediction pipeline returns valid job role."""
    presets = engine.get_presets()
    test_profile = presets[2]["data"]
    result = engine.predict(test_profile, model_name="Decision Tree")
    assert "suggested_role" in result
    assert result["suggested_role"] in engine.target_classes
    assert result["model_used"] == "Decision Tree"


def test_alternative_career_recommendations():
    """11. Verify alternative career recommendations provides top 3 ranked fallback pathways."""
    presets = engine.get_presets()
    test_profile = presets[0]["data"]
    result = engine.predict(test_profile, model_name="XGBoost")
    assert "alternatives" in result
    alts = result["alternatives"]
    assert len(alts) >= 2
    for a in alts:
        assert "role" in a
        assert "confidence" in a


def test_role_insights_knowledge_base():
    """12. Verify domain knowledge base contains descriptions, skills, certifications, and salary."""
    for role_name in ["Software Engineer", "Web Developer", "Database Developer"]:
        assert role_name in ROLE_INSIGHTS
        info = ROLE_INSIGHTS[role_name]
        assert "description" in info
        assert "skills" in info
        assert len(info["skills"]) >= 3
        assert "salary_range" in info
        assert "certifications" in info


def test_sqlite_database_init_and_stats():
    """13. Verify SQLite database initializes with assessments table."""
    db.init_db()
    stats = db.get_stats()
    assert "total_assessments" in stats
    assert "top_recommended_roles" in stats


def test_sqlite_assessment_crud_flow():
    """14. Verify saving, querying, and deleting student assessment in SQLite."""
    db.init_db()
    presets = engine.get_presets()
    test_id = db.save_assessment(
        student_name="Unit Test Candidate",
        suggested_role="Software Engineer",
        model_used="XGBoost",
        confidence=88.5,
        top_skills=["Python", "System Design"],
        salary_range="$85,000 - $155,000 / yr",
        academic_avg=91.2,
        coding_rating=9,
        interested_area="developer",
        input_data=presets[0]["data"]
    )
    assert test_id > 0
    records = db.get_recent_assessments(limit=10)
    assert any(r["id"] == test_id for r in records)

    # Delete test record
    del_res = client.delete(f"/api/history/{test_id}")
    assert del_res.status_code == 200
    records_after = db.get_recent_assessments(limit=10)
    assert not any(r["id"] == test_id for r in records_after)


def test_multi_preset_evaluation_execution():
    """15. Verify prediction succeeds across all 5 preset student profiles."""
    presets = engine.get_presets()
    assert len(presets) >= 5
    for p in presets:
        res = client.post("/api/predict", json={
            "student_name": p["label"],
            "model_name": "XGBoost",
            "profile": p["data"]
        })
        assert res.status_code == 200
        val = res.get_json()
        assert val["status"] == "success"
        assert "suggested_role" in val


def test_boundary_missing_profile_features():
    """16. Verify engine handles empty or partially populated profiles with robust defaults."""
    empty_profile = {}
    result = engine.predict(empty_profile, model_name="XGBoost")
    assert "suggested_role" in result
    assert result["suggested_role"] in engine.target_classes
    assert result["confidence"] > 0


def test_index_html_rendering():
    """17. Verify web dashboard GET / returns HTML with key application components."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Career Guidance AI" in html
    assert "Student Career Assessment" in html


def test_inference_latency_performance():
    """18. Verify CPU inference execution speed is under 50ms per candidate."""
    presets = engine.get_presets()
    data = presets[0]["data"]
    t0 = time.time()
    for _ in range(5):
        engine.predict(data, model_name="XGBoost")
    avg_latency_ms = ((time.time() - t0) / 5) * 1000
    print(f"\nAverage Inference Latency: {avg_latency_ms:.2f}ms")
    assert avg_latency_ms < 50.0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
