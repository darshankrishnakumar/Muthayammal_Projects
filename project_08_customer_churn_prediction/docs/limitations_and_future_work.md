# Limitations and Future Work: Customer Churn Intelligence (PROJECT-008)

## 1. Current Limitations

### 1.1 Static Snapshot Nature of Tabular Attributes
The benchmark IBM Telco corpus captures customer behavior as an aggregated cross-sectional snapshot rather than a streaming event log. Consequently, dynamic changes in user behavior (e.g., sudden drop in weekly bandwidth consumption, spike in customer service complaint calls, or failed credit card authorizations) are represented through static cumulative indicators rather than real-time temporal signals.

### 1.2 Proportional Hazards Assumption
The Cox Proportional Hazards model assumes that the relative hazard ratio between any two subscribers remains constant across their entire subscription tenure. In reality, telecom subscribers often undergo distinct lifecycle phases—onboarding vulnerability (months 1–3), mid-tenure stability (months 4–24), and contract-expiration churn windows—violating strict proportionality for certain service configurations.

### 1.3 Absence of Customer Sentiment Signals
Customer churn is frequently catalyzed by qualitative customer support interactions, network outage frustration, or negative competitor advertising. These textual and sentiment dimensions are not captured in the numeric/categorical attributes of the current corpus.

---

## 2. Future Work & Architectural Extensions

### 2.1 Deep Survival Analysis (DeepSurv & Survival Transformers)
Transition from semi-parametric Cox regression to neural non-linear survival architectures such as DeepSurv or Transformer-based multi-event models (Dynamic-DeepHit). This enables modeling non-proportional hazard dynamics and complex high-order feature interactions.

### 2.2 Streaming Telemetry & Event-Driven Microservices
Integrate Apache Kafka event streams to capture real-time network QoS metrics (packet latency, dropped calls, 5G signal strength) and web interaction events, recalculating subscriber risk scores in sub-second streaming pipelines.

### 2.3 Automated Uplift Modeling & Counterfactual Recommendations
Extend the prescriptive recommendation engine with Causal Machine Learning (Uplift Modeling). Rather than merely predicting *who* will churn, uplift models predict *which intervention* (e.g., $10 discount vs free speed tier upgrade) delivers the highest incremental retention probability for each individual customer.
