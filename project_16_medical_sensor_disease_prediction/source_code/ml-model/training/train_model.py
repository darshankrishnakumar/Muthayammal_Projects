"""
Enhanced 1D CNN Arrhythmia Classifier Training with Residual Connections
and Weak-Class Performance Optimization.

Trains a Residual 1D CNN on MIT-BIH dataset with inter-patient segregation.
Saves model to ml-model/saved-model/ecg_cnn.keras and preprocessing config.
"""

import os
import sys
import json
import time
import numpy as np
import tensorflow as tf

# Add root directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from training.dataset_loader import load_dataset
from preprocessing.ecg_pipeline import AAMI_CLASSES, AAMI_CODES, WINDOW_SIZE


def build_residual_1d_cnn(input_shape=(WINDOW_SIZE, 1), num_classes=5):
    """
    Constructs a Residual 1D CNN tailored for ECG beat classification.
    Skip connections preserve morphological high-frequency gradients (QRS complexes)
    while deeper layers capture temporal rhythm patterns.
    """
    inputs = tf.keras.layers.Input(shape=input_shape)

    # Initial Stem Convolution
    x = tf.keras.layers.Conv1D(filters=32, kernel_size=7, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)

    # Residual Block 1 (32 filters)
    res1 = x
    x = tf.keras.layers.Conv1D(filters=32, kernel_size=5, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv1D(filters=32, kernel_size=5, padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.add([x, res1])
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling1D(pool_size=2)(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    # Residual Block 2 (64 filters)
    res2 = tf.keras.layers.Conv1D(filters=64, kernel_size=1, padding="same")(x)
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=5, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.add([x, res2])
    x = tf.keras.layers.Activation("relu")(x)
    x = tf.keras.layers.MaxPooling1D(pool_size=2)(x)
    x = tf.keras.layers.Dropout(0.2)(x)

    # Residual Block 3 (128 filters)
    res3 = tf.keras.layers.Conv1D(filters=128, kernel_size=1, padding="same")(x)
    x = tf.keras.layers.Conv1D(filters=128, kernel_size=3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv1D(filters=128, kernel_size=3, padding="same")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.add([x, res3])
    x = tf.keras.layers.Activation("relu")(x)

    # Global Average Pooling & Dense Head
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    x = tf.keras.layers.Dense(units=64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(units=num_classes, activation="softmax", name="output_probabilities")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="residual_1d_cnn_ecg")
    return model


def train_and_export():
    start_time = time.time()
    dataset_dir = os.path.join(PROJECT_ROOT, "dataset", "mit-bih")
    saved_model_dir = os.path.join(PROJECT_ROOT, "saved-model")
    evaluation_dir = os.path.join(PROJECT_ROOT, "evaluation")
    os.makedirs(saved_model_dir, exist_ok=True)
    os.makedirs(evaluation_dir, exist_ok=True)

    print("=" * 80)
    print("Enhanced 1D CNN Arrhythmia Classifier Training")
    print("=" * 80)
    print(f"Dataset directory:   {dataset_dir}")
    print(f"Model output path:   {os.path.join(saved_model_dir, 'ecg_cnn.keras')}")
    print(f"Window length:       {WINDOW_SIZE} samples")
    print(f"AAMI Target Classes: {AAMI_CLASSES}")
    print("=" * 80)

    # 1. Load patient-stratified data with minority augmentation
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_dataset(dataset_dir)

    # 2. Compute square-root smoothed class weights (prevents loss explosion on rare classes)
    counts = np.bincount(y_train, minlength=5)
    total_samples = len(y_train)
    smoothed_weights = (total_samples / (5.0 * np.maximum(counts, 1))) ** 0.5
    smoothed_weights = np.clip(smoothed_weights, 0.5, 3.5)
    class_weight_dict = {int(i): float(round(smoothed_weights[i], 3)) for i in range(5)}
    print(f"Class Counts:           {counts}")
    print(f"Smoothed Class Weights: {class_weight_dict}")

    # 3. Build Residual 1D CNN Model
    model = build_residual_1d_cnn(input_shape=(WINDOW_SIZE, 1), num_classes=5)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    model.summary()

    # 4. Callbacks
    model_save_path = os.path.join(saved_model_dir, "ecg_cnn.keras")
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-5,
            verbose=1
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_save_path,
            monitor="val_loss",
            save_best_only=True,
            verbose=1
        )
    ]

    # 5. Train Model
    print("\nStarting Residual 1D CNN training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=16,
        batch_size=64,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1
    )

    # Save final model explicitly
    model.save(model_save_path)
    print(f"\n[OK] Model saved successfully to: {model_save_path}")

    # 6. Save Preprocessing & Model Configuration
    config = {
        "model_name": "Residual 1D CNN Arrhythmia Classifier",
        "model_version": "1.1.0",
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "architecture": "Residual 1D CNN (3 ResNet Blocks, BatchNorm, GlobalAvgPool, Dense)",
        "input_shape": [WINDOW_SIZE, 1],
        "sampling_rate_hz": 360,
        "classes": {str(k): {"code": AAMI_CODES[k], "name": AAMI_CLASSES[k]} for k in AAMI_CLASSES},
        "normalization": "min_max_[0,1]",
        "filter": {
            "type": "butterworth_bandpass",
            "lowcut_hz": 0.5,
            "highcut_hz": 45.0,
            "order": 3
        },
        "train_samples": int(len(X_train)),
        "val_samples": int(len(X_val)),
        "test_samples": int(len(X_test)),
        "class_weights": class_weight_dict
    }

    config_path = os.path.join(saved_model_dir, "preprocessing_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print(f"[OK] Preprocessing configuration saved to: {config_path}")

    # 7. Evaluate on Independent DS2 Test Set
    print("\nEvaluating model on independent patient test set (DS2)...")
    from evaluation.evaluate_model import evaluate_predictions
    y_pred_probs = model.predict(X_test, batch_size=128)
    y_pred = np.argmax(y_pred_probs, axis=1)

    eval_results = evaluate_predictions(y_test, y_pred, y_pred_probs, evaluation_dir)

    total_time = time.time() - start_time
    print(f"\n[COMPLETE] Model training and evaluation finished in {total_time:.1f} seconds.")
    return eval_results


if __name__ == "__main__":
    train_and_export()
