"""
Apple Health Intelligence AI - Dataset Preparation Engine
==========================================================
Audits, deduplicates, and generates stratified 70% Train, 15% Val, 15% Test splits
for Fruit Condition (Fresh vs Rotten), Leaf Disease, and Input Validator tasks.
Generates complete manifest and dataset_summary.json.
"""

import os
import sys
import json
import hashlib
import shutil
import random
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

SUPPORTED_EXTS = {"*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.JPG", "*.JPEG", "*.PNG"}

def compute_file_hash(filepath: str, block_size: int = 65536) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            hasher.update(block)
    return hasher.hexdigest()

def verify_image(filepath: str):
    try:
        with Image.open(filepath) as img:
            img.verify()
        with Image.open(filepath) as img:
            img.load()
            size = img.size
        return True, "valid", size
    except Exception as e:
        return False, str(e), None

class DatasetPreparer:
    def __init__(self, raw_dir: str = "datasets/raw", processed_dir: str = "datasets/processed", seed: int = 42):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def scan_and_clean_class(self, class_dir: Path) -> dict:
        valid_files = []
        corrupted_files = []
        duplicates = []
        seen_hashes = {}
        sizes = []

        if not class_dir.exists():
            return {"valid": [], "corrupted": [], "duplicates": [], "stats": {"count": 0}}

        for ext in SUPPORTED_EXTS:
            for file_path in class_dir.glob(ext):
                p_str = str(file_path)
                is_valid, err_msg, size = verify_image(p_str)
                if not is_valid:
                    corrupted_files.append({"path": p_str, "error": err_msg})
                    continue

                f_hash = compute_file_hash(p_str)
                if f_hash in seen_hashes:
                    duplicates.append({"path": p_str, "duplicate_of": seen_hashes[f_hash], "hash": f_hash})
                    continue

                seen_hashes[f_hash] = p_str
                valid_files.append(file_path)
                if size:
                    sizes.append(size)

        return {
            "valid": valid_files,
            "corrupted": corrupted_files,
            "duplicates": duplicates,
            "stats": {
                "count": len(valid_files),
                "corrupted_count": len(corrupted_files),
                "duplicate_count": len(duplicates),
                "avg_width": sum(s[0] for s in sizes) / len(sizes) if sizes else 0,
                "avg_height": sum(s[1] for s in sizes) / len(sizes) if sizes else 0
            }
        }

    def split_data(self, files: list, train_ratio: float = 0.70, val_ratio: float = 0.15):
        shuffled = sorted(files.copy(), key=lambda x: x.name)
        rng = random.Random(self.seed)
        rng.shuffle(shuffled)
        n = len(shuffled)

        if n == 1:
            return shuffled, [], shuffled
        elif n == 2:
            return [shuffled[0]], [shuffled[1]], [shuffled[1]]

        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio)) if n > 3 else 0

        train = shuffled[:n_train]
        val = shuffled[n_train:n_train + n_val]
        test = shuffled[n_train + n_val:]
        if not test:
            test = val if val else train
        return train, val, test

    def prepare_task(self, task_name: str, class_mappings: dict, train_ratio: float = 0.70, val_ratio: float = 0.15) -> dict:
        task_out = self.processed_dir / task_name
        
        # Clean target split folders to prevent leftover files across runs
        if task_out.exists():
            shutil.rmtree(task_out)

        task_summary = {
            "task_name": task_name,
            "classes": list(class_mappings.keys()),
            "splits": {"train": {}, "val": {}, "test": {}},
            "totals": {},
            "audit": {},
            "manifest": []
        }

        for split in ["train", "val", "test"]:
            for cls_name in class_mappings.keys():
                (task_out / split / cls_name).mkdir(parents=True, exist_ok=True)

        for cls_name, src_dirs in class_mappings.items():
            all_valid_files = []
            cls_corrupt = []
            cls_dup = []

            for s_dir in src_dirs:
                res = self.scan_and_clean_class(Path(s_dir))
                all_valid_files.extend(res["valid"])
                cls_corrupt.extend(res["corrupted"])
                cls_dup.extend(res["duplicates"])

            # Deduplicate across multiple source dirs if any
            unique_files = []
            seen_hashes = set()
            for f in all_valid_files:
                h = compute_file_hash(str(f))
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    unique_files.append(f)
                else:
                    cls_dup.append({"path": str(f), "hash": h})

            task_summary["audit"][cls_name] = {
                "valid_total": len(unique_files),
                "corrupted_detected": len(cls_corrupt),
                "duplicates_removed": len(cls_dup)
            }
            task_summary["totals"][cls_name] = len(unique_files)

            if unique_files:
                train_files, val_files, test_files = self.split_data(unique_files, train_ratio, val_ratio)
            else:
                train_files, val_files, test_files = [], [], []

            task_summary["splits"]["train"][cls_name] = len(train_files)
            task_summary["splits"]["val"][cls_name] = len(val_files)
            task_summary["splits"]["test"][cls_name] = len(test_files)

            # Copy files to destination splits and record manifest
            for split_name, flist in [("train", train_files), ("val", val_files), ("test", test_files)]:
                dest_dir = task_out / split_name / cls_name
                for f in flist:
                    dest_file = dest_dir / f.name
                    shutil.copy2(f, dest_file)
                    task_summary["manifest"].append({
                        "task": task_name,
                        "class": cls_name,
                        "split": split_name,
                        "filename": f.name,
                        "original_path": str(f),
                        "processed_path": str(dest_file),
                        "md5": compute_file_hash(str(dest_file))
                    })

        report_path = task_out / "dataset_summary.json"
        with open(report_path, "w") as rf:
            json.dump(task_summary, rf, indent=2)

        manifest_path = task_out / "manifest.json"
        with open(manifest_path, "w") as mf:
            json.dump(task_summary["manifest"], mf, indent=2)

        print(f"[+] Prepared task {task_name}:")
        print(f"    Train: {task_summary['splits']['train']}")
        print(f"    Val:   {task_summary['splits']['val']}")
        print(f"    Test:  {task_summary['splits']['test']}")
        print(f"    Summary: {report_path}")
        return task_summary

    def setup_demo_environment(self):
        demo_dir = self.raw_dir / "demo_reference"
        demo_dir.mkdir(parents=True, exist_ok=True)
        fruit_fresh = demo_dir / "fruit" / "fresh"
        fruit_rot = demo_dir / "fruit" / "rotten"
        fruit_fresh.mkdir(parents=True, exist_ok=True)
        fruit_rot.mkdir(parents=True, exist_ok=True)
        
        leaf_healthy = demo_dir / "leaf" / "healthy"
        leaf_scab = demo_dir / "leaf" / "scab"
        leaf_rot = demo_dir / "leaf" / "black_rot"
        leaf_rust = demo_dir / "leaf" / "cedar_rust"
        for p in [leaf_healthy, leaf_scab, leaf_rot, leaf_rust]:
            p.mkdir(parents=True, exist_ok=True)

        val_fruit = demo_dir / "validator" / "apple_fruit"
        val_leaf = demo_dir / "validator" / "apple_leaf"
        val_unrelated = demo_dir / "validator" / "unsupported"
        for p in [val_fruit, val_leaf, val_unrelated]:
            p.mkdir(parents=True, exist_ok=True)

        unsupported_img_path = val_unrelated / "unsupported_benchmark.jpg"
        if not unsupported_img_path.exists():
            arr = np.zeros((224, 224, 3), dtype=np.uint8)
            arr[::16, :] = 200
            arr[:, ::16] = 200
            Image.fromarray(arr).save(str(unsupported_img_path), "JPEG")

        samples = Path("sample_images")
        if samples.exists():
            mapping = {
                "normal_apple_sample.jpg": [fruit_fresh, val_fruit],
                "rot_apple_sample.jpg": [fruit_rot, val_fruit],
                "scab_apple_sample.jpg": [val_fruit],
                "blotch_apple_sample.jpg": [val_fruit],
                "healthy_leaf_sample.jpg": [leaf_healthy, val_leaf],
                "scab_leaf_sample.jpg": [leaf_scab, val_leaf],
                "black_rot_leaf_sample.jpg": [leaf_rot, val_leaf],
                "cedar_rust_sample.jpg": [leaf_rust, val_leaf]
            }
            for fname, targets in mapping.items():
                src = samples / fname
                if src.exists():
                    for t in targets:
                        shutil.copy2(src, t / fname)

        return demo_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare and split Apple AI datasets")
    parser.add_argument("--raw_dir", default="datasets/raw", help="Path to raw datasets")
    parser.add_argument("--processed_dir", default="datasets/processed", help="Path to processed splits")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splitting")
    args = parser.parse_args()

    preparer = DatasetPreparer(args.raw_dir, args.processed_dir, args.seed)
    preparer.setup_demo_environment()

    # Fruit Condition Task Mapping: incorporates raw fruit_condition and demo references
    fruit_mappings = {
        "Fresh": [
            Path(args.raw_dir) / "fruit_condition" / "Fresh",
            Path(args.raw_dir) / "fruit_and_vegetable_disease" / "dataset" / "train" / "freshapples",
            Path(args.raw_dir) / "demo_reference" / "fruit" / "fresh"
        ],
        "Rotten": [
            Path(args.raw_dir) / "fruit_condition" / "Rotten",
            Path(args.raw_dir) / "fruit_and_vegetable_disease" / "dataset" / "train" / "rottenapples",
            Path(args.raw_dir) / "demo_reference" / "fruit" / "rotten"
        ]
    }
    preparer.prepare_task("fruit_condition", fruit_mappings)

    # Leaf Disease Task Mapping (PlantVillage & Raw Leaf Disease)
    leaf_mappings = {
        "Healthy": [
            Path(args.raw_dir) / "leaf_disease" / "Healthy",
            Path(args.raw_dir) / "plantvillage_apple_leaf" / "Apple___healthy",
            Path(args.raw_dir) / "demo_reference" / "leaf" / "healthy"
        ],
        "Apple_Scab": [
            Path(args.raw_dir) / "leaf_disease" / "Apple_Scab",
            Path(args.raw_dir) / "plantvillage_apple_leaf" / "Apple___Apple_scab",
            Path(args.raw_dir) / "demo_reference" / "leaf" / "scab"
        ],
        "Black_Rot": [
            Path(args.raw_dir) / "leaf_disease" / "Black_Rot",
            Path(args.raw_dir) / "plantvillage_apple_leaf" / "Apple___Black_rot",
            Path(args.raw_dir) / "demo_reference" / "leaf" / "black_rot"
        ],
        "Cedar_Apple_Rust": [
            Path(args.raw_dir) / "leaf_disease" / "Cedar_Apple_Rust",
            Path(args.raw_dir) / "plantvillage_apple_leaf" / "Apple___Cedar_apple_rust",
            Path(args.raw_dir) / "demo_reference" / "leaf" / "cedar_rust"
        ]
    }
    preparer.prepare_task("leaf_disease", leaf_mappings)

    # Input Validator Task Mapping (preserved)
    validator_mappings = {
        "apple_fruit": [Path(args.raw_dir) / "demo_reference" / "validator" / "apple_fruit"],
        "apple_leaf": [Path(args.raw_dir) / "demo_reference" / "validator" / "apple_leaf"],
        "unsupported": [Path(args.raw_dir) / "demo_reference" / "validator" / "unsupported"]
    }
    preparer.prepare_task("input_validator", validator_mappings)
