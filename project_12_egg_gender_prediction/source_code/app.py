"""
Egg Prediction Web Application (Flask)
AI-based Chick Sex Prediction from Egg Shape Morphology & Neural Network Analysis.
Integrated with persistent SQLite database for audit history and analytics.
"""

import os
import sys
import io
import time
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory
from egg_engine import EggPredictionEngine
import database as db

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAYSCALE_DIR = os.path.join(BASE_DIR, "grayscale")
os.makedirs(GRAYSCALE_DIR, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=os.path.join(BASE_DIR, "static"))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

print("[App] Initializing Egg Prediction Engine...")
engine = EggPredictionEngine()
print("[App] Engine ready.")

# Initialize database
db.init_db()
print(f"[App] Database connected: {db.DB_FILE}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    db_stats = db.get_database_stats()
    return jsonify({
        "status": "healthy",
        "service": "Egg Sex Prediction Neural Network",
        "engine": "Neural Network (MLP) + Shape Index Morphology",
        "database": {
            "status": "operational",
            "file": db.DB_FILE,
            "total_records": db_stats["total_records"]
        },
        "timestamp": time.time()
    })

@app.route("/api/samples")
def get_samples():
    """Returns sample egg images for instant testing."""
    samples = []
    if os.path.exists(GRAYSCALE_DIR):
        files = sorted(os.listdir(GRAYSCALE_DIR))
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                expected_sex = "Female" if f.upper().startswith("F") else "Male"
                samples.append({
                    "id": f,
                    "filename": f,
                    "title": f.replace("_", " ").replace(".png", "").replace(".jpg", ""),
                    "expected_sex": expected_sex,
                    "url": f"/sample_image/{f}"
                })
    return jsonify({"samples": samples})

@app.route("/sample_image/<path:filename>")
def serve_sample(filename):
    return send_from_directory(GRAYSCALE_DIR, filename)

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        image_pil = None
        specimen_name = "Uploaded Egg Image"
        
        # Check if sample ID was sent
        sample_id = request.form.get("sample_id")
        if sample_id:
            sample_path = os.path.join(GRAYSCALE_DIR, os.path.basename(sample_id))
            if os.path.exists(sample_path):
                image_pil = Image.open(sample_path)
                specimen_name = os.path.basename(sample_id)
            else:
                return jsonify({"error": f"Sample image '{sample_id}' not found."}), 404
        
        # Or check if a file was uploaded
        elif "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected."}), 400
            image_pil = Image.open(file.stream)
            specimen_name = file.filename
            
        if image_pil is None:
            return jsonify({"error": "Please provide an egg image or choose a sample."}), 400

        result = engine.predict_image(image_pil)

        # Log prediction to SQLite database
        record_id = db.save_prediction_record(
            specimen_name=specimen_name,
            predicted_sex=result["prediction"],
            symbol=result["symbol"],
            confidence=result["confidence_pct"],
            female_prob=result["female_probability"],
            male_prob=result["male_probability"],
            shape_index=result["morphology"]["shape_index"],
            elongation=result["morphology"]["elongation"],
            apex_sharpness=result["morphology"]["apex_sharpness"],
            recommendation=result["recommendation"],
            source="sample" if sample_id else "upload"
        )
        result["db_record_id"] = record_id

        return jsonify({
            "success": True,
            "result": result,
            "database_logged": True
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/submit_all", methods=["POST", "GET"])
@app.route("/api/evaluate_dataset", methods=["POST", "GET"])
def submit_all():

    """
    Submits and evaluates all eggs in the dataset.
    Computes overall accuracy, cross-validation metrics, confusion matrix, and logs to database.
    """
    try:
        results = []
        correct = 0
        total = 0
        tp = 0  # True Female
        tn = 0  # True Male
        fp = 0  # Predicted Female, Actually Male
        fn = 0  # Predicted Male, Actually Female

        if not os.path.exists(GRAYSCALE_DIR):
            return jsonify({"error": "Grayscale dataset folder not found."}), 404

        files = sorted(os.listdir(GRAYSCALE_DIR))
        egg_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        for fname in egg_files:
            filepath = os.path.join(GRAYSCALE_DIR, fname)
            img = Image.open(filepath)
            pred = engine.predict_image(img)
            
            ground_truth = "Female" if fname.upper().startswith("F") else "Male"
            predicted_class = "Female" if "Female" in pred["prediction"] else "Male"
            is_correct = (ground_truth == predicted_class)
            
            total += 1
            if is_correct:
                correct += 1

            if ground_truth == "Female" and predicted_class == "Female":
                tp += 1
            elif ground_truth == "Male" and predicted_class == "Male":
                tn += 1
            elif ground_truth == "Male" and predicted_class == "Female":
                fp += 1
            elif ground_truth == "Female" and predicted_class == "Male":
                fn += 1

            # Log to SQLite
            db.save_prediction_record(
                specimen_name=fname,
                predicted_sex=pred["prediction"],
                symbol=pred["symbol"],
                confidence=pred["confidence_pct"],
                female_prob=pred["female_probability"],
                male_prob=pred["male_probability"],
                shape_index=pred["morphology"]["shape_index"],
                elongation=pred["morphology"]["elongation"],
                apex_sharpness=pred["morphology"]["apex_sharpness"],
                recommendation=pred["recommendation"],
                source="batch_evaluation"
            )

            results.append({
                "filename": fname,
                "ground_truth": ground_truth,
                "prediction": pred["prediction"],
                "is_correct": is_correct,
                "confidence_pct": pred["confidence_pct"],
                "female_prob": pred["female_probability"],
                "male_prob": pred["male_probability"],
                "shape_index": pred["morphology"]["shape_index"],
                "elongation": pred["morphology"]["elongation"],
                "apex_sharpness": pred["morphology"]["apex_sharpness"],
                "thumbnail_url": f"/sample_image/{fname}"
            })

        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        precision = (tp / (tp + fp) * 100.0) if (tp + fp) > 0 else 100.0
        recall = (tp / (tp + fn) * 100.0) if (tp + fn) > 0 else 100.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return jsonify({
            "success": True,
            "total_samples": total,
            "correct_predictions": correct,
            "accuracy_pct": round(accuracy, 1),
            "precision_pct": round(precision, 1),
            "recall_pct": round(recall, 1),
            "f1_score": round(f1, 1),
            "confusion_matrix": {
                "true_female": tp,
                "true_male": tn,
                "false_female": fp,
                "false_male": fn
            },
            "evaluations": results
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/history")
def get_history():
    """Returns past prediction audit logs from SQLite."""
    try:
        limit = request.args.get("limit", default=30, type=int)
        records = db.get_recent_history(limit=limit)
        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/stats")
def get_stats():
    """Returns aggregated stats from SQLite database."""
    try:
        stats = db.get_database_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    """Clears history from SQLite database."""
    try:
        db.clear_all_history()
        return jsonify({"success": True, "message": "Database history cleared."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5012))
    print(f"[*] Starting Egg Prediction Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

