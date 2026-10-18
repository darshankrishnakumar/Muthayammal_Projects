"""
Standalone Python HTTP Inference Service for 1D CNN Arrhythmia Classification.

Endpoints:
- GET  /health   -> Verifies model health and load status
- POST /predict  -> Accepts ECG file path or raw samples, applies standardized
                    preprocessing, executes model forward pass, and returns genuine results.

Port: 5001 (configurable via PORT environment variable)
"""

import os
import sys
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import numpy as np

# Add project root to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from preprocessing.ecg_pipeline import (
    butter_bandpass_filter,
    detect_r_peaks,
    segment_beat,
    normalize_beat,
    AAMI_CLASSES,
    AAMI_CODES,
    WINDOW_SIZE,
)

# Global model and config holders
MODEL = None
CONFIG = None
MODEL_PATH = os.path.join(SCRIPT_DIR, "saved-model", "ecg_cnn.keras")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "saved-model", "preprocessing_config.json")


def load_model_and_config():
    global MODEL, CONFIG
    import tensorflow as tf

    if not os.path.exists(MODEL_PATH):
        print(f"[WARN] Model file not found at {MODEL_PATH}")
        return False

    try:
        MODEL = tf.keras.models.load_model(MODEL_PATH)
        print(f"[OK] 1D CNN Model loaded from {MODEL_PATH}")

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                CONFIG = json.load(f)
            print(f"[OK] Preprocessing config loaded from {CONFIG_PATH}")
        else:
            CONFIG = {
                "model_name": "1D CNN Arrhythmia Classifier",
                "model_version": "1.0.0",
                "sampling_rate_hz": 360,
            }
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        traceback.print_exc()
        return False


