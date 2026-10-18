import sys

print("==================================================")
print("MACHINE LEARNING ENVIRONMENT VERIFICATION")
print("==================================================")
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version.split()[0]}")
print("--------------------------------------------------")

# Import tests & version printing
print("Testing individual package imports...")

import numpy as np
print(f"[OK] numpy: {np.__version__}")

import pandas as pd
print(f"[OK] pandas: {pd.__version__}")

import scipy
print(f"[OK] scipy: {scipy.__version__}")

import sklearn
print(f"[OK] scikit-learn: {sklearn.__version__}")

import matplotlib
print(f"[OK] matplotlib: {matplotlib.__version__}")

import seaborn as sns
print(f"[OK] seaborn: {sns.__version__}")

import wfdb
print(f"[OK] wfdb: {wfdb.__version__}")

import tensorflow as tf
print(f"[OK] tensorflow: {tf.__version__}")

print("--------------------------------------------------")
print("Executing TensorFlow Tensor & 1D CNN Test...")

# 1. Create a small sample tensor and execute basic operation
t1 = tf.constant([[1.0, 2.0], [3.0, 4.0]], dtype=tf.float32)
t2 = tf.constant([[0.5, 0.5], [1.0, 1.0]], dtype=tf.float32)
t_add = tf.add(t1, t2)
print(f"[OK] Tensor operation (add) passed. Result shape: {t_add.shape}")

# 2. Build a test 1D CNN using Keras
# Dummy shape for testing: (batch_size=2, sequence_length=187, channels=1)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(187, 1)),
    tf.keras.layers.Conv1D(filters=16, kernel_size=5, activation='relu', padding='same'),
    tf.keras.layers.MaxPooling1D(pool_size=2),
    tf.keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same'),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(units=5, activation='softmax')  # 5 classes for testing dummy output
])

# 3. Run one forward pass using dummy numerical input for software installation verification only
dummy_input = np.random.randn(2, 187, 1).astype(np.float32)
output = model(dummy_input)

print(f"[OK] Test 1D CNN forward pass passed.")
print(f"     Input shape:  {dummy_input.shape}")
print(f"     Output shape: {output.shape}")
assert output.shape == (2, 5), f"Unexpected output shape: {output.shape}"

print("--------------------------------------------------")
print("ALL MACHINE LEARNING ENVIRONMENT CHECKS PASSED!")
print("==================================================")
