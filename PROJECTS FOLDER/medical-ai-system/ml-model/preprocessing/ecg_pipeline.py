"""
ECG Signal Preprocessing and Beat Segmentation Pipeline.

Implements:
1. Butterworth Bandpass Filtering (0.5 Hz - 45 Hz) to remove baseline wander and HF noise.
2. R-peak detection & beat segmentation (187-sample fixed window).
3. Per-beat amplitude normalization ([0, 1] min-max).
4. Standard AAMI EC57 annotation class mapping (N, S, V, F, Q).
"""

import os
import numpy as np
import scipy.signal as signal

# AAMI EC57 5-Class Categorization
AAMI_CLASSES = {
    0: "Normal Sinus Rhythm",
    1: "Supraventricular Ectopic Beat",
    2: "Ventricular Ectopic Beat",
    3: "Fusion Beat",
    4: "Unknown / Unclassified Beat",
}

AAMI_CODES = {
    0: "N",
    1: "S",
    2: "V",
    3: "F",
    4: "Q",
}

# Mapping PhysioNet annotation symbols to AAMI classes
SYMBOL_TO_AAMI = {
    # N - Normal beat
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,
    # S - Supraventricular ectopic beat
    "A": 1, "a": 1, "J": 1, "S": 1,
    # V - Ventricular ectopic beat
    "V": 2, "E": 2,
    # F - Fusion beat
    "F": 3,
    # Q - Paced / unclassifiable / unknown
    "/": 4, "f": 4, "Q": 4,
}

WINDOW_SIZE = 187
PRE_PEAK = 70
POST_PEAK = WINDOW_SIZE - PRE_PEAK  # 117 samples


def butter_bandpass_filter(data, lowcut=0.5, highcut=45.0, fs=360.0, order=3):
    """
    Apply zero-phase Butterworth bandpass filter to isolate ECG bandwidth (0.5 - 45 Hz).
    Removes baseline wander (< 0.5 Hz) and high-frequency powerline/EMG noise (> 45 Hz).
    """
    nyq = 0.5 * fs
    low = max(0.001, lowcut / nyq)
    high = min(0.999, highcut / nyq)
    b, a = signal.butter(order, [low, high], btype="band")
    return signal.filtfilt(b, a, data)


def normalize_beat(beat):
    """
    Min-Max normalize a single ECG beat segment to [0, 1].
    Guards against division by zero for flat segments.
    """
    beat = np.asarray(beat, dtype=np.float32)
    b_min = np.min(beat)
    b_max = np.max(beat)
    diff = b_max - b_min
    if diff > 1e-6:
        return (beat - b_min) / diff
    return np.zeros_like(beat)


def detect_r_peaks(ecg_signal, fs=360.0):
    """
    Detect R-peaks from single-lead ECG signal using bandpass filtering,
    squaring, and prominence-based peak finding.
    """
    # 1. Bandpass filter
    filtered = butter_bandpass_filter(ecg_signal, lowcut=1.0, highcut=35.0, fs=fs, order=2)
    
    # 2. Derivative & square to accentuate QRS complex
    diff = np.diff(filtered, prepend=filtered[0])
    squared = diff ** 2

    # 3. Moving average integration
    win_len = int(0.12 * fs)  # 120ms window
    kernel = np.ones(win_len) / win_len
    integrated = np.convolve(squared, kernel, mode="same")

    # 4. Find peaks with minimum distance (~250ms = 240 BPM max)
    min_dist = int(0.25 * fs)
    prominence = np.mean(integrated) + 0.5 * np.std(integrated)
    peaks, _ = signal.find_peaks(integrated, distance=min_dist, prominence=prominence)

    # Refine to local maximum in original filtered signal
    refined = []
    search_radius = int(0.06 * fs)
    sig_len = len(ecg_signal)
    for p in peaks:
        left = max(0, p - search_radius)
        right = min(sig_len, p + search_radius + 1)
        local_max = left + np.argmax(ecg_signal[left:right])
        refined.append(local_max)

    return np.array(refined, dtype=int)


def segment_beat(ecg_signal, r_peak_idx, window_size=WINDOW_SIZE, pre_peak=PRE_PEAK):
    """
    Extract a fixed-length beat window around an R-peak index with padding if near boundaries.
    """
    sig_len = len(ecg_signal)
    start = r_peak_idx - pre_peak
    end = start + window_size

    if start >= 0 and end <= sig_len:
        beat = ecg_signal[start:end]
    else:
        # Pad with boundary reflection or zeros
        beat = np.zeros(window_size, dtype=np.float32)
        v_start = max(0, start)
        v_end = min(sig_len, end)
        b_offset = v_start - start
        b_len = v_end - v_start
        beat[b_offset : b_offset + b_len] = ecg_signal[v_start:v_end]

    return normalize_beat(beat)


def extract_beats_from_record(record_path, channel=0):
    """
    Extract annotated beats from a WFDB MIT-BIH recording (.dat, .hea, .atr).
    Returns list of (beat_array, aami_class_int).
    """
    import wfdb

    rec = wfdb.rdrecord(record_path)
    ann = wfdb.rdann(record_path, "atr")

    sig = rec.p_signal[:, channel]
    fs = rec.fs

    # Filter signal
    filtered_sig = butter_bandpass_filter(sig, fs=fs)

    beats = []
    labels = []

    for idx, sym in zip(ann.sample, ann.symbol):
        if sym in SYMBOL_TO_AAMI:
            aami_class = SYMBOL_TO_AAMI[sym]
            beat = segment_beat(filtered_sig, idx)
            beats.append(beat)
            labels.append(aami_class)

    return np.array(beats, dtype=np.float32), np.array(labels, dtype=np.int32)
