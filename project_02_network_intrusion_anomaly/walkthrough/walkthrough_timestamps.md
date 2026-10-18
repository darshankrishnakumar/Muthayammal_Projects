# Walkthrough Demonstration Timestamps

**Project Identifier**: Project 02 of 55 (`PROJECT-002`)  
**Project Title**: Network Intrusion Detection Using Ensemble Machine Learning and Anomaly Detection  
**Video File**: `walkthrough/walkthrough_video.mp4`  
**Video Resolution**: 1280x800 (H.264 High Profile, 24 fps)  
**Total Duration**: 03:00 (180.0 seconds)

---

## Chronological Operational Flow

| Timestamp | Duration | Section / Operational Phase | Core Features & Actions Demonstrated |
|:---:|:---:|---|---|
| **00:00 - 00:20** | 20s | **SOC Dashboard & Architecture Overview** | Initial page load at `http://127.0.0.1:5002`. Displays "CYBERSHIELD AI" header, live status beacon ("SOC ONLINE PORT 5002"), dual-engine architecture, and tab navigation. |
| **00:20 - 00:45** | 25s | **Neptune SYN Flood (DoS Attack)** | Ingests high-frequency TCP SYN packet without ACK (`flag=S0`, `count=250`, `serror_rate=1.0`). Ensemble returns **DoS** with 82.1% confidence. Automated defense triggers: `BLOCK & THROTTLE`. |
| **00:45 - 01:10** | 25s | **Port Sweep Reconnaissance (Probe)** | Ingests TCP RST sweep (`flag=RSTR`, `rerror_rate=1.0`). Ensemble returns **Probe** reconnaissance. Automated mitigation triggers: `BLACKLIST SOURCE IP`. |
| **01:10 - 01:30** | 20s | **Benign Web Browsing (HTTP Session)** | Ingests standard HTTP session (`flag=SF`, `src_bytes=280`, `dst_bytes=3520`, `logged_in=1`). Ensemble returns **Normal** with 97.9% confidence. Automated action: `ALLOW`. |
| **01:30 - 01:50** | 20s | **Password Brute-Force (R2L Attack)** | Ingests repeated authentication failures over Telnet (`num_failed_logins=5`, `logged_in=0`). Ensemble classifies as **R2L** unauthorized access. Automated mitigation: `REVOKE CREDENTIALS`. |
| **01:50 - 02:15** | 25s | **Zero-Day Out-of-Distribution Anomaly** | Ingests anomalous UDP exfiltration with extreme payload size (985 KB) and hot indicators. Supervised models flag normal, but **Isolation Forest anomaly gauge surges to 76.6%**, triggering `SUSPICIOUS_ANOMALY` quarantine. |
| **02:15 - 02:30** | 15s | **Model Benchmarks & Defense Taxonomy** | Switches to Benchmarks tab. Reviews Random Forest (98.34% accuracy), Extra Trees (98.03% accuracy), weighted F1-score (0.9833), and full defense signature taxonomy. |
| **02:30 - 02:45** | 15s | **Security Event Audit Log (SQLite)** | Switches to Event Logs tab. Demonstrates transactional database persistence (`nids.db`) with real-time audit stream showing timestamps, IP addresses, classifications, and mitigation logs. |
| **02:45 - 03:00** | 15s | **Threat Intelligence Analytics** | Switches to Analytics tab. Reviews high-level SOC statistics: total packets inspected, malicious vs. benign breakdown, average latency (55.8 ms), and threat severity distribution. |
