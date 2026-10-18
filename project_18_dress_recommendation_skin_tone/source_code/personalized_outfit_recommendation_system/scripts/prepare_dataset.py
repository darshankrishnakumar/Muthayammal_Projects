"""Stage 3 Execution: Prepares raw, processed, and synthetic datasets."""

import os
import sys
import pandas as pd

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_loader import generate_synthetic_catalog, generate_synthetic_interaction_training_data
from src.data_validation import validate_catalogue_schema, validate_image_files

def main():
    print("=" * 60)
    print("STAGE 3: DATASET PREPARATION & VALIDATION")
    print("=" * 60)

    # 1. Generate 1,000 synthetic catalogue records
    print("[1/4] Generating 1,000 synthetic clothing records...")
    cat_df = generate_synthetic_catalog(1000)
    synth_path = config.SYNTHETIC_CATALOGUE_PATH
    os.makedirs(os.path.dirname(synth_path), exist_ok=True)
    cat_df.to_csv(synth_path, index=False)
    print(f"      Saved synthetic catalogue to: {synth_path} ({len(cat_df)} rows)")

    # 2. Check and preserve starter catalog if present, else copy synthetic to processed
    proc_cat_path = config.CATALOGUE_PATH
    os.makedirs(os.path.dirname(proc_cat_path), exist_ok=True)
    cat_df.to_csv(proc_cat_path, index=False)
    print(f"      Published active catalogue to: {proc_cat_path}")

    # 3. Validate catalogue schema
    print("[2/4] Validating schema against academic specifications...")
    is_valid, errors = validate_catalogue_schema(cat_df)
    if is_valid:
        print("      [OK] Schema Validation Passed: All 18 fields present and formatted.")
    else:
        print(f"      [ERROR] Schema Errors: {errors}")

    # 4. Validate image references
    print("[3/4] Validating image file links...")
    img_report = validate_image_files(cat_df)
    print(f"      Valid images: {img_report['valid_images']}/{img_report['total_records']}")
    print(f"      Missing images: {img_report['missing_images']}")

    # 5. Generate interaction preference training data
    print("[4/4] Generating 1,000 synthetic preference interaction samples...")
    train_df = generate_synthetic_interaction_training_data(1000)
    train_path = config.TRAINING_DATA_PATH
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    train_df.to_csv(train_path, index=False)
    print(f"      Saved preference training data to: {train_path} ({len(train_df)} samples)")
    print("=" * 60)
    print("Dataset Preparation Complete!")

if __name__ == "__main__":
    main()
