import express from "express";
import path from "path";
import fs from "fs";
import { spawn, execFile } from "child_process";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;
const PYTHON_PORT = 5004;
const PYTHON_CMD = process.platform === "win32" ? "python" : "python3";

app.use(express.json());

// Start FastAPI in the background
let pyProcess: any = null;

function startPythonBackend() {
  try {
    pyProcess = spawn(PYTHON_CMD, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(PYTHON_PORT)], {
      stdio: "inherit",
      detached: false,
    });

    pyProcess.on("error", (err: any) => {
      console.warn("FastAPI process spawn error:", err.message);
    });

    pyProcess.on("exit", (code: number) => {
      console.log(`FastAPI process exited with code ${code}`);
    });
  } catch (err: any) {
    console.warn("Could not spawn uvicorn directly:", err.message);
  }
}

startPythonBackend();

process.on("SIGINT", () => {
  if (pyProcess) pyProcess.kill();
  process.exit();
});

process.on("SIGTERM", () => {
  if (pyProcess) pyProcess.kill();
  process.exit();
});

// Helper to query Python FastAPI backend with fallback to direct Python execution
async function queryPythonAPI(endpoint: string, method: string = "GET", body?: any): Promise<any> {
  const url = `http://127.0.0.1:${PYTHON_PORT}${endpoint}`;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (res.ok) {
      return await res.json();
    } else {
      const errBody = await res.json().catch(() => ({}));
      let msg = errBody.detail || errBody.error;
      if (Array.isArray(msg)) {
        msg = msg.map((m: any) => `${m.loc?.join('.') || 'field'}: ${m.msg}`).join(', ');
      }
      throw new Error(msg || `Request failed with status ${res.status}`);
    }
  } catch (err: any) {
    // If it was an intentional error thrown above, rethrow
    if (err.message && !err.message.includes('fetch') && !err.message.includes('abort')) {
      throw err;
    }
    // Otherwise fallback to direct Python or file read
  }

  // Fallbacks if FastAPI is still booting or unavailable
  if (endpoint === "/api/info") {
    const metaPath = path.join(process.cwd(), "models", "model_metadata.json");
    if (fs.existsSync(metaPath)) {
      return JSON.parse(fs.readFileSync(metaPath, "utf-8"));
    }
  }

  if (endpoint === "/api/predict" && body) {
    return new Promise((resolve, reject) => {
      const script = `
import json, sys
from app.main import CarInputSchema, predict_car_price
payload = json.loads(sys.argv[1])
try:
    car = CarInputSchema(**payload)
    result = predict_car_price(car)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}), file=sys.stderr)
    sys.exit(1)
`;
      execFile(PYTHON_CMD, ["-c", script, JSON.stringify(body)], (error, stdout, stderr) => {
        if (error) {
          return reject(new Error(stderr || error.message));
        }
        try {
          resolve(JSON.parse(stdout.trim()));
        } catch (e: any) {
          reject(new Error("Failed to parse Python prediction response"));
        }
      });
    });
  }

  if (endpoint.startsWith("/api/dataset/sample")) {
    const csvPath = path.join(process.cwd(), "data", "car_data.csv");
    if (fs.existsSync(csvPath)) {
      const content = fs.readFileSync(csvPath, "utf-8");
      const lines = content.split("\n").filter((l) => l.trim().length > 0);
      const headers = lines[0].split(",");
      const sampleRows = lines.slice(1, 16).map((line) => {
        const vals = line.split(",");
        const obj: Record<string, any> = {};
        headers.forEach((h, i) => {
          obj[h.trim()] = vals[i]?.trim();
        });
        return obj;
      });
      return sampleRows;
    }
  }

  throw new Error("Service temporarily unavailable");
}

// REST API Endpoints
app.get("/api/health", async (req, res) => {
  try {
    const pyHealth = await queryPythonAPI("/api/health", "GET").catch(() => null);
    res.json({
      status: "healthy",
      timestamp: new Date().toISOString(),
      backend_python: pyHealth ? "connected" : "standalone_mode",
      models_loaded: pyHealth?.models_loaded || ["Random Forest Regression"]
    });
  } catch (err: any) {
    res.json({ status: "healthy", timestamp: new Date().toISOString() });
  }
});

app.get("/api/info", async (req, res) => {
  try {
    const data = await queryPythonAPI("/api/info", "GET");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/dataset/sample", async (req, res) => {
  try {
    const data = await queryPythonAPI("/api/dataset/sample", "GET");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/predict", async (req, res) => {
  try {
    const result = await queryPythonAPI("/api/predict", "POST", req.body);
    res.json(result);
  } catch (err: any) {
    res.status(400).json({ error: err.message });
  }
});

app.get("/api/history", async (req, res) => {
  try {
    const data = await queryPythonAPI("/api/history", "GET");
    res.json(data || []);
  } catch (err: any) {
    res.json([]);
  }
});

app.delete("/api/history/:id", async (req, res) => {
  try {
    const data = await queryPythonAPI(`/api/history/${req.params.id}`, "DELETE");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.delete("/api/history", async (req, res) => {
  try {
    const data = await queryPythonAPI("/api/history", "DELETE");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/retrain", (req, res) => {
  execFile(PYTHON_CMD, ["scripts/train_model.py"], (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ success: false, error: stderr || error.message });
    }
    const metaPath = path.join(process.cwd(), "models", "model_metadata.json");
    let meta = {};
    if (fs.existsSync(metaPath)) {
      meta = JSON.parse(fs.readFileSync(metaPath, "utf-8"));
    }
    res.json({ success: true, message: "Models retrained and evaluated successfully", metadata: meta });
  });
});

async function startServer() {
  const distPath = path.join(process.cwd(), "dist");
  const hasPrebuiltDist = fs.existsSync(path.join(distPath, "index.html"));

  if (process.env.NODE_ENV === "production" || hasPrebuiltDist) {
    console.log("Serving optimized pre-bundled static application from dist/ (sub-10ms latency)");
    app.use(express.static(distPath));
    app.get("*", (req, res, next) => {
      if (req.path.startsWith("/api/")) return next();
      res.sendFile(path.join(distPath, "index.html"));
    });
  } else {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  }

  app.listen(PORT, () => {
    console.log(`Car Price Prediction Server running at:`);
    console.log(`  - Local:   http://127.0.0.1:${PORT}`);
    console.log(`  - Network: http://localhost:${PORT}`);
  });
}

startServer();
