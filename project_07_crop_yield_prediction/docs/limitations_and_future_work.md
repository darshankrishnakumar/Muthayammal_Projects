# Limitations and Future Work: Crop Yield Prediction System (PROJECT-007)

## 1. Current Limitations

### 1.1 Temporal Granularity of Historical Climate Data
The historical training corpus is compiled at annual resolution (average annual rainfall, average annual temperature, total annual pesticide usage). While this enables macro-level regional forecasting across decades (1990–2013), it does not account for acute within-season micro-climatic events, such as mid-season flash droughts, late-spring frost events, or torrential harvest-window rainfall.

### 1.2 Soil Physicochemical Properties
The current FAO dataset tracks environmental variables (precipitation, temperature) and agrochemical interventions (pesticides, tonnes) but lacks fine-grained pedological attributes such as soil pH, organic matter percentage, cation exchange capacity (CEC), and nitrogen-phosphorus-potassium (NPK) ratios. These factors are currently captured indirectly through geographic area one-hot indicators.

### 1.3 Static Agrochemical Representation
Pesticide volume is recorded as total tonnes per country per year rather than per-hectare application density or specific chemical compound class (e.g., organophosphates, neonicotinoids, glyphosates), limiting toxicological and chemical-specific yield impact analysis.

## 2. Future Work & Enhancements

### 2.1 Satellite Remote Sensing & Vegetation Indices
Integrate multi-spectral satellite imagery streams (Sentinel-2, Landsat-8) to compute real-time Normalized Difference Vegetation Index (NDVI), Enhanced Vegetation Index (EVI), and Land Surface Temperature (LST) at 10-meter spatial resolution.

### 2.2 Deep Spatio-Temporal Modeling
Migrate from ensemble decision trees to hybrid Spatio-Temporal Graph Neural Networks (ST-GNNs) or Convolutional LSTM architectures to capture continuous cross-border climate teleconnections and temporal decay dynamics.

### 2.3 Edge Deployment & Offline PWA
Package lightweight quantized ONNX models for mobile edge deployment, enabling smallholder farmers in remote agrarian communities with limited internet connectivity to run offline crop assessments on Android smartphones.
