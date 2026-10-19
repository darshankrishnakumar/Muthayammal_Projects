# Model Card: PyTorch Bi-Directional LSTM Forecaster

## Model Summary
- **Model Name**: PyTorch Deep Multi-Layer Bi-LSTM Demand Forecaster
- **Version**: 2.0-Enterprise
- **Input Dimension**: `[Batch Size, 7 Timesteps, 12 Features]`
- **Output**: Continuous expected demand for day $t+1$
- **Total Trainable Weights**: 43,841 parameters
- **Weight Checkpoint**: `source_code/backend/models/lstm_demand_forecaster.pt` (221 KB)

## Neural Layer Graph
```
Input: [B, 7, 12]
  │
  ├── nn.LSTM(input_size=12, hidden_size=64, num_layers=2, batch_first=True, dropout=0.20)
  │     Output: [B, 7, 64]
  │     Last Timestep Slice: [B, 64]
  │
  ├── nn.Linear(in_features=64, out_features=32)
  ├── nn.ReLU()
  ├── nn.Dropout(p=0.20)
  └── nn.Linear(in_features=32, out_features=1)
        Output: [B, 1]
```

## Holdout Evaluation Benchmarks
- **R² Score**: 0.9327
- **Mean Absolute Error (MAE)**: 5.45 units
- **Root Mean Squared Error (RMSE)**: 11.07 units
- **Mean Absolute Percentage Error (MAPE)**: 23.29%
- **Ensemble R²**: 0.9670 (Ensemble with RF & GBM)
