# Project 29: Requirements Specification

## 1. Functional Requirements (FR)
- **FR-01 (Skeletal Perception)**: System must extract and track 21 3D hand joints (63 continuous features) matching MediaPipe Hands topology.
- **FR-02 (Multi-Class Recognition)**: System must classify 38 ASL/ISL tokens (12 conversational phrases + 26 alphabet letters A-Z).
- **FR-03 (Top-5 Probabilities)**: Backend must calculate normalized softmax probability distributions and return top-5 candidate rankings.
- **FR-04 (Sentence Assembly)**: Interface must aggregate sequential tokens into fluent phrases with character-level and word-level spacing.
- **FR-05 (Speech Synthesis)**: System must trigger immediate auditory speech output using native text-to-speech engines.
- **FR-06 (Emergency Mode)**: System must recognize high-priority emergency phrases ('HELP', 'EMERGENCY', 'DOCTOR') and trigger immediate acoustic alerts.
- **FR-07 (ACID Persistence)**: All recognized gestures and audio events must be committed to SQLite with WAL mode enabled.

## 2. Non-Functional Requirements (NFR)
- **NFR-01 (Latency)**: End-to-end inference latency must remain below 50ms (PyTorch CPU forward pass $\le 10$ms).
- **NFR-02 (Accuracy)**: Classification accuracy must exceed 90% on held-out test datasets.
- **NFR-03 (Footprint)**: Total model weights must remain under 5 MB on disk, enabling deployment on low-power edge nodes.
- **NFR-04 (Zero Lock Contention)**: SQLite database must operate in WAL mode (`PRAGMA journal_mode=WAL;`).
- **NFR-05 (Accessibility)**: Interface must comply with WCAG 2.1 AA standards for high contrast, keyboard accessibility, and dual visual/audio feedback.
