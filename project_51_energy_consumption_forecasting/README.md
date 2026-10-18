# PROJECT 51: Smart Energy Consumption Forecasting and Optimization Using Machine Learning

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)

> **Multi-Horizon Deep Bi-LSTM Electricity Demand Forecasting & Peak-Shaving Dynamic Load Shifting Platform.**

```
        [Historical Smart Meter & Meteorological Telemetry]
                                │
                                ▼
               [Deep Bi-LSTM Demand Forecaster]
                                │
                                ▼
             [24-Hour Ahead Electricity Demand Curve]
                                │
                                ▼
             [Constrained Peak Shaving Optimizer]
             • Time-of-Use (TOU) Tariff Arbitrage
             • HVAC & Battery ESS Load Shifting
                                │
                                ▼
         [Optimized Dispatch Schedule & Cost/CO2 Savings]
```

## Quickstart
```bash
cd College_51
pip install -r requirements.txt
python run_system.py --port 8051
```
Dashboard at [http://localhost:8051](http://localhost:8051)
