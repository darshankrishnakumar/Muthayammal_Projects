"""
Apple Health Intelligence AI - Fruit Condition Dataset Acquisition Script
Downloads real-world fresh and rotten apple images from the verified benchmark dataset.
"""

import os
import sys
import json
import urllib.request
from pathlib import Path
from PIL import Image
import io

RAW_DIR = Path("datasets/raw/fruit_condition")
FRESH_DIR = RAW_DIR / "Fresh"
ROTTEN_DIR = RAW_DIR / "Rotten"

REPO_API_BASE = "https://api.github.com/repos/Bangkit-JKT2-D/fruits-fresh-rotten-classification/contents/Datasets"

def fetch_file_list(endpoint):
    url = f"{REPO_API_BASE}/{endpoint}"
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
            # Verify image
            img = Image.open(io.BytesIO(img_bytes))
            img.verify()
            
            with open(target_path, "wb") as f:
                f.write(img_bytes)
            count += 1
            print(f"[{count}/{max_count}] Saved {target_dir.name}/{name} ({img.size})")
        except Exception as e:
            print(f"[!] Skipped {name}: {e}")
    return count

def main(count_per_class=60):
    print("=" * 60)
    print(f"ACQUIRING REAL APPLE FRUIT DATASET (Target: {count_per_class}/class)")
    print("=" * 60)
    
    # 1. Fresh Apples
    print("\nFetching Fresh Apples file manifest...")
    fresh_test_files = fetch_file_list("test/freshapples")
    fresh_downloaded = download_images(fresh_test_files, FRESH_DIR, max_count=count_per_class)
    print(f"[OK] Total Fresh images in {FRESH_DIR}: {fresh_downloaded}")

    # 2. Rotten Apples
    print("\nFetching Rotten Apples file manifest...")
    rotten_test_files = fetch_file_list("test/rottenapples")
    rotten_downloaded = download_images(rotten_test_files, ROTTEN_DIR, max_count=count_per_class)
    print(f"[OK] Total Rotten images in {ROTTEN_DIR}: {rotten_downloaded}")

    # 3. Incorporate local verified images from sample_images
    sample_fresh = Path("sample_images/normal_apple_sample.jpg")
    sample_rot = Path("sample_images/rot_apple_sample.jpg")
    if sample_fresh.exists():
        import shutil
        shutil.copy2(sample_fresh, FRESH_DIR / "sample_normal_apple.jpg")
    if sample_rot.exists():
        import shutil
        shutil.copy2(sample_rot, ROTTEN_DIR / "sample_rot_apple.jpg")

    print("\n[Complete] Raw dataset acquisition finished successfully.")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    main(count)
