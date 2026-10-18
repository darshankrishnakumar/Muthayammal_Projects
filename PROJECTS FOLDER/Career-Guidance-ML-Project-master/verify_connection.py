import sqlite3
import os
import requests
import json

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "career_guidance.db")
print("==================================================================")
print("             BACKEND & DATABASE VERIFICATION CHECK")
print("==================================================================")

# 1. Direct SQLite Check
print("\n[1] Direct SQLite Database Inspection:")
print(f"    - Database file: {db_path}")
print(f"    - File exists  : {os.path.exists(db_path)}")
print(f"    - File size    : {os.path.getsize(db_path)} bytes")

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in c.fetchall()]
print(f"    - Tables found : {tables}")

c.execute("PRAGMA table_info(career_assessments);")
cols = [f"{col[1]} ({col[2]})" for col in c.fetchall()]
print(f"    - Schema columns: {cols}")

c.execute("SELECT COUNT(*) FROM career_assessments;")
total_in_db = c.fetchone()[0]
print(f"    - Total records in DB: {total_in_db}")

c.execute("SELECT id, timestamp, student_name, suggested_role, confidence FROM career_assessments ORDER BY id DESC LIMIT 2;")
recent = c.fetchall()
for r in recent:
    print(f"      * [ID {r[0]}] {r[1]} | {r[2]} -> {r[3]} ({r[4]}%)")
conn.close()

# 2. Live HTTP Backend API Check
print("\n[2] Live Backend REST API Check (http://127.0.0.1:5055):")
try:
    r_health = requests.get("http://127.0.0.1:5055/api/health", timeout=5)
    print(f"    - Health Check Status : HTTP {r_health.status_code}")
    health_data = r_health.json()
    print(f"    - Service Name        : {health_data.get('service')}")
    print(f"    - Database Connected  : {health_data.get('database', {}).get('status')}")
    print(f"    - DB Records Count    : {health_data.get('database', {}).get('total_assessments')}")

    r_history = requests.get("http://127.0.0.1:5055/api/history", timeout=5)
    print(f"    - History API Status  : HTTP {r_history.status_code}")
    print(f"    - Records retrieved   : {len(r_history.json().get('records', []))}")
    
    # 3. Live Round-Trip Write & Read Test
    print("\n[3] End-to-End Live Write & Read Verification:")
    sample_payload = {
        "student_name": "Database Connection Test",
        "model_name": "XGBoost",
        "profile": {
            "Acedamic percentage in Operating Systems": 90,
            "percentage in Algorithms": 90,
            "Percentage in Programming Concepts": 90,
            "Percentage in Software Engineering": 90,
            "Percentage in Computer Networks": 90,
            "Percentage in Electronics Subjects": 70,
            "Percentage in Computer Architecture": 80,
            "Percentage in Mathematics": 85,
            "Percentage in Communication skills": 85,
            "coding skills rating": 8,
            "hackathons": 3,
            "certifications": "python",
            "workshops": "cloud computing",
            "Extra-courses did": "yes",
            "talenttests taken?": "yes",
            "olympiads": "no",
            "reading and writing skills": "excellent",
            "Hours working per day": 8,
            "Logical quotient rating": 8,
            "public speaking points": 6,
            "memory capability score": "excellent",
            "can work long time before system?": "yes",
            "self-learning capability?": "yes",
            "hard/smart worker": "smart worker",
            "worked in teams ever?": "yes",
            "Introvert": "no",
            "Gentle or Tuff behaviour?": "gentle",
            "Interested subjects": "programming",
            "interested career area ": "developer",
            "Job/Higher Studies?": "job",
            "Type of company want to settle in?": "product development",
            "Management or Technical": "Technical",
            "Salary/work": "work",
            "Interested Type of Books": "Science fiction",
            "Taken inputs from seniors or elders": "yes",
            "Salary Range Expected": "salary",
            "In a Realtionship?": "no",
            "interested in games": "yes"
        }
    }
    r_post = requests.post("http://127.0.0.1:5055/api/predict", json=sample_payload, timeout=5)
    post_res = r_post.json()
    new_id = post_res.get("record_id")
    print(f"    - Live prediction POST: HTTP {r_post.status_code}")
    print(f"    - Assigned DB Record ID: {new_id}")
    print(f"    - Prediction Result   : {post_res.get('suggested_role')} ({post_res.get('confidence')}%)")
    
    # Confirm it can be read back from API
    r_verify = requests.get("http://127.0.0.1:5055/api/history", timeout=5)
    latest_record = r_verify.json().get("records", [])[0]
    assert latest_record["id"] == new_id
    print(f"    - Confirmed saved in SQLite and readable via API: OK!")

    print("\n==================================================================")
    print("  STATUS: YES! BACKEND & DATABASE ARE 100% OPERATIONAL & CONNECTED")
    print("==================================================================")

except Exception as e:
    print(f"    [ERROR] Connection failed: {e}")
