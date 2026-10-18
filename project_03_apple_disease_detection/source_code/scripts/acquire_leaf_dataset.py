"""
Apple Health Intelligence AI - Leaf Disease Dataset Acquisition Script
Downloads authentic real-world Apple Leaf pathology images from the verified PlantVillage dataset.
Maps classes:
- Apple___healthy         -> Healthy
- Apple___Apple_scab      -> Apple_Scab
- Apple___Black_rot       -> Black_Rot
- Apple___Cedar_apple_rust -> Cedar_Apple_Rust
"""

import os
import sys
import json
import urllib.request
from pathlib import Path
from PIL import Image
import io

RAW_DIR = Path("datasets/raw/leaf_disease")
TARGET_CLASSES = {
    "Healthy": "Apple___healthy",
    "Apple_Scab": "Apple___Apple_scab",
    "Black_Rot": "Apple___Black_rot",
    "Cedar_Apple_Rust": "Apple___Cedar_apple_rust"
}

REPO_API_BASE = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color"

def fetch_file_list(class_subdir):
    url = f"{REPO_API_BASE}/{class_subdir}"
    req = urllib.request.Request(url, headers={"User-Agent": "AppleAIResearch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return []

def download_images(items, target_dir, max_count=60):
    target_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in items:
        if count >= max_count:
            break
        name = item.get("name")
        download_url = item.get("download_url")
        if not download_url:
            continue

        target_path = target_dir / name
        if target_path.exists():
            count += 1
            continue

        try:
            req = urllib.request.Request(download_url, headers={"User-Agent": "AppleAIResearch/1.0"})
            with urllib.request.urlopen(req, timeout=30) as res:
                img_bytes = res.read()
            # Verify image format and integrity
            img = Image.open(io.BytesIO(img_bytes))
            img.verify()

            with open(target_path, "wb") as f:
                f.write(img_bytes)
            count += 1
            if count % 10 == 0 or count == max_count:
                print(f"[{count}/{max_count}] Saved {target_dir.name}/{name} ({img.size})")
        except Exception as e:
            print(f"[!] Skipped {name}: {e}")
    return count

def main(count_per_class=60):
    print("=" * 70)
    print(f"ACQUIRING PLANTVILLAGE APPLE LEAF DATASET ({count_per_class} images/class)")
    print("=" * 70)

    for target_class, src_folder in TARGET_CLASSES.items():
        dest_dir = RAW_DIR / target_class
        print(f"\nFetching {target_class} from {src_folder}...")
        files = fetch_file_list(src_folder)
        downloaded = download_images(files, dest_dir, max_count=count_per_class)
        print(f"[OK] Total in {dest_dir}: {downloaded} images")

    # Seed verified local sample leaf images if available
    samples = Path("sample_images")
    if samples.exists():
        import shutil
        mapping = {
            "healthy_leaf_sample.jpg": RAW_DIR / "Healthy" / "sample_healthy_leaf.jpg",
            "scab_leaf_sample.jpg": RAW_DIR / "Apple_Scab" / "sample_scab_leaf.jpg",
            "black_rot_leaf_sample.jpg": RAW_DIR / "Black_Rot" / "sample_black_rot_leaf.jpg",
            "cedar_rust_sample.jpg": RAW_DIR / "Cedar_Apple_Rust" / "sample_cedar_rust_leaf.jpg"
        }
        for src_name, dst_path in mapping.items():
            s_file = samples / src_name
            if s_file.exists() and not dst_path.exists():
                shutil.copy2(s_file, dst_path)

    print("\n[Complete] PlantVillage leaf dataset acquisition finished.")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    main(count)
