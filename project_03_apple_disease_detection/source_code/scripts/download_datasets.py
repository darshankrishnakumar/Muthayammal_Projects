"""
Apple Health Intelligence AI - Dataset Download Guide and Utility
===================================================================
Provides clear instructions and automated helpers for acquiring the recommended
real-world training datasets:

1. Fruit and Vegetable Disease (Healthy vs Rotten):
   URL: https://www.kaggle.com/dsv/8463025 (or kaggle datasets download -d sriramr/fruits-fresh-and-rotten-for-classification)
   Target classes for Model A:
     - Fresh: FreshApple
     - Rotten: RottenApple

2. PlantVillage Apple Leaf Dataset:
   URL: https://figshare.com/articles/dataset/PlantVillage_Dataset/26096800
   (Also available via Kaggle: emmarex/plantdisease or abdallahalidev/plantvillage-dataset)
   Target classes for Model B:
     - Healthy: Apple___healthy
     - Apple_Scab: Apple___Apple_scab
     - Black_Rot: Apple___Black_rot
     - Cedar_Apple_Rust: Apple___Cedar_apple_rust

3. Fruits-360:
   URL: https://www.kaggle.com/moltean/fruits
   Used as supplementary data for fruit recognition / input validation:
     - Apple Braeburn, Apple Crimson Snow, Apple Golden, Apple Granny Smith, Apple Red, etc.
"""

import os
import sys
import argparse

DATASETS_CONFIG = {
    "fruit_and_vegetable_disease": {
        "name": "Fruit and Vegetable Disease (Fresh vs Rotten)",
        "source_url": "https://www.kaggle.com/dsv/8463025",
        "kaggle_slug": "sriramr/fruits-fresh-and-rotten-for-classification",
        "expected_subdirs": ["dataset/train/freshapples", "dataset/train/rottenapples"],
        "target_task": "Model A (Fruit Condition: Fresh vs Rotten)",
        "license": "CC0: Public Domain"
    },
    "plantvillage_apple_leaf": {
        "name": "PlantVillage Apple Foliar Pathology Dataset",
        "source_url": "https://figshare.com/articles/dataset/PlantVillage_Dataset/26096800",
        "kaggle_slug": "abdallahalidev/plantvillage-dataset",
        "expected_subdirs": [
            "segmented/Apple___healthy",
            "segmented/Apple___Apple_scab",
            "segmented/Apple___Black_rot",
            "segmented/Apple___Cedar_apple_rust"
        ],
        "target_task": "Model B (Leaf Disease: Healthy, Scab, Black Rot, Cedar Rust)",
        "license": "CC BY 4.0"
    },
    "fruits_360": {
        "name": "Fruits-360 Dataset",
        "source_url": "https://www.kaggle.com/moltean/fruits",
        "kaggle_slug": "moltean/fruits",
        "expected_subdirs": ["Training/Apple Golden 1", "Training/Apple Red 1"],
        "target_task": "Model C (Supplementary Apple Fruit Recognition)",
        "license": "CC BY-SA 4.0"
    }
}


def print_instructions():
    print("=" * 80)
    print(" APPLE HEALTH INTELLIGENCE AI - DATASET ACQUISITION INSTRUCTIONS")
    print("=" * 80)
    print("\nIn accordance with project guidelines, large datasets (multi-gigabytes)")
    print("are not silently downloaded in the background. Follow these steps:\n")

    for key, info in DATASETS_CONFIG.items():
        print(f"--- [{info['name']}] ---")
        print(f" Task:        {info['target_task']}")
        print(f" Primary URL: {info['source_url']}")
        print(f" Kaggle CLI:  kaggle datasets download -d {info['kaggle_slug']}")
        print(f" License:     {info['license']}")
        print(f" Placement:   Extract into: datasets/raw/{key}/\n")

    print("After downloading and placing files in datasets/raw/:")
    print("Run the dataset preparation script:")
    print("    python scripts/prepare_datasets.py --input_dir datasets/raw --output_dir datasets/processed")
    print("=" * 80)


def check_status(base_dir="datasets/raw"):
    print("Scanning dataset directory:", os.path.abspath(base_dir))
    if not os.path.exists(base_dir):
        print(f"[!] Directory {base_dir} does not exist yet.")
        return

    found_any = False
    for key, info in DATASETS_CONFIG.items():
        ds_path = os.path.join(base_dir, key)
        if os.path.exists(ds_path):
            count = sum(len(files) for _, _, files in os.walk(ds_path))
            print(f"[OK] Found {info['name']}: {count} files in {ds_path}")
            found_any = True
        else:
            print(f"[-] Missing: {info['name']} (expected at {ds_path})")

    if not found_any:
        print("\nNo raw datasets detected. Run python scripts/download_datasets.py --help for download instructions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset Download and Verification Helper")
    parser.add_argument("--status", action="store_true", help="Check current status of downloaded datasets")
    parser.add_argument("--raw_dir", default="datasets/raw", help="Path to raw dataset directory")
    args = parser.parse_args()

    if args.status:
        check_status(args.raw_dir)
    else:
        print_instructions()
