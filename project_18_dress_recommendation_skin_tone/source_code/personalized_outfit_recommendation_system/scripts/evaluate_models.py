"""Stage 12: Offline Evaluation & Model Comparison Script."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.evaluation import run_ablation_experiments


def main():
    print("=" * 60)
    print("STAGE 12: MODEL EVALUATION & EXPERIMENTAL COMPARISON")
    print("=" * 60)
    print("Running comparative experiments across recommendation variants:")
    print("  - TF-IDF Only")
    print("  - GBM Only")
    print("  - Rule Engine Only")
    print("  - Hybrid Multi-Modal Ensemble")
    print("...")

    df = run_ablation_experiments(top_k=5)
    print("\nSummary of Comparative Results:")
    summary = df.groupby("model_variant")["mean_top_k_score"].mean().reset_index()
    for _, r in summary.iterrows():
        print(f"  * {r['model_variant']:<20}: Mean Top-5 Score = {r['mean_top_k_score']:.4f}")

    print(f"\nDetailed evaluation report saved to: {config.EXPERIMENT_REPORT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
