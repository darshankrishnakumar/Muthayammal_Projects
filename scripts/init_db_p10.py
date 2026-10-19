import sqlite3
import os
import time

db_dir = "/Users/eash/Documents/antigravity/excited-borg/project_10_deepfake_detector/source_code/data"
db_path = os.path.join(db_dir, "deepfake_detector.db")
os.makedirs(db_dir, exist_ok=True)

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS forensic_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    filename TEXT NOT NULL,
    prediction TEXT NOT NULL,
    is_deepfake INTEGER NOT NULL,
    confidence REAL NOT NULL,
    fft_anomaly_score REAL NOT NULL,
    boundary_discontinuity REAL NOT NULL,
    moderation_verdict TEXT NOT NULL,
    latency_ms REAL NOT NULL
)
""")

seed_records = [
    ("2026-10-19 11:15:20", "user_portrait_091.jpg", "REAL", 0, 0.9854, 0.1420, 0.0650, "AUTHENTIC VERIFIED", 18.2),
    ("2026-10-19 11:22:45", "social_avatar_fake22.jpg", "DEEPFAKE", 1, 0.9942, 0.7840, 0.8410, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 22.1),
    ("2026-10-19 11:34:10", "press_conference_c1.jpg", "REAL", 0, 0.9710, 0.1650, 0.0820, "AUTHENTIC VERIFIED", 19.5),
    ("2026-10-19 11:45:00", "celeb_faceswap_manip.png", "DEEPFAKE", 1, 0.9890, 0.5210, 0.8920, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 21.0),
    ("2026-10-19 11:58:12", "id_verification_scan08.jpg", "REAL", 0, 0.9920, 0.1280, 0.0540, "AUTHENTIC VERIFIED", 17.8),
    ("2026-10-19 12:05:30", "diffusion_portrait_gen.png", "DEEPFAKE", 1, 0.9965, 0.6950, 0.6450, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 23.4),
    ("2026-10-19 12:14:18", "candidate_headshot_a.jpg", "REAL", 0, 0.9680, 0.1910, 0.0910, "AUTHENTIC VERIFIED", 19.0),
    ("2026-10-19 12:28:44", "gan_generated_female.jpg", "DEEPFAKE", 1, 0.9912, 0.7630, 0.2840, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 20.8),
    ("2026-10-19 12:39:15", "student_id_card_04.jpg", "REAL", 0, 0.9880, 0.1550, 0.0710, "AUTHENTIC VERIFIED", 18.6),
    ("2026-10-19 12:47:00", "deepfake_video_frame_34.jpg", "DEEPFAKE", 1, 0.9820, 0.5420, 0.7950, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 21.9),
    ("2026-10-19 12:55:22", "employee_badge_face.jpg", "REAL", 0, 0.9740, 0.1780, 0.0880, "AUTHENTIC VERIFIED", 18.9),
    ("2026-10-19 13:02:11", "stylegan3_synthetic_male.png", "DEEPFAKE", 1, 0.9978, 0.8120, 0.3120, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 24.1),
    ("2026-10-19 13:12:40", "passport_photo_official.jpg", "REAL", 0, 0.9940, 0.1190, 0.0480, "AUTHENTIC VERIFIED", 17.5),
    ("2026-10-19 13:20:05", "tiktok_influencer_swap.mp4_f12.jpg", "DEEPFAKE", 1, 0.9865, 0.4950, 0.8650, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 20.5),
    ("2026-10-19 13:28:30", "news_anchor_live_frame.jpg", "REAL", 0, 0.9650, 0.2050, 0.0950, "AUTHENTIC VERIFIED", 19.8),
    ("2026-10-19 13:35:19", "midjourney_v6_photoreal.png", "DEEPFAKE", 1, 0.9930, 0.6720, 0.6200, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 22.8),
    ("2026-10-19 13:42:01", "driver_license_portrait.jpg", "REAL", 0, 0.9890, 0.1340, 0.0620, "AUTHENTIC VERIFIED", 18.0),
    ("2026-10-19 13:50:55", "ai_face_cloning_attack.jpg", "DEEPFAKE", 1, 0.9950, 0.7410, 0.7780, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 21.6),
    ("2026-10-19 13:58:20", "conference_speaker_real.jpg", "REAL", 0, 0.9780, 0.1600, 0.0760, "AUTHENTIC VERIFIED", 18.4),
    ("2026-10-19 14:05:10", "synthetic_bot_profile.png", "DEEPFAKE", 1, 0.9982, 0.8350, 0.8120, "CRITICAL SYNTHETIC FRAUD - QUARANTINED", 23.0)
]

cur.executemany("""
INSERT INTO forensic_scans (timestamp, filename, prediction, is_deepfake, confidence, fft_anomaly_score, boundary_discontinuity, moderation_verdict, latency_ms)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", seed_records)

conn.commit()
conn.close()
print(f"=== Successfully Created and Seeded Database with 20 Records at {db_path} ===")