def read_ecg_signal_from_file(file_path, file_format):
    """
    Parse raw voltage values from stored ECG file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ECG file not found at {file_path}")

    ext = (file_format or "").lower().replace(".", "")

    if ext in ["csv", "txt"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]

        samples = []
        for line in lines:
            parts = [p.strip() for p in line.replace(",", " ").replace("\t", " ").split()]
            nums = []
            for p in parts:
                try:
                    nums.append(float(p))
                except ValueError:
                    pass
            if not nums:
                continue
            val = nums[1] if len(nums) > 1 else nums[0]
            samples.append(val)

        if len(samples) < 5:
            raise ValueError("Insufficient signal samples in ECG file (at least 5 samples required).")
        return np.array(samples, dtype=np.float32)

    elif ext == "json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            raw_list = data
        elif isinstance(data, dict):
            raw_list = data.get("samples") or data.get("data") or data.get("voltage") or []
        else:
            raw_list = []

        samples = [float(x if isinstance(x, (int, float)) else x.get("mv", 0)) for x in raw_list]
        if len(samples) < 5:
            raise ValueError("Insufficient signal samples in ECG JSON file.")
        return np.array(samples, dtype=np.float32)

    elif ext in ["dat", "hea"]:
        import wfdb
        base_path = os.path.splitext(file_path)[0]
        rec = wfdb.rdrecord(base_path)
        return rec.p_signal[:, 0].astype(np.float32)

    else:
        raise ValueError(f"Unsupported ECG file format '{ext}' for direct inference.")


def run_pipeline_inference(signal_array, fs=360.0):
    """
    Apply bandpass filtering, extract beats, run 1D CNN forward pass, and compute clinical output.
    """
    global MODEL, CONFIG
    if MODEL is None:
        raise RuntimeError("Model is not loaded.")

    sig_len = len(signal_array)
    if sig_len < 30:
        raise ValueError("ECG signal too short for cardiac cycle analysis.")

    # 1. Bandpass filter signal
    filtered = butter_bandpass_filter(signal_array, fs=fs)

    # 2. Detect R-peaks
    r_peaks = detect_r_peaks(filtered, fs=fs)

    beats = []
    if len(r_peaks) > 0:
        for rp in r_peaks:
            b = segment_beat(filtered, rp)
            beats.append(b)
    else:
        # If no distinct R-peaks detected (e.g. short snippet or isolated segment),
        # extract uniform sliding windows
        step = WINDOW_SIZE // 2
        for start in range(0, max(1, sig_len - WINDOW_SIZE + 1), step):
            segment = filtered[start : start + WINDOW_SIZE]
            if len(segment) < WINDOW_SIZE:
                padded = np.zeros(WINDOW_SIZE, dtype=np.float32)
                padded[:len(segment)] = segment
                segment = padded
            beats.append(normalize_beat(segment))

    if not beats:
        beats.append(normalize_beat(filtered[:WINDOW_SIZE]))

    beats_batch = np.array(beats, dtype=np.float32)
    beats_batch = np.expand_dims(beats_batch, axis=-1)  # (N, 187, 1)

    # 3. Model forward pass
    preds = MODEL.predict(beats_batch, verbose=0)  # Shape (N, 5)

    # 4. Compute aggregate decision
    # Mean class probabilities across all beats
    mean_probs = np.mean(preds, axis=0)
    top_class_idx = int(np.argmax(mean_probs))
    confidence = float(mean_probs[top_class_idx])

    pred_name = AAMI_CLASSES.get(top_class_idx, "Unknown")
    pred_code = AAMI_CODES.get(top_class_idx, "Q")

    prob_dict = {
        AAMI_CODES[i]: round(float(mean_probs[i]), 4)
        for i in range(len(AAMI_CLASSES))
    }

    explanation = (
        f"Analyzed {len(beats)} cardiac cycle(s). Predominant rhythm classified as "
        f"{pred_name} ({pred_code}) with {confidence * 100:.1f}% model confidence."
    )

    return {
        "modelName": CONFIG.get("model_name", "1D CNN Arrhythmia Classifier") if CONFIG else "1D CNN Arrhythmia Classifier",
        "modelVersion": CONFIG.get("model_version", "1.0.0") if CONFIG else "1.0.0",
        "predictedClass": pred_name,
        "predictedCode": pred_code,
        "confidenceScore": round(confidence, 4),
        "totalBeatsAnalyzed": len(beats),
        "classProbabilities": prob_dict,
        "explanation": explanation,
    }


class InferenceHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            is_ready = MODEL is not None
            self._send_json(200 if is_ready else 503, {
                "status": "healthy" if is_ready else "model_not_loaded",
                "model": "1D CNN Arrhythmia Classifier",
                "version": "1.0.0",
                "ready": is_ready,
                "classes": list(AAMI_CLASSES.values()),
            })
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == "/predict":
            if MODEL is None:
                self._send_json(503, {
                    "code": "MODEL_NOT_CONNECTED",
                    "message": "The 1D CNN model has not been loaded.",
                })
                return

            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                payload = json.loads(body.decode("utf-8"))

                # 1. Read signal from filePath or raw samples
                if "filePath" in payload:
                    file_path = payload["filePath"]
                    file_format = payload.get("fileFormat", "csv")
                    signal_array = read_ecg_signal_from_file(file_path, file_format)
                elif "samples" in payload:
                    signal_array = np.array(payload["samples"], dtype=np.float32)
                else:
                    self._send_json(400, {
                        "code": "INVALID_PAYLOAD",
                        "message": "Request must contain either 'filePath' or 'samples'.",
                    })
                    return

                fs = float(payload.get("samplingFrequencyHz", 360.0))
                result = run_pipeline_inference(signal_array, fs=fs)
                self._send_json(200, result)

            except FileNotFoundError as e:
                self._send_json(404, {"code": "FILE_NOT_FOUND", "message": str(e)})
            except ValueError as e:
                self._send_json(422, {"code": "INVALID_ECG_DATA", "message": str(e)})
            except Exception as e:
                traceback.print_exc()
                self._send_json(500, {"code": "INFERENCE_ERROR", "message": str(e)})
        else:
            self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        # Concise logging
        print(f"[Inference Service] {args[0]} - {args[1]}", flush=True)


def run_service(port=5001):
    print("=" * 70)
    print("Starting ECG 1D CNN HTTP Inference Service")
    print("=" * 70)
    load_model_and_config()
    server_address = ("", port)
    httpd = HTTPServer(server_address, InferenceHandler)
    print(f"[OK] Inference Server listening on http://localhost:{port}")
    print("Endpoints:")
    print(f"  GET  http://localhost:{port}/health")
    print(f"  POST http://localhost:{port}/predict")
    print("=" * 70, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down inference server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    run_service(port=port)
