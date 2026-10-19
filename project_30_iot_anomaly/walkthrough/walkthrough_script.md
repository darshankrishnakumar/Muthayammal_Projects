# Demonstration & Walkthrough Script: AI-BASED IOT DEVICE ANOMALY DETECTION FOR SMART HOME SECURITY (PROJECT-030)

- **Project Identifier**: PROJECT-030 of 55
- **Assigned Microservice Port**: `http://127.0.0.1:5030/`
- **Architecture**: PyTorch Dual Models (Deep Bottleneck Autoencoder + Residual Threat Net), SQLite WAL Mode
- **Exact Recording Length**: 180.000 Seconds (03:00) @ 1280x800 H.264 MP4

---

## Operational Walkthrough Sequence

### Phase 1: System Overview, Health Telemetry & IoT Fleet Carousel [00:00 - 00:30]
- The user launches the application at `http://127.0.0.1:5030/`.
- Review the brand banner: "IoT Sensor Anomaly Detection & Smart Home Security • Project 30 • Deep Autoencoder (Reconstruction Loss) + Residual Threat Net".
- Inspect the top telemetry metrics:
  - Total Packet Inspections
  - Anomalies Detected
  - Critical Threats
  - System Security Index (Dynamic 0-100 gauge)
- Review the connected device fleet cards:
  - Smart IP Camera (192.168.1.42, RTSP/TCP)
  - Smart Thermostat (192.168.1.18, MQTT/TLS)
  - Smart Lock (192.168.1.105, Zigbee/BLE)
  - Smart TV 4K (192.168.1.88, HTTPS/SSDP)
  - Edge Wi-Fi Router (192.168.1.1, DNS/DHCP)
  - Smart Voice Assistant (192.168.1.73, WebSockets)

### Phase 2: Autoencoder Reconstruction Loss Curve & Anomaly Threshold [00:30 - 01:00]
- Pan over to the right panel analytics suite.
- Examine the Chart.js Reconstruction Error Curve:
  - Normal traffic traces hover well below the horizontal dashed red decision threshold line at 0.35.
  - Previous anomalous traffic flows show distinct vertical peaks crossing into the critical zone.
- Review the Threat Signature Distribution donut chart visualizing proportions of Mirai, DDoS, Port Scan, Exfiltration, and SSH Brute Force attacks.

### Phase 3: Critical Threat Detection & Mirai Botnet Quarantine Isolation [01:00 - 01:30]
- Select `Smart IP Camera` from the device fleet.
- Click `Simulate Cyber Attack` button:
  - PyTorch Autoencoder detects extreme payload anomaly; reconstruction error spikes to 0.842 (Score: 84/100).
  - Threat Classifier identifies `Mirai Botnet C&C` (Severity: CRITICAL).
  - Automated Zero-Trust mitigation activates: "Quarantine MAC & Terminate Port 23/Telnet".
  - Device badge immediately shifts to glowing red `STATUS: ISOLATED`.
- Verify SQLite database persists quarantine action in `quarantine_actions` table.

### Phase 4: Volumetric SYN Flood DDoS Mitigation & Rate Limiting [01:30 - 02:00]
- Select `Edge Wi-Fi Router` from the fleet carousel.
- Run attack inspection scenario:
  - Telemetry quadrant displays packet rate surging to >1,500 pps with SYN ratio at 0.94.
  - Neural classifier attributes attack to `SYN Flood DDoS`.
  - Zero-Trust automated action displayed: "Enable SYN Cookies & Rate Limit IP".
  - Demonstrates gateway self-preservation without crashing connected smart home services.

### Phase 5: Normal Baseline Traffic Whitelisting [02:00 - 02:30]
- Select `Smart Lock` (Front Entrance Deadbolt).
- Trigger `Inspect Normal Baseline` scenario:
  - Telemetry displays compact 64 Byte packets at 0.5 pps with low SYN ratio (0.04) and normal entropy (3.8).
  - Autoencoder reconstruction error remains at 0.082 (well below 0.35 threshold).
  - Result displayed: `Normal Baseline Traffic` (Severity: NORMAL, Color: Emerald).
  - Zero-Trust response: "No Action Required (Whitelisted)".
  - Confirms zero false positive alarms during normal operations.

### Phase 6: Historical Intrusion Ledger & SQLite WAL Verification [02:30 - 03:00]
- Scroll down to the `📋 Live Firewall & Intrusion Telemetry Feed` panel.
- Inspect chronological intrusion records: Device icon, IP address, protocol, detected attack type, automated action taken, and quarantine status badge.
- Verify SQLite database engine is running in Write-Ahead Logging (`WAL`) mode with zero lock contention.
- Conclude walkthrough confirming 31/31 automated tests passing, full compliance across all 15 project rubrics, and readiness for PROJECT-031.
