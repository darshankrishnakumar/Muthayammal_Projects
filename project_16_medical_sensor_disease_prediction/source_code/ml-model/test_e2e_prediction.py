import urllib.request
import json
import os
import wfdb

print("Starting End-to-End Live Integration Verification...")

# 1. Create realistic MIT-BIH Lead II sample CSV
os.makedirs("backend/storage/test_samples", exist_ok=True)
sample_csv = "backend/storage/test_samples/sample_test_100.csv"
try:
    rec = wfdb.rdrecord("ml-model/dataset/mit-bih/100")
    with open(sample_csv, "w", encoding="utf-8") as f:
        f.write("time_sec,voltage_mv\n")
        for i in range(1800):
            f.write(f"{i/360:.4f},{rec.p_signal[i, 0]:.4f}\n")
except Exception:
    import numpy as np
    t = np.linspace(0, 5, 1800)
    # Realistic Lead II wave
    signal = np.zeros(1800)
    for beat_center in [0.8, 1.6, 2.4, 3.2, 4.0, 4.8]:
        p = 0.15 * np.exp(-((t - (beat_center - 0.16))**2) / (2 * 0.02**2))
        q = -0.15 * np.exp(-((t - (beat_center - 0.03))**2) / (2 * 0.008**2))
        r = 1.0 * np.exp(-((t - beat_center)**2) / (2 * 0.012**2))
        s = -0.35 * np.exp(-((t - (beat_center + 0.03))**2) / (2 * 0.01**2))
        tw = 0.3 * np.exp(-((t - (beat_center + 0.25))**2) / (2 * 0.06**2))
        signal += (p + q + r + s + tw)
    signal += np.random.normal(0, 0.01, 1800)
    with open(sample_csv, "w", encoding="utf-8") as f:
        f.write("time_sec,voltage_mv\n")
        for i in range(1800):
            f.write(f"{i/360:.4f},{signal[i]:.4f}\n")
print(f"[1/4] Created benchmark sample file at: {sample_csv}")

# 2. Upload file through Node.js Express backend
boundary = "----WebKitFormBoundaryE2ETestBoundary777"
with open(sample_csv, "rb") as f:
    file_bytes = f.read()

header = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="sample_test_100.csv"\r\n'
    f"Content-Type: text/csv\r\n\r\n"
).encode("utf-8")
footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
body = header + file_bytes + footer

backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:5016")

upload_req = urllib.request.Request(
    f"{backend_url}/api/ecg/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
with urllib.request.urlopen(upload_req) as resp:
    upload_res = json.loads(resp.read().decode("utf-8"))

recording_id = int(upload_res["data"]["recordingId"])
print(f"[2/4] Uploaded ECG recording. Backend assigned ID: #{recording_id}")

# 3. Trigger 1D CNN Inference via Node backend -> Python HTTP inference service
pred_payload = json.dumps({"recordingId": recording_id}).encode("utf-8")
pred_req = urllib.request.Request(
    f"{backend_url}/api/predictions",
    data=pred_payload,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(pred_req) as resp:
    pred_res = json.loads(resp.read().decode("utf-8"))

print(f"[3/4] 1D CNN Prediction completed successfully!")
prediction_data = pred_res["data"]
print(f"      Model Name:        {prediction_data.get('modelName')}")
print(f"      Model Version:     {prediction_data.get('modelVersion')}")
print(f"      Predicted Class:   {prediction_data.get('predictedClass')}")
print(f"      Confidence Score:  {prediction_data.get('confidenceScore')}")
print(f"      Explanation:       {prediction_data.get('explanation')}")

# 4. Verify History API
with urllib.request.urlopen(f"{backend_url}/api/predictions/history") as resp:
    hist_res = json.loads(resp.read().decode("utf-8"))

history_items = hist_res["data"]
print(f"[4/4] Verification of SQLite History: Found {len(history_items)} recorded prediction(s).")
assert any(int(h["recordingId"]) == recording_id for h in history_items), "New prediction not found in history!"

print("\nALL END-TO-END CNN PIPELINE CHECKS PASSED SUCCESSFULLY!")
