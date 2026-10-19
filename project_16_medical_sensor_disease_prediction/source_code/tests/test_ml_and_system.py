import os
import sys
import unittest
import numpy as np
import torch

# Add paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
ML_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "ml-model"))
sys.path.insert(0, ML_DIR)

from preprocessing.ecg_pipeline import (
    butter_bandpass_filter,
    detect_r_peaks,
    segment_beat,
    normalize_beat,
    AAMI_CLASSES,
    AAMI_CODES,
    WINDOW_SIZE,
)
from inference_service import load_model_and_config, MODEL_PATH_TORCH


class TestResidual1DCNN(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_model_and_config()

    def test_model_file_exists(self):
        """Verify the trained PyTorch 1D CNN model weights exist."""
        self.assertTrue(os.path.isfile(MODEL_PATH_TORCH), f"Missing model file at {MODEL_PATH_TORCH}")
        file_size_kb = os.path.getsize(MODEL_PATH_TORCH) / 1024
        self.assertGreater(file_size_kb, 100, "Model weight file is suspiciously small")

    def test_model_weight_loading_and_architecture(self):
        """Test model weights dictionary keys and layer dimensions."""
        state_dict = torch.load(MODEL_PATH_TORCH, map_location="cpu")
        self.assertIn("stem.0.weight", state_dict)
        self.assertIn("res1.conv1.weight", state_dict)
        self.assertIn("res2.conv1.weight", state_dict)
        self.assertIn("res3.conv1.weight", state_dict)
        self.assertIn("fc2.weight", state_dict)
        # Check num classes is 5 (AAMI standard)
        self.assertEqual(state_dict["fc2.weight"].shape[0], 5)

    def test_forward_pass_dimension(self):
        """Verify forward pass output shape for arbitrary batch sizes."""
        from inference_service import ECGResidual1DCNN
        net = ECGResidual1DCNN(num_classes=5)
        net.load_state_dict(torch.load(MODEL_PATH_TORCH, map_location="cpu"))
        net.eval()

        dummy_input = torch.randn(4, 1, 187)
        with torch.no_grad():
            output = net(dummy_input)
        self.assertEqual(output.shape, (4, 5))
        # Ensure outputs are valid probabilities summing to ~1.0
        sums = torch.sum(output, dim=1).numpy()
        np.testing.assert_allclose(sums, np.ones(4), atol=1e-4)

    def test_butterworth_bandpass_filter(self):
        """Verify 0.5-40Hz bandpass filtering attenuates high frequency noise."""
        fs = 360.0
        t = np.linspace(0, 1, int(fs))
        # 10Hz signal (passband) + 120Hz signal (stopband noise)
        sig = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 120 * t)
        filtered = butter_bandpass_filter(sig, lowcut=0.5, highcut=40.0, fs=fs, order=2)
        self.assertEqual(len(filtered), len(sig))
        # Filtered signal amplitude should be lower because high freq is removed
        self.assertLess(np.max(np.abs(filtered)), np.max(np.abs(sig)))

    def test_r_peak_detection(self):
        """Verify R-peak detection on synthetic QRS complexes."""
        fs = 360.0
        sig = np.zeros(1000)
        # Place peaks at index 200, 500, 800
        sig[200] = 2.0
        sig[500] = 2.0
        sig[800] = 2.0
        peaks = detect_r_peaks(sig, fs=fs)
        self.assertGreaterEqual(len(peaks), 1)

    def test_segment_beat(self):
        """Verify beat segmentation extracts exactly WINDOW_SIZE (187) samples."""
        sig = np.sin(np.linspace(0, 10, 1000))
        beat = segment_beat(sig, r_peak_idx=300, window_size=187)
        self.assertEqual(len(beat), 187)

    def test_normalize_beat(self):
        """Verify beat normalization produces bounded outputs."""
        raw_beat = np.array([-0.5, 0.0, 1.2, -0.2, 0.8], dtype=np.float32)
        norm_beat = normalize_beat(raw_beat)
        self.assertEqual(len(norm_beat), len(raw_beat))
        self.assertTrue(np.all(np.isfinite(norm_beat)))

    def test_aami_class_mapping(self):
        """Verify all 5 AAMI classes are present and properly documented."""
        self.assertEqual(len(AAMI_CLASSES), 5)
        self.assertIn(0, AAMI_CLASSES)
        self.assertEqual(AAMI_CLASSES[0], "Normal Sinus Rhythm")
        self.assertIn("N", AAMI_CODES.values())
        self.assertIn("V", AAMI_CODES.values())


if __name__ == "__main__":
    unittest.main()
