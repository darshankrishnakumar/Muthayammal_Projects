"""
Entry point to train Model C: Apple Input Validator (apple_fruit, apple_leaf, unsupported)
"""
import argparse
from train_model import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Apple Input Validator (Fruit vs Leaf vs Unsupported)")
    parser.add_argument("--data_dir", default="datasets/processed/input_validator", help="Dataset directory")
    parser.add_argument("--output_dir", default="models", help="Model checkpoint directory")
    parser.add_argument("--epochs_head", type=int, default=5, help="Head training epochs")
    parser.add_argument("--epochs_fine", type=int, default=5, help="Backbone fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    run_pipeline(
        task_name="input_validator",
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs_head=args.epochs_head,
        epochs_fine=args.epochs_fine,
        batch_size=args.batch_size
    )
