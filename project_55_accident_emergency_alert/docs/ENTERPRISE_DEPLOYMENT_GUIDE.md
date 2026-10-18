# PROJECT 55 — ENTERPRISE DEPLOYMENT & OPERATION GUIDE
## Production Orchestration, Docker, Kubernetes, and Runbook

---

### 1. Architecture Deployment Topology
The Project 55 platform is structured as a cloud-native microservices architecture designed for deployment on edge gateways (NVIDIA Jetson / roadside compute nodes) or central Traffic Management Cloud Clusters (AWS / GCP / Azure):

```mermaid
graph TD
    subgraph Edge["Roadside Edge Nodes / Cameras"]
        C1[CCTV Camera 1] -->|RTSP / HLS| EP[Edge Ingestion Gateway]
        C2[CCTV Camera 2] -->|RTSP / HLS| EP
        Dash[Fleet Dashcams] -->|WebRTC / RTMP| EP
    end

    subgraph Cluster["Kubernetes / Docker Cluster"]
        EP --> Ingress[Nginx Ingress Controller & SSL]
        Ingress --> APIService[FastAPI AI Inference Pods]
        APIService --> ModelWorker[PyTorch Multi-Cue Engine MPS/CUDA]
        APIService --> DB[(PostgreSQL / SQLite Database)]
        APIService --> WSBroker[WebSocket Real-Time Hub]
    end

    subgraph Egress["Emergency Integration & Operators"]
        APIService --> CAD[Computer-Aided Dispatch 911 API]
        APIService --> SMS[Emergency SMS / Webhook Gateway]
        WSBroker --> TMC[TMC Operator Command Center UI]
    end
```

---

### 2. Quickstart Run Instructions

#### Option A: Direct Local Execution
Ensure Python 3.10+ is active.
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Database Setup and Model Warmup
python3 backend/app/db/session.py

# 3. Launch Enterprise System
python3 run_system.py
```
The system will start at:
- **Operator Command Dashboard**: `http://localhost:8000`
- **Interactive Swagger REST API Docs**: `http://localhost:8000/docs`
- **WebSocket Telemetry Stream**: `ws://localhost:8000/api/ws`
- **Health Check Endpoint**: `http://localhost:8000/api/health/`

#### Option B: Containerized Deployment via Docker Compose
```bash
cd docker
docker-compose up --build -d
```
Verify container status:
```bash
docker-compose ps
docker logs -f project55_enterprise_api
```

---

### 3. Production Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Set to `production` or `development` |
| `DATABASE_URL` | `sqlite:///./data/project55_enterprise.db` | SQLAlchemy connection URI (supports PostgreSQL: `postgresql://user:pass@host/db`) |
| `DEFAULT_CONFIDENCE_THRESHOLD` | `0.65` | Calibrated threshold for triggering high-confidence CAD dispatches |
| `AUTO_DISPATCH_ENABLED` | `true` | Automated emergency dispatch notification trigger |
| `EMERGENCY_WEBHOOK_URL` | `https://mock-cad-dispatch.traffic.gov/alerts` | Destination CAD / EMS Webhook URL |
| `PORT` | `8000` | HTTP listen port |

---

### 4. Kubernetes Production Deployment Manifest (Snippet)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project55-inference-engine
  labels:
    app: project55-cv
spec:
  replicas: 3
  selector:
    matchLabels:
      app: project55-cv
  template:
    metadata:
      labels:
        app: project55-cv
    spec:
      containers:
      - name: cv-engine
        image: project55/accident-detection:latest
        resources:
          limits:
            cpu: "4000m"
            memory: "8Gi"
            nvidia.com/gpu: "1"
          requests:
            cpu: "1000m"
            memory: "2Gi"
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

### 5. Operator Runbook: Incident Triage Workflow
1. **Live Feed Monitoring**: Operator observes roadside camera feeds in the Command Center. Green bounding boxes designate standard traffic flow.
2. **Alert Trigger**: When confidence $\ge 0.65$, an audible alert sounds, the video HUD turns red, and an emergency incident card enters the **Live Incident Feed**.
3. **Forensic Evidence Verification**: Operator clicks the incident card to inspect the high-resolution evidence snapshot, 5-cue radar scores, and deceleration curve.
4. **Action Triage**:
   - Click **`Dispatch CAD`** to transmit the telemetry payload to 911 / EMS.
   - Click **`Acknowledge`** to flag that a dispatcher is actively managing the incident.
   - Click **`False Alarm`** if manual inspection reveals non-collision activity (logs forensic feedback to refine model weights).
   - Click **`Resolve`** once responders clear the roadway.
