# System Architecture & Technical Design

## 1. High-Level System Architecture

PROJECT-012 provides an industrial-grade automated egg sex determination system utilizing computer vision, geometric morphology analysis, and artificial neural networks.

```
+-----------------------------------------------------------------------------------+
|                            EGG SEX PREDICTION PORTAL                              |
|          Web Interface (Tailwind CSS, FontAwesome, SVG Visual Indicators)         |
+-----------------------------------------------------------------------------------+
                                        |  HTTP/REST (Port 5012)
                                        v
+-----------------------------------------------------------------------------------+
|                         FLASK APPLICATION SERVER (app.py)                         |
|   /api/health | /api/samples | /api/predict | /api/submit_all | /api/history     |
+-----------------------------------------------------------------------------------+
                   |                                             |
                   v                                             v
+---------------------------------------+       +-----------------------------------+
|       EGG PREDICTION ENGINE           |       |      DATABASE SUBSYSTEM           |
|         (egg_engine.py)               |       |         (database.py)             |
|  - Bicubic Image Vectorization        |       |  - SQLite Persistent Storage      |
|  - Morphological Contour Analysis     |       |  - 'egg_predictions' Table        |
|  - Shape Index (SI = B/L * 100)       |       |  - Real-Time Diagnostic Ledger    |
|  - Apex Curvature & Sharpness         |       |  - Aggregate Batch Analytics      |
|  - Neural Network MLP (4096-30-1)     |       +-----------------------------------+
|  - model_weights.npz Serialization    |                         |
+---------------------------------------+                         v
                   |                                    [ egg_history.db ]
                   v
      [ Diagnostic Verdict & Report ]
```

## 2. Component Descriptions

### 2.1 Web UI (templates/index.html)
A modern, responsive user portal built with Tailwind CSS and FontAwesome. Provides:
- Real-time engine health and connection status.
- 10-specimen reference egg gallery with instant 1-click evaluation.
- Drag-and-drop custom image upload with live client preview.
- Dual probability meter displaying comparative Female vs Male percentages.
- Morphological parameter breakdown (Shape Index, Elongation, Apex Sharpness, Asymmetry, Roundness).
- Global batch evaluation modal with comprehensive confusion matrix.
- Persistent SQLite audit history table.

### 2.2 Flask Application Server (app.py)
A lightweight microservice listening on Port 5012. Exposes:
- `GET /api/health`: Service health and database operational statistics.
- `GET /api/samples`: Listing of 10 standard calibration reference eggs.
- `GET /sample_image/<filename>`: Serves high-contrast grayscale specimen images.
- `POST /api/predict`: Evaluates egg specimen (via sample_id or multipart file upload).
- `POST /api/submit_all`: Runs cross-validation across all dataset specimens.
- `GET /api/history`: Returns historical audit logs with limit slicing.
- `GET /api/stats`: Returns aggregated classification statistics.

### 2.3 Neural Engine (egg_engine.py)
Implements:
- 64x64 bicubic image vectorization (4,096-dimensional normalized vector).
- Fully connected MLP (4,096 inputs -> 30 hidden neurons -> 1 output neuron).
- Numerical stability clipping for logistic sigmoid activations.
- Morphological contour detection with axis-aligned bounding geometry.
- Mathematical calculation of Shape Index ($SI = rac{B}{L} 	imes 100$).
- Synthetic egg generator for baseline network training.

### 2.4 Database Subsystem (database.py)
Manages `egg_history.db`:
- Persistent SQLite schema with B-tree indexes on `timestamp` and `predicted_sex`.
- Thread-safe connection pooling and row factory mappings.
- Automatic schema migration and verification.
