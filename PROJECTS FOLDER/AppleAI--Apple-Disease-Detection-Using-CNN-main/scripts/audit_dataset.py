"""
Apple Health Intelligence AI - Dataset Audit Engine
===================================================
Inspects raw and prepared datasets to ensure data integrity, prevent leakage,
detect exact/near duplicates, audit dimensions, and export results/dataset_report.json.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image
import numpy as np

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def compute_md5(filepath: Path) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_dhash(img: Image.Image, hash_size: int = 8) -> str:
    """Perceptual difference hash for near-duplicate identification."""
    resized = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized, dtype=np.float32)
    diff = pixels[:, 1:] > pixels[:, :-1]
    return hex(int("".join(["1" if b else "0" for b in diff.flatten()]), 2))[2:].zfill(16)

def verify_single_image(filepath: Path):
    if filepath.suffix.lower() not in SUPPORTED_EXTS:
        return False, f"Unsupported extension: {filepath.suffix}", None, None, None
    try:
        with Image.open(filepath) as img:
            img.verify()
        with Image.open(filepath) as img:
            img.load()
            size = img.size
            mode = img.mode
            dhash = compute_dhash(img)
            return True, "valid", size, mode, dhash
    except Exception as e:
        return False, str(e), None, None, None

def audit_directory(data_dir: Path, min_samples_per_class: int = 15):
    print("=" * 70)
    print(f" AUDITING DATASET: {data_dir.resolve()}")
    print("=" * 70)

    if not data_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {data_dir}")

    class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    if not class_dirs:
        raise ValueError(f"No subdirectories found in {data_dir}. Expected class folders.")

    class_names = sorted([d.name for d in class_dirs])
    print(f"Detected Classes ({len(class_names)}): {class_names}")

    audit_results = {
        "dataset_path": str(data_dir.resolve()),
        "classes": class_names,
        "class_counts": {},
        "valid_samples": [],
        "corrupted_samples": [],
        "exact_duplicates": [],
        "near_duplicates": [],
        "dimension_stats": {},
        "class_balance_ratio": None,
        "is_sufficient": True,
        "sufficiency_notes": []
    }

    seen_md5 = {}
    seen_dhash = {}

    total_valid = 0

    for c_dir in class_dirs:
        c_name = c_dir.name
        image_files = [f for f in c_dir.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS]
        valid_in_class = 0
        widths, heights = [], []

        for f_path in image_files:
            is_valid, msg, size, mode, dh = verify_single_image(f_path)
            if not is_valid:
                audit_results["corrupted_samples"].append({
                    "path": str(f_path),
                    "class": c_name,
                    "reason": msg
                })
                continue

            md5 = compute_md5(f_path)
            if md5 in seen_md5:
                audit_results["exact_duplicates"].append({
                    "path": str(f_path),
                    "duplicate_of": seen_md5[md5],
                    "class": c_name,
                    "md5": md5
                })
                continue

            # Check near-duplicates (identical dhash)
            if dh in seen_dhash:
                audit_results["near_duplicates"].append({
                    "path": str(f_path),
                    "near_duplicate_of": seen_dhash[dh],
                    "class": c_name,
                    "dhash": dh
                })

            seen_md5[md5] = str(f_path)
            seen_dhash[dh] = str(f_path)

            widths.append(size[0])
            heights.append(size[1])
            valid_in_class += 1
            total_valid += 1

            audit_results["valid_samples"].append({
                "path": str(f_path),
                "class": c_name,
                "width": size[0],
                "height": size[1],
                "mode": mode,
                "md5": md5,
                "dhash": dh
            })

        audit_results["class_counts"][c_name] = valid_in_class
        audit_results["dimension_stats"][c_name] = {
            "min_width": min(widths) if widths else 0,
            "max_width": max(widths) if widths else 0,
            "min_height": min(heights) if heights else 0,
            "max_height": max(heights) if heights else 0,
            "avg_width": round(float(np.mean(widths)), 1) if widths else 0,
            "avg_height": round(float(np.mean(heights)), 1) if heights else 0
        }

        if valid_in_class < min_samples_per_class:
            audit_results["is_sufficient"] = False
            audit_results["sufficiency_notes"].append(
                f"Class '{c_name}' has only {valid_in_class} valid images (minimum threshold is {min_samples_per_class})."
            )

    # Class balance check
    counts = list(audit_results["class_counts"].values())
    if len(counts) >= 2 and min(counts) > 0:
        ratio = round(max(counts) / min(counts), 2)
        audit_results["class_balance_ratio"] = ratio
    else:
        audit_results["class_balance_ratio"] = 0.0

    # Summary Display
    print("\n--- AUDIT SUMMARY ---")
    for c_name, cnt in audit_results["class_counts"].items():
        stats = audit_results["dimension_stats"].get(c_name, {})
        print(f"  • {c_name:<12}: {cnt} valid images | Avg Dimensions: {stats.get('avg_width', 0)}x{stats.get('avg_height', 0)}")
    print(f"  Total Valid Unique Images: {total_valid}")
    print(f"  Exact Duplicates Detected: {len(audit_results['exact_duplicates'])}")
    print(f"  Near Duplicates Detected:  {len(audit_results['near_duplicates'])}")
    print(f"  Corrupted/Invalid Files:   {len(audit_results['corrupted_samples'])}")
    print(f"  Class Balance Ratio:       {audit_results['class_balance_ratio']}")
    print(f"  Sufficiency Check:         {'PASSED [OK]' if audit_results['is_sufficient'] else 'FAILED [!] ' + str(audit_results['sufficiency_notes'])}")

    # Save to results/
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    report_file = results_dir / "dataset_report.json"
    with open(report_file, "w") as f:
        json.dump(audit_results, f, indent=2)
    specific_report = results_dir / f"{data_dir.name}_dataset_report.json"
    with open(specific_report, "w") as f:
        json.dump(audit_results, f, indent=2)
    print(f"\n[OK] Dataset audit report saved to: {report_file} and {specific_report}")

    return audit_results

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("datasets/raw/fruit_condition")
    min_thresh = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    res = audit_directory(target, min_thresh)
    if not res["is_sufficient"]:
        sys.exit(1)
