# 05. Deep Neural Model Design (PROJECT-028)

## 1. BiLSTM Time-Series Forecaster (`AQITimeSeriesBiLSTM`)
```python
class AQITimeSeriesBiLSTM(nn.Module):
    def __init__(self, in_features=10, hidden_dim=64, num_layers=2, out_features=3, horizon=24):
        super().__init__()
        self.bilstm = nn.LSTM(
            input_size=in_features, hidden_size=hidden_dim, num_layers=num_layers,
            batch_first=True, bidirectional=True, dropout=0.15
        )
        self.fc1 = nn.Linear(hidden_dim * 2, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, horizon * out_features)

    def forward(self, x):
        lstm_out, _ = self.bilstm(x)
        last_step = lstm_out[:, -1, :]
        h = self.relu(self.fc1(last_step))
        out = self.fc2(h)
        return out.view(-1, self.horizon, self.out_features)
```
- **Weights File:** `source_code/backend/aqi_bilstm_weights.pt` (648 KB)

## 2. Environmental Hazard Classifier (`AQIHazardClassifier`)
```python
class AQIHazardClassifier(nn.Module):
    def __init__(self, in_features=10, num_classes=6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.15),
            nn.Linear(64, 48),
            nn.BatchNorm1d(48),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.1),
            nn.Linear(48, num_classes)
        )
```
- **Weights File:** `source_code/backend/aqi_classifier_weights.pt` (24 KB)
- **Test Accuracy:** 93.73% across 1,100 test vectors
