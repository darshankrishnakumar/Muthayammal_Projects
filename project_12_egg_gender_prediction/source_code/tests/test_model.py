import os
import sys
import numpy as np
import pytest
from PIL import Image

# Ensure source_code is on path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from egg_engine import EggPredictionEngine

@pytest.fixture
def engine():
    return EggPredictionEngine()

def test_weights_loaded_correctly(engine):
    assert engine.Theta1 is not None
    assert engine.Theta2 is not None
    assert engine.Theta1.shape == (30, 4097)
    assert engine.Theta2.shape == (1, 31)

def test_sigmoid_limits(engine):
    assert np.isclose(engine.sigmoid(0.0), 0.5)
    assert np.isclose(engine.sigmoid(100.0), 1.0)
    assert np.isclose(engine.sigmoid(-100.0), 0.0)

def test_sigmoid_gradient_symmetry(engine):
    grad_zero = engine.sigmoid_gradient(0.0)
    assert np.isclose(grad_zero, 0.25)
    assert np.isclose(engine.sigmoid_gradient(2.0), engine.sigmoid_gradient(-2.0))

def test_load_image_vector_normalization(engine):
    test_img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    vec, gray = engine.load_image_vector(test_img)
    assert vec.shape == (4096,)
    assert 0.0 <= vec.min() <= 1.0
    assert 0.0 <= vec.max() <= 1.0

def test_female_egg_morphology_and_prediction(engine):
    path = os.path.join(BASE_DIR, "grayscale", "F01_standard_female.png")
    assert os.path.exists(path)
    img = Image.open(path)
    res = engine.predict_image(img)
    assert "Female" in res["prediction"]
    assert res["symbol"] == "♀"
    assert res["morphology"]["shape_index"] > 74.0
    assert res["confidence_pct"] > 50.0

def test_male_egg_morphology_and_prediction(engine):
    path = os.path.join(BASE_DIR, "grayscale", "M01_pointed_apex_male.png")
    assert os.path.exists(path)
    img = Image.open(path)
    res = engine.predict_image(img)
    assert "Male" in res["prediction"]
    assert res["symbol"] == "♂"
    assert res["morphology"]["shape_index"] < 74.0
    assert res["confidence_pct"] > 50.0

def test_spherical_hen_egg(engine):
    path = os.path.join(BASE_DIR, "grayscale", "F02_spherical_hen_egg.png")
    img = Image.open(path)
    res = engine.predict_image(img)
    assert "Female" in res["prediction"]
    assert res["morphology"]["roundness"] > 0.5

def test_conical_rooster_egg(engine):
    path = os.path.join(BASE_DIR, "grayscale", "M02_conical_rooster_egg.png")
    img = Image.open(path)
    res = engine.predict_image(img)
    assert "Male" in res["prediction"]
    assert res["morphology"]["apex_sharpness"] > 0.0

def test_all_sample_eggs_evaluation(engine):
    gray_dir = os.path.join(BASE_DIR, "grayscale")
    files = [f for f in sorted(os.listdir(gray_dir)) if f.lower().endswith(('.png', '.jpg'))]
    assert len(files) >= 10
    correct = 0
    for f in files:
        img = Image.open(os.path.join(gray_dir, f))
        res = engine.predict_image(img)
        ground_truth = "Female" if f.startswith("F") else "Male"
        pred = "Female" if "Female" in res["prediction"] else "Male"
        if ground_truth == pred:
            correct += 1
    accuracy = correct / len(files)
    assert accuracy == 1.0  # 100% accuracy on standard calibration dataset
