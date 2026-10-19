# 04. Data Pipeline & Graph Topologies

## Entity & Transaction Distribution
The benchmark financial graph dataset models a complex cross-border banking ecosystem consisting of 520 entities and 1,650 transactions:

| Entity Subgraph Category | Node Count | Edge Count | Average Balance | Primary Jurisdictions |
|:--------------------------|:----------:|:----------:|:---------------:|:---------------------:|
| Normal Commercial Retail  | 450        | ~1,500     | $1,500 - $45,000| US, CA, UK, DE, FR    |
| Circular Carousel Syndicate| 15        | 15         | $180k - $340k   | VG, CY, PA, SC, KY    |
| Smurfing Fan-Out Syndicate| 32         | 30         | $8.9k - $9.8k   | US, UK, CH, DE        |
| Aggregation Funnel Hub    | 18         | 16         | $25k - $48k     | KY, VG, BS, US        |
| **Total Benchmark Corpus**| **520**    | **1,650**  | **$12,850,000** | **18 Jurisdictions**  |

## Topological Feature Vectors (8 Features)
1. `log10(balance + 1)`: Log-transformed account balance.
2. `in_degree`: Count of unique inbound transaction counterparties.
3. `out_degree`: Count of unique outbound transaction counterparties.
4. `log10(total_inflow + 1)`: Cumulative inbound transaction volume.
5. `log10(total_outflow + 1)`: Cumulative outbound transaction volume.
6. `country_risk`: Regulatory risk coefficient assigned to the jurisdiction (0.04 to 0.94).
7. `fan_out_ratio`: Ratio of out-degree to total degree $\frac{\text{deg}^+}{\text{deg}^+ + \text{deg}^- + \epsilon}$.
8. `flow_asymmetry`: Transactional cash asymmetry $\frac{\text{Inflow} - \text{Outflow}}{\text{Inflow} + \text{Outflow} + \epsilon}$.\n