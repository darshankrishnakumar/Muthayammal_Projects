# 08. Enterprise Deployment & Operations Guide (PROJECT-026)

## System Prerequisites
- **Operating System:** Linux (Ubuntu 22.04 LTS recommended) / macOS
- **Python Runtime:** Python 3.10, 3.11, or 3.12
- **Required Libraries:** `torch`, `numpy`, `pandas`, `scikit-learn`, `flask`, `flask-cors`
- **Network Interface:** Port 5026 open for TCP ingress

## Step-by-Step Production Launch
```bash
# 1. Navigate to project root
cd project_26_network_intrusion

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify / Train PyTorch Models (Weights already serialized)
python3 source_code/data/generate_dataset_and_train.py

# 4. Launch Backend Server on Dedicated Port 5026
python3 source_code/backend/app.py
```

## Systemd Production Daemon Configuration (`/etc/systemd/system/nids.service`)
```ini
[Unit]
Description=AI Network Intrusion Detection System (PROJECT-026)
After=network.target

[Service]
User=security
WorkingDirectory=/opt/nids/project_26_network_intrusion/source_code/backend
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=5
Environment=PORT=5026

[Install]
WantedBy=multi-user.target
```

## Firewall Script Execution
Generated iptables rules can be piped directly to the kernel:
```bash
curl -s http://127.0.0.1:5026/api/firewall/rules | jq -r .iptables_script | sudo bash
```
