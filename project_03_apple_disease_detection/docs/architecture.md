# System Architecture & Technical Design

## High-Level Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Client Layer (Browser)                         │
│  - Responsive Diagnostic Portal (Outfit / JetBrains Mono)              │
│  - Tabbed Workflow: Real-Time Diagnosis, CNN Feature Maps, Guide       │
│  - 1-Click Preset Gallery + Direct Camera / File Upload               │
└─────────────────────────────────▲──────────────────────────────────────┘
                                  │ HTTP / JSON (Port 5003)
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Application Gateway (Flask API Layer)                │
│  - Static Asset & Template Serving                                     │
│  - Multipart Form & Base64 Payload Parsers                             │
│  - Endpoints: /health, /api/samples, /api/predict, /api/db/history     │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│        Deep Computer Vision Engine   │ │        Database Subsystem     │
│  - Stage 1: Input Specimen Validator │ │  - SQLite3 Engine             │
│    (apple_leaf, fruit, unsupported)  │ │    (apple_diagnostics.db)     │
│  - Stage 2: Foliar Disease Model     │ │  - Schema: diagnostic_records │
│    (Scab, Black Rot, Rust, Healthy)  │ │  - Audit History & Analytics  │
│  - Stage 3: Fruit Condition Model    │ └───────────────────────────────┘
│    (Fresh vs Rotten)                 │
│  - Grad-CAM Heatmap Generator        │
│  - Agronomic Decision Support        │
└──────────────────────────────────────┘
```

## Data Flow & Processing Pipeline

1. **Image Ingestion**: An apple leaf or fruit image is captured via device camera, uploaded as JPEG/PNG, or selected from the validated preset gallery.
2. **Preprocessing & Tensor Transformation**:
   - Resized to $(224 \times 224)$ pixels.
   - Converted to 3-channel RGB float tensor.
   - Normalized using ImageNet statistics: $\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$.
3. **Stage 1 — Input Specimen Validation**:
   - `apple_input_validator_v1.pth` evaluates whether image represents an apple leaf, apple fruit, or unsupported out-of-distribution noise.
   - If unsupported or entropy exceeds uncertainty threshold, system safely halts and prompts grower to supply clear foliage.
4. **Stage 2 — Adaptive Routing & Deep Inference**:
   - Foliage: Routed to `apple_leaf_disease_v1.pth` (MobileNetV2, 4 classes).
   - Fruit: Routed to `apple_fruit_condition_v1.pth` (MobileNetV2, 2 classes).
   - Softmax layer computes calibrated class probabilities and confidence percentage.
5. **Grad-CAM Visual Saliency Generation**:
   - Gradients of the winning class score $y^c$ are backpropagated to feature maps $A^k$ of the final inverted residual block.
   - Neuron importance weights $a_k^c = \frac{1}{Z} \sum_i \sum_j \frac{\partial y^c}{\partial A_{i,j}^k}$ weight the forward activation maps.
   - Rectified linear combination yields localized 2D heatmap $L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k a_k^c A^k\right)$, blended as an overlay onto original RGB specimen.
6. **Agronomic Decision Support & Remedy Matching**:
   - Pathology matched against agronomic database to prescribe registered active fungicides (with FRAC resistance codes), OMRI-listed organic remedies, and cultural canopy practices.
7. **Transactional Logging**:
   - Diagnosis, timestamp, specimen type, confidence, severity, and uncertainty flags logged transactionally to `apple_diagnostics.db`.
