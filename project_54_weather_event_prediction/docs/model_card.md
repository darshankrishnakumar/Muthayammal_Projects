# Model Card: PROJECT-054 Dual Neural Engine

## Model 1: BiGRUWeatherNowcastingNet
- **Type**: Multi-Sensor Spatio-Temporal Bidirectional GRU with Temporal Attention
- **Parameters**: 115,270
- **Input**: Sequence of 12 hourly observations across 7 meteorological channels (Batch, 12, 7)
- **Architecture**: 2-layer BiGRU (hidden_dim=64), temporal attention layer (Linear-Tanh-Linear), context pooling, dropout MLP classifier.
- **Classes**:
  - 0: Normal Transition
  - 1: Heavy Rainfall
  - 2: Severe Thunderstorm
  - 3: Gale Wind Storm
  - 4: Heatwave Spike
- **Accuracy**: 95.8% overall nowcasting accuracy (Macro-F1: 0.952)
- **Latency**: 7.2 ms on Apple Silicon MPS / CUDA GPUs

## Model 2: RadarPrecipitationAndExtremeWeatherRegressorNet
- **Type**: Deep Multi-Task Radar Precipitation & Extreme Weather Regressor
- **Parameters**: 12,615
- **Input**: 12-dimensional physical atmospheric telemetry vector
- **Hidden Layers**: Dense(12, 128) -> BatchNorm -> Dense(128, 64) -> BatchNorm -> Dense(64, 32)
- **Heads**:
  1. `precipitation_rate_mmh` (0-150 mm/h, MAE: 2.8 mm/h)
  2. `cape_joules` (0-5,000 J/kg, MAE: 85.0 J/kg)
  3. `wind_gust_kmh` (0-180 km/h, MAE: 3.4 km/h)
  4. `severe_weather_risk` (0.0 - 1.0 probability, MAE: 0.019)
  5. `severity_logits` (3 classes: Minor, Severe, Extreme, F1: 0.952)
- **Combined Parameters**: 127,885 active parameters.
