"""
Apple Health Intelligence AI - Standalone Apple Leaf Disease Predictor CLI
===========================================================================
Predicts Apple Leaf Pathology:
- Healthy
- Apple_Scab
- Black_Rot
- Cedar_Apple_Rust

Includes:
- Two-stage MobileNetV2 checkpoint inference
- Uncertainty safety rejection (< threshold)
- Full per-class probability distribution
- High-resolution Grad-CAM visual explanation overlay export
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure root & scripts in sys.path
root_dir = Path(__file__).resolve().parent.parent
scripts_dir = Path(__file__).resolve().parent
for p in [str(root_dir), str(scripts_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np

from apple_cnn_engine import get_engine, TaskClassifier

def predict_single_leaf(
    image_path: str,
    checkpoint_path: str = "models/apple_leaf_disease_v1.pth",
    rejection_threshold: float = 0.60,
    save_cam: str = None
):
    img_p = Path(image_path)
    if not img_p.exists():
        raise FileNotFoundError(f"Image not found at: {image_path}")

    # Use unified engine for consistent Grad-CAM and preprocessing
    engine = get_engine()
    img = Image.open(str(img_p)).convert("RGB")
    
    result = engine.predict(img, model_type="transfer", specimen_override="apple_leaf")
    
    print("\n" + "=" * 65)
    print(f" APPLE FOLIAR PATHOLOGY DIAGNOSIS: {img_p.name}")
    print("=" * 65)
    print(f" Predicted Condition: {result['predicted_class']} ({result['display_name']})")
    print(f" Confidence:          {result['confidence']}%")
    print(f" Specimen Detected:   {result['specimen_type']}")
    print(f" Model Architecture:  {result['model_used']}")
    print(f" Severity Level:      {result.get('severity', 'N/A')}")
    print(f" Class Breakdown:     {result['all_probabilities']}")
    
    if result.get("is_uncertain"):
        print(f"\n[!] SAFETY ADVISORY: {result.get('uncertainty_reason')}")
    else:
        print("\n[OK] Prediction confidence meets reliable safety threshold.")

    if save_cam:
        # Save Grad-CAM image
        cam_b64 = result.get("gradcam_image")
        if cam_b64 and "," in cam_b64:
            import base64
            raw_bytes = base64.b64decode(cam_b64.split(",", 1)[1])
            with open(save_cam, "wb") as f:
                f.write(raw_bytes)
            print(f"[OK] Grad-CAM overlay saved to: {save_cam}")

    print("=" * 65)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict Apple Leaf Disease (Healthy, Apple_Scab, Black_Rot, Cedar_Apple_Rust)")
    parser.add_argument("image_path", help="Path to apple leaf photograph")
    parser.add_argument("--checkpoint", default="models/apple_leaf_disease_v1.pth", help="Checkpoint file")
    parser.add_argument("--threshold", type=float, default=0.60, help="Confidence threshold")
    parser.add_argument("--save_cam", default=None, help="Optional output path for Grad-CAM overlay")
    args = parser.parse_args()

    predict_single_leaf(
        image_path=args.image_path,
        checkpoint_path=args.checkpoint,
        rejection_threshold=args.threshold,
        save_cam=args.save_cam
    )
