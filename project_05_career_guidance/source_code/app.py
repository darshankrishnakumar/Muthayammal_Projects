"""
Career Guidance ML Web Application (Flask)
AI-Powered Job Role & Career Recommendation System
Trained on Multi-Dimensional Student Academic & Cognitive Profiles.
"""

import os
import sys
import time
from flask import Flask, render_template, request, jsonify
from career_engine import CareerGuidanceEngine
import database as db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.config["SECRET_KEY"] = "career-guidance-ml-secret-key-2026"

print("[App] Initializing Career Guidance Engine...")
engine = CareerGuidanceEngine()
print("[App] Engine ready.")

print("[App] Initializing SQLite Database...")
db.init_db()
print(f"[App] Database connected: {db.DB_FILE}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    stats = db.get_stats()
    return jsonify({
        "status": "healthy",
        "service": "Career Guidance & Job Role Recommendation AI",
        "models_available": list(engine.models.keys()),
        "metrics": engine.metrics,
        "database": {
            "status": "operational",
            "file": db.DB_FILE,
            "total_assessments": stats["total_assessments"]
        },
        "timestamp": time.time()
    })

@app.route("/api/presets")
def get_presets():
    return jsonify({
        "status": "success",
        "presets": engine.get_presets()
    })

@app.route("/api/metrics")
def get_metrics():
    return jsonify({
        "status": "success",
        "metrics": engine.metrics
    })

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"status": "error", "message": "No input payload provided"}), 400

        student_name = payload.get("student_name", "Candidate")
        model_name = payload.get("model_name", "XGBoost")
        profile_data = payload.get("profile", {})

        result = engine.predict(profile_data, model_name=model_name)

        # Compute academic average
        acad_keys = [
            "Acedamic percentage in Operating Systems", "percentage in Algorithms",
            "Percentage in Programming Concepts", "Percentage in Software Engineering",
            "Percentage in Computer Networks", "Percentage in Electronics Subjects",
            "Percentage in Computer Architecture", "Percentage in Mathematics",
            "Percentage in Communication skills"
        ]
        acad_vals = []
        for k in acad_keys:
            try:
                acad_vals.append(float(profile_data.get(k, 0)))
            except (ValueError, TypeError):
                pass
        acad_avg = round(sum(acad_vals) / len(acad_vals), 1) if acad_vals else 0.0
        coding_rating = int(profile_data.get("coding skills rating", 5))
        interested_area = str(profile_data.get("interested career area ", "Technology"))

        record_id = db.save_assessment(
            student_name=student_name,
            suggested_role=result["suggested_role"],
            model_used=result["model_used"],
            confidence=result["confidence"],
            top_skills=result["insights"].get("skills", []),
            salary_range=result["insights"].get("salary_range", "N/A"),
            academic_avg=acad_avg,
            coding_rating=coding_rating,
            interested_area=interested_area,
            input_data=profile_data
        )

        result["record_id"] = record_id
        result["student_name"] = student_name
        result["academic_avg"] = acad_avg
        result["status"] = "success"

        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    records = db.get_recent_assessments(limit=50)
    stats = db.get_stats()
    return jsonify({
        "status": "success",
        "total": stats["total_assessments"],
        "top_roles": stats["top_recommended_roles"],
        "records": records
    })

@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    success = db.delete_assessment(record_id)
    return jsonify({"status": "success" if success else "not_found"})

@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    db.clear_all_assessments()
    return jsonify({"status": "success", "message": "History cleared successfully"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5055))
    print(f"\n==================================================================")
    print(f"  Career Guidance AI System running at http://127.0.0.1:{port}")
    print(f"==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
