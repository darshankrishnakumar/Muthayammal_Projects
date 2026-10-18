# Limitations & Future Roadmap

## Known Limitations

1. **Synthetic & Simulated Traffic Horizon**:
   - The NSL-KDD dataset represents synthetic and sanitized network connections designed for academic benchmarking. While it successfully establishes relative algorithmic performance and feature importance, production deployment in modern enterprise perimeters requires testing against live multi-gigabit encrypted TLS traffic.
2. **Encrypted Payload Inspection**:
   - Modern HTTPS / TLS 1.3 encryption masks deep packet payloads. The current model relies heavily on network flow telemetry, connection timing, byte rates, and TCP flags. Extension to encrypted traffic requires JA3/JA4 fingerprinting and packet length sequence analysis.
3. **Imbalanced Representation of Rare Exploits (U2R)**:
   - In benchmark datasets, User-to-Root (U2R) exploits constitute less than 0.5% of total records. While the ensemble maintains high overall precision, advanced synthetic oversampling (e.g. SMOTE / CTGAN) can further enhance rare-class recall.

---

## Future Roadmap

1. **Kernel-Bypass & eBPF Integration**:
   - Integrate with Linux extended Berkeley Packet Filters (eBPF) or DPDK (Data Plane Development Kit) to evaluate packet telemetry directly in kernel space at 100 Gbps line rate without user-space context-switching penalties.
2. **Graph Neural Networks (GNNs)**:
   - Model enterprise network topologies as dynamic heterogeneous graphs to detect sophisticated multi-stage advanced persistent threats (APTs) and lateral reconnaissance.
3. **Automated SIEM / SOAR Connectors**:
   - Implement webhooks and syslog forwarders to stream alerts into standard enterprise SIEM platforms (Splunk, Elastic SIEM, Microsoft Sentinel).
