"""
Entry point to train Model B: Apple Leaf Disease Classifier (Healthy, Apple_Scab, Black_Rot, Cedar_Apple_Rust)
"""
import os
import sys
from pathlib import Path
import argparse

root_dir = Path(__file__).resolve().parent.parent
scripts_dir = Path(__file__).resolve().parent
for p in [str(root_dir), str(scripts_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from train_model import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Apple Leaf Disease Classifier")
    parser.add_argument("--data_dir", default="datasets/processed/leaf_disease", help="Dataset directory")
    parser.add_argument("--output_dir", default="models", help="Model checkpoint directory")
    parser.add_argument("--epochs_head", type=int, default=5, help="Head training epochs")
    parser.add_argument("--epochs_fine", type=int, default=5, help="Backbone fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    run_pipeline(
        task_name="leaf_disease",
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs_head=args.epochs_head,
        epochs_fine=args.epochs_fine,
        batch_size=args.batch_size
    )
