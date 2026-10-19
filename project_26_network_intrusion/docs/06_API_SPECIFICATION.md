# 06. REST API Specification (PROJECT-026)

**Base URL:** `http://127.0.0.1:5026/api`

### 1. `GET /api/health`
Returns service status, architecture, port 5026, model metadata, and database state.

### 2. `GET /api/stats`
Returns system rollups: total flows, attacks intercepted, normal packets, critical threats, threat ratio %, active quarantine count, category breakdown, PPS throughput, and bandwidth.

### 3. `GET /api/stream/next`
Simulates the next realistic network flow in real-time, executes PyTorch forward pass, persists to SQLite, and returns enriched JSON.

### 4. `POST /api/simulate/attack`
Injects a specific cyber attack vector (`SYN_Flood`, `Port_Scan`, `SSH_BruteForce`, `Mirai_Botnet`, `Zero_Day`, `Normal`), executes inference, and triggers automated defense.

### 5. `POST /api/analyze/flow`
Analyzes a custom 12-dimensional flow JSON object supplied by the user/sensor.

### 6. `GET /api/traffic/log?limit=50`
Retrieves recent network flow logs from SQLite `network_flows` table.

### 7. `GET /api/quarantine`
Returns all active blacklisted IP addresses, trigger reasons, and timestamps.

### 8. `POST /api/quarantine`
Manually or programmatically quarantines an IP address (`{"ip": "1.2.3.4", "reason": "SOC Block"}`).

### 9. `DELETE /api/quarantine`
Unquarantines an IP address, updating status to UNBLOCKED and revoking firewall rules.

### 10. `GET /api/firewall/rules`
Generates concrete copy-pasteable firewall rules across Linux `iptables`, Ubuntu `ufw`, and AWS VPC Network ACLs.
