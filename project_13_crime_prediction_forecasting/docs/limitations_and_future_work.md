# Limitations & Future Work

## 1. Current Limitations
- **Data Granularity**: Incident timestamps are recorded at minute resolution; micro-temporal variations under 60 seconds are not captured.
- **Weather Exogenous Factors**: Extreme weather events (severe blizzards, torrential rainfall) suppress crime rates but are currently modeled via temperature seasonal proxies.
- **Spatial Resolution**: Geographic coordinates are modeled within 50-meter street blocks; indoor building layout geometry is not modeled.

## 2. Future Development Roadmap
- **CAD 911 Stream Ingestion**: Real-time Kafka streaming from emergency dispatchers to dynamically recalculate density scores.
- **Explainable AI (XAI)**: SHAP and LIME integration providing real-time feature attribution in the officer dispatch dashboard.
- **Fairness & Constitutional Audits**: Demographic parity checks ensuring unbiased patrol allocation.
