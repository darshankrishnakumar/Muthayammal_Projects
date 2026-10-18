"""
Standalone CLI Test Script for Egg Prediction Model
Run this script to test individual egg images or the entire evaluation dataset.
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from PIL import Image
from egg_engine import EggPredictionEngine

def test_single_image(image_path):
    print(f"\n==================================================")
    print(f"Testing Single Egg: {os.path.basename(image_path)}")
    print(f"==================================================")
    
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return

    engine = EggPredictionEngine()
    img = Image.open(image_path)
    res = engine.predict_image(img)

    print(f"Prediction         : {res['prediction']} ({res['symbol']})")
    print(f"Confidence         : {res['confidence_pct']}%")
    print(f"Female Probability : {res['female_probability']}%")
    print(f"Male Probability   : {res['male_probability']}%")
    print(f"\n--- Morphological Features ---")
    print(f"Shape Index (SI)   : {res['morphology']['shape_index']}% (Round > 74% / Pointed < 74%)")
    print(f"Elongation         : {res['morphology']['elongation']}")
    print(f"Apex Sharpness     : {res['morphology']['apex_sharpness']}")
    print(f"Asymmetry Index    : {res['morphology']['asymmetry_index']}")
    print(f"Roundness Coeff    : {res['morphology']['roundness']}")
    print(f"\nRecommendation     : {res['recommendation']}\n")

def test_all_samples():
    print(f"\n==================================================")
    print(f"Testing All Dataset Samples (Batch Evaluation)")
    print(f"==================================================")

    engine = EggPredictionEngine()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gray_dir = os.path.join(base_dir, "grayscale")

    if not os.path.exists(gray_dir):
        print(f"Error: Directory {gray_dir} does not exist.")
        return

    files = [f for f in sorted(os.listdir(gray_dir)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        print("No sample images found in grayscale directory.")
        return

    total = len(files)
    correct = 0

    print(f"{'Filename':<30} | {'Truth':<8} | {'Prediction':<15} | {'SI (%)':<7} | {'Conf (%)':<8} | {'Status'}")
    print("-" * 88)

    for fname in files:
        path = os.path.join(gray_dir, fname)
        img = Image.open(path)
        res = engine.predict_image(img)

        ground_truth = "Female" if fname.upper().startswith("F") else "Male"
        predicted = "Female" if "Female" in res["prediction"] else "Male"
        is_match = (ground_truth == predicted)
        if is_match:
            correct += 1

        status = "PASS [OK]" if is_match else "FAIL [X]"
        print(f"{fname:<30} | {ground_truth:<8} | {res['prediction']:<15} | {res['morphology']['shape_index']:<7} | {res['confidence_pct']:<8} | {status}")

    acc = (correct / total) * 100.0
    print("-" * 88)
    print(f"Total Evaluated: {total} | Correct: {correct} | Accuracy: {acc:.1f}%\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_single_image(sys.argv[1])
    else:
        test_all_samples()
