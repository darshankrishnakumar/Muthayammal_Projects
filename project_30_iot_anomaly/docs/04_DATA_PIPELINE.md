# Project 30: Data Pipeline Specification

## 1. Telemetry Feature Vector
1. `packet_size_bytes`: Mean packet size in bytes.
2. `packet_rate_pps`: Packet rate in packets per second.
3. `syn_ratio`: Ratio of TCP SYN flags relative to total headers.
4. `payload_entropy`: Shannon entropy of payload data bits in $[0.0, 8.0]$.
5. `conn_freq_hz`: Connection frequency in Hz.
6. `byte_rate_bps`: Instantaneous throughput in bytes per second.
7. `port_diversity`: Unique destination port ratio in $[0.0, 1.0]$.
8. `retransmission_rate`: TCP retransmission frequency.

## 2. Preprocessing & Normalization
- Z-Score standardization: $x_{\text{norm}} = \frac{x - \mu}{\sigma + 10^{-6}}$.
- Scalers file: `source_code/backend/iot_scalers.json`.
- Dataset: 5,500 samples across 6 devices (55% normal baseline, 45% attack vectors).
