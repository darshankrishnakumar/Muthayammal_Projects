import os
import json
import numpy as np
import cv2

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(DATA_DIR, "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

def create_sample_images():
    scenarios = [
        {
            "id": "SMP-01",
            "name": "Handgun at Concourse A",
            "filename": "sample_handgun_detection.jpg",
            "class": "handgun",
            "category": "Firearm",
            "threat": "CRITICAL",
            "camera_id": "CAM-01",
            "bbox": [280, 190, 110, 85],
            "description": "Suspect drawing concealed semi-automatic pistol near boarding gate."
        },
        {
            "id": "SMP-02",
            "name": "Tactical Knife at Checkpoint",
            "filename": "sample_knife_detection.jpg",
            "class": "knife",
            "category": "Bladed Weapon",
            "threat": "HIGH",
            "camera_id": "CAM-03",
            "bbox": [320, 240, 130, 45],
            "description": "Exposed fixed-blade combat knife detected in passenger baggage."
        },
        {
            "id": "SMP-03",
            "name": "Long Rifle at Perimeter Gate",
            "filename": "sample_assault_rifle.jpg",
            "class": "assault_rifle",
            "category": "Long Firearm",
            "threat": "CRITICAL",
            "camera_id": "CAM-03",
            "bbox": [180, 160, 240, 95],
            "description": "Unauthorized individual bearing military assault rifle at vehicle gate."
        },
        {
            "id": "SMP-04",
            "name": "Suspicious Explosive IED Package",
            "filename": "sample_suspicious_package.jpg",
            "class": "explosive",
            "category": "IED / Explosive",
            "threat": "CRITICAL",
            "camera_id": "CAM-02",
            "bbox": [240, 220, 160, 140],
            "description": "Unattended suspicious case with high-density wiring and battery signature."
        },
        {
            "id": "SMP-05",
            "name": "Routine Civilian Clearance (Safe)",
            "filename": "sample_civilian_safe.jpg",
            "class": None,
            "category": "Safe",
            "threat": "SAFE",
            "camera_id": "CAM-04",
            "bbox": None,
            "description": "Normal terminal pedestrian flow with zero threat detection."
        }
    ]

    for item in scenarios:
        # Create 640x480 security surveillance frame
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Gradient background representing terminal hall / corridor
        for y in range(480):
            val = int(35 + (y / 480.0) * 45)
            img[y, :] = (val - 10, val, val + 15)

        # Draw architectural floor tiles and hallway perspective
        cv2.line(img, (0, 480), (220, 240), (70, 75, 85), 2)
        cv2.line(img, (640, 480), (420, 240), (70, 75, 85), 2)
        cv2.line(img, (220, 240), (420, 240), (70, 75, 85), 2)

        # Draw CCTV timestamp & camera watermark
        cv2.putText(img, f"CCTV [{item['camera_id']}] 2026-10-19 14:22:08 UTC", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(img, "SEC-ZONE: OPTICAL SURVEILLANCE FEED", (15, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        # If scenario has a weapon, render weapon silhouette & shape
        if item["bbox"]:
            x, y, w, h = item["bbox"]
            # Human silhouette in background
            cv2.ellipse(img, (x + w//2, y - 45), (28, 38), 0, 0, 360, (50, 50, 60), -1)
            cv2.rectangle(img, (x - 20, y - 10), (x + w + 20, y + h + 80), (45, 45, 55), -1)

            # Draw weapon object
            if item["class"] == "handgun":
                # L-shaped handgun
                cv2.rectangle(img, (x, y), (x + w, y + 35), (25, 25, 30), -1) # slide/barrel
                cv2.rectangle(img, (x + w - 40, y + 25), (x + w - 10, y + h), (20, 20, 25), -1) # grip
                cv2.rectangle(img, (x + 10, y + 32), (x + 25, y + 35), (80, 80, 85), -1) # trigger guard
            elif item["class"] == "knife":
                # Elongated blade & handle
                cv2.fillPoly(img, [np.array([[x, y+15], [x+w-30, y+10], [x+w, y+22], [x+w-30, y+35], [x, y+28]])], (180, 185, 195)) # steel blade
                cv2.rectangle(img, (x, y + 10), (x + 35, y + 32), (30, 30, 35), -1) # handle
            elif item["class"] == "assault_rifle":
                # Long rifle profile
                cv2.rectangle(img, (x, y + 20), (x + w, y + 50), (25, 25, 30), -1) # receiver & barrel
                cv2.rectangle(img, (x + 40, y + 45), (x + 75, y + h), (20, 20, 25), -1) # curved magazine
                cv2.rectangle(img, (x + w - 50, y + 45), (x + w - 20, y + h - 15), (35, 35, 40), -1) # stock
                cv2.rectangle(img, (x + 120, y + 5), (x + 150, y + 20), (50, 50, 55), -1) # optical sight
            elif item["class"] == "explosive":
                # Heavy industrial package with wires
                cv2.rectangle(img, (x, y), (x + w, y + h), (30, 40, 45), -1)
                cv2.rectangle(img, (x + 15, y + 15), (x + w - 15, y + h - 15), (60, 25, 25), -1)
                cv2.line(img, (x + 25, y + 30), (x + w - 30, y + 50), (0, 0, 255), 2)
                cv2.line(img, (x + 25, y + 60), (x + w - 30, y + 80), (0, 255, 255), 2)
        else:
            # Safe civilian passengers
            cv2.ellipse(img, (320, 180), (32, 42), 0, 0, 360, (75, 80, 95), -1)
            cv2.rectangle(img, (285, 220), (355, 420), (60, 70, 90), -1)
            cv2.putText(img, "CLEAR PASSENGER CONCOURSE", (210, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 120), 1, cv2.LINE_AA)

        # Add camera sensor noise
        noise = np.random.normal(0, 4, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)

        file_path = os.path.join(SAMPLES_DIR, item["filename"])
        cv2.imwrite(file_path, img)
        print(f"Generated sample image: {file_path}")

    manifest_path = os.path.join(DATA_DIR, "dataset_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)
    print(f"Saved dataset manifest: {manifest_path}")

if __name__ == "__main__":
    create_sample_images()
