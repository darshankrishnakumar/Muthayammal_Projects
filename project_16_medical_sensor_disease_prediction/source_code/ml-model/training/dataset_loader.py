"""
Patient-Stratified MIT-BIH Dataset Loader with Minority Augmentation.

Strictly splits patients/recordings into two independent groups (DS1 vs DS2)
to guarantee zero data leakage between training and testing sets.
(AAMI / de Chazal standard inter-patient division)
"""

import os
import sys
import numpy as np

# Ensure preprocessing module is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from preprocessing.ecg_pipeline import extract_beats_from_record, AAMI_CLASSES, WINDOW_SIZE

# Standard AAMI Patient Division to prevent cross-patient data leakage
DS1_TRAIN_RECORDS = [
    "101", "106", "108", "109", "112", "114", "115", "116", "118", "119",
    "122", "124", "201", "203", "205", "207", "208", "209", "215", "220",
    "223", "230"
]

DS2_TEST_RECORDS = [
    "100", "103", "105", "111", "113", "117", "121", "123", "200", "202",
    "210", "212", "213", "214", "219", "221", "222", "228", "231", "232",
    "233", "234"
]


def load_partition_beats(record_ids, dataset_dir, max_beats_per_record=None):
    """
    Load all beats from a designated partition of MIT-BIH recordings.
    """
    all_beats = []
    all_labels = []

    for r_id in record_ids:
        rec_path = os.path.join(dataset_dir, r_id)
        if not os.path.exists(f"{rec_path}.dat") or not os.path.exists(f"{rec_path}.atr"):
            continue

        beats, labels = extract_beats_from_record(rec_path)
        if len(beats) == 0:
            continue

        if max_beats_per_record is not None and len(beats) > max_beats_per_record:
            indices = np.random.choice(len(beats), max_beats_per_record, replace=False)
            beats = beats[indices]
            labels = labels[indices]

        all_beats.append(beats)
        all_labels.append(labels)

    if not all_beats:
        return np.empty((0, WINDOW_SIZE), dtype=np.float32), np.empty((0,), dtype=np.int32)

    X = np.concatenate(all_beats, axis=0)
    y = np.concatenate(all_labels, axis=0)
    return X, y


def augment_beat(beat):
    """
    Apply physiological signal augmentations: time shift, amplitude jitter, and Gaussian noise.
    """
    aug = beat.copy()
    # Random shift (+/- 3 samples)
    shift = np.random.randint(-3, 4)
    if shift != 0:
        aug = np.roll(aug, shift)
        if shift > 0:
            aug[:shift] = aug[shift]
        else:
            aug[shift:] = aug[shift - 1]

    # Random amplitude scaling (0.92 to 1.08)
    scale = np.random.uniform(0.92, 1.08)
    aug = aug * scale

    # Subtle Gaussian noise (sigma = 0.015)
    noise = np.random.normal(0, 0.015, size=aug.shape)
    aug = aug + noise

    # Clip to [0, 1]
    return np.clip(aug, 0.0, 1.0).astype(np.float32)


def augment_minority_classes(X, y, target_per_class=3500):
    """
    Augment training samples of minority arrhythmia classes (S, V, F, Q)
    strictly within the DS1 training partition.
    """
    aug_X = [X]
    aug_y = [y]

    for c in range(1, 5):
        c_indices = np.where(y == c)[0]
        c_count = len(c_indices)
        if c_count == 0:
            continue

        needed = max(0, target_per_class - c_count)
        if needed > 0:
            # Resample and augment
            sample_from = np.random.choice(c_indices, needed, replace=True)
            new_beats = [augment_beat(X[i]) for i in sample_from]
            aug_X.append(np.array(new_beats, dtype=np.float32))
            aug_y.append(np.full(needed, c, dtype=np.int32))

    X_balanced = np.concatenate(aug_X, axis=0)
    y_balanced = np.concatenate(aug_y, axis=0)

    perm = np.random.permutation(len(X_balanced))
    return X_balanced[perm], y_balanced[perm]


def load_dataset(dataset_dir, max_normal_ratio=2.5, random_state=42):
    """
    Load training, validation, and test datasets with patient segregation.
    Applies minority class augmentation strictly on training split to improve weak-class recall.
    """
    np.random.seed(random_state)
    print(f"Loading DS1 (Train/Val) records: {len(DS1_TRAIN_RECORDS)} patients...")
    X_ds1, y_ds1 = load_partition_beats(DS1_TRAIN_RECORDS, dataset_dir)
    print(f"Loaded {len(X_ds1)} raw beats from DS1.")

    print(f"Loading DS2 (Test) records: {len(DS2_TEST_RECORDS)} patients...")
    X_test, y_test = load_partition_beats(DS2_TEST_RECORDS, dataset_dir)
    print(f"Loaded {len(X_test)} raw beats from DS2 (Test set).")

    # Downsample majority Normal class in DS1
    ectopic_count = int(np.sum(y_ds1 > 0))
    normal_indices = np.where(y_ds1 == 0)[0]
    ectopic_indices = np.where(y_ds1 > 0)[0]

    max_normals = min(len(normal_indices), int(ectopic_count * max_normal_ratio) + 2000)
    selected_normals = np.random.choice(normal_indices, max_normals, replace=False)

    keep_train_idx = np.concatenate([selected_normals, ectopic_indices])
    np.random.shuffle(keep_train_idx)

    X_train_full = X_ds1[keep_train_idx]
    y_train_full = y_ds1[keep_train_idx]

    # Split DS1 into 85% Train and 15% Validation BEFORE augmentation
    num_samples = len(X_train_full)
    indices = np.arange(num_samples)
    np.random.shuffle(indices)

    val_split = int(0.15 * num_samples)
    val_idx = indices[:val_split]
    train_idx = indices[val_split:]

    X_train_raw = X_train_full[train_idx]
    y_train_raw = y_train_full[train_idx]
    X_val = X_train_full[val_idx]
    y_val = y_train_full[val_idx]

    # Augment ONLY the training set to boost weak classes (S, V, F, Q)
    print(f"Augmenting minority classes in training set...")
    X_train, y_train = augment_minority_classes(X_train_raw, y_train_raw, target_per_class=3500)

    # Add channel dimension: (N, 187, 1)
    X_train = np.expand_dims(X_train, axis=-1)
    X_val = np.expand_dims(X_val, axis=-1)
    X_test = np.expand_dims(X_test, axis=-1)

    print("--------------------------------------------------")
    print(f"Train set:      {X_train.shape} | Labels dist: {np.bincount(y_train, minlength=5)}")
    print(f"Validation set: {X_val.shape}   | Labels dist: {np.bincount(y_val, minlength=5)}")
    print(f"Test set:       {X_test.shape}  | Labels dist: {np.bincount(y_test, minlength=5)}")
    print("--------------------------------------------------")

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)
