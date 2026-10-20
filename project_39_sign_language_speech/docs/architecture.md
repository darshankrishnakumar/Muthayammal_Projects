# System Architecture: AI Sign Language Recognition & Speech Synthesis (PROJECT-039)

## 1. System Topology Overview
SIGN-SPEECH AI implements an edge-to-cloud multimodal assistive communication architecture designed for non-verbal and deaf accessibility across healthcare, emergency, and commercial domains.

```
+---------------------------------------------------------------------------------+
|                         OPTICAL SENSING & MESH LAYER                            |
|    [60 FPS RGB Camera]  -->  [MediaPipe 54-D Spatial Skeletal Keypoints]         |
|    - 21 Left Hand Joints   - 21 Right Hand Joints   - 12 Upper Torso Joints     |
+---------------------------------------------------------------------------------+
                                       |
                                       v (30 Frames x 54 Dimensions Normalized Tensor)
+---------------------------------------------------------------------------------+
|                       PYTORCH NEURAL INFERENCE ENGINE                           |
|  +-------------------------------------+   +---------------------------------+  |
|  | BiLSTMSignAttentionNet              |   | SpeechProsodyAcousticRegressor  |  |
|  | - 2-Layer BiLSTM (256 hidden)       |   | - Shared Trunk (LayerNorm+GELU) |  |
|  | - Self-Attention Temporal Pooling   |   | - Multi-Head: Pitch F0, Dur,    |  |
|  | - 10 Standard Classes (100.0% Acc)  |   |   Energy, Prosody Quality Score |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Decoded Gloss, Prosody Parameters, Sentence)
+---------------------------------------------------------------------------------+
|                  CONVERSATIONAL EXPANSION & NEURAL TTS SYNTHESIS                |
|  - HELLO --> "Hello, how can I assist you today?" (Pitch: 185 Hz, Dur: 0.85s)   |
|  - EMERGENCY --> "This is a critical emergency situation..." (Pitch: 245 Hz)    |
|  - DOCTOR --> "Please call a doctor immediately..." (Pitch: 180 Hz, Dur: 1.25s) |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [translation_logs] [vocabulary]                                                |
|  [cryptographic_audit_ledger (SHA-256 Block Chaining)]                          |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5039) & INTERACTIVE HUD                   |
|  - 60 FPS Skeletal Landmark Canvas       - Live Acoustic Waveform Visualizer    |
|  - 10-Gesture Quick Selector Toolbar     - Tamper-Evident Hash Chain Viewer     |
+---------------------------------------------------------------------------------+
```
