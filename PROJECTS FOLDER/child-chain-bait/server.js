const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const BACKEND_PORT = 8000;
const FRONTEND_PORT = 8080;

const DB_DIR = path.join(__dirname, 'backend', 'database');
const CSV_FILE = path.join(__dirname, 'backend', 'data', 'synthetic_child_gait.csv');
const JSON_DB = path.join(DB_DIR, 'gait_records.json');
const HTML_FILE = path.join(__dirname, 'public', 'index.html');

// Ensure database directory exists
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true });
}

// In-memory records store
let records = [];

function loadInitialData() {
  if (fs.existsSync(JSON_DB)) {
    try {
      const data = fs.readFileSync(JSON_DB, 'utf8');
      records = JSON.parse(data);
      console.log(`[DB] Loaded ${records.length} records from ${JSON_DB}`);
      return;
    } catch (e) {
      console.warn('[DB] Failed to parse JSON DB, falling back to CSV:', e.message);
    }
  }

  // Load from synthetic_child_gait.csv
  if (fs.existsSync(CSV_FILE)) {
    try {
      const content = fs.readFileSync(CSV_FILE, 'utf8');
      const lines = content.trim().split('\n');
      records = [];
      for (let i = 1; i < lines.length; i++) {
        const parts = lines[i].split(',').map(p => p.trim());
        if (parts.length >= 10) {
          const rec = {
            id: `rec-dev-${i}`,
            child_id: parts[0],
            childId: parts[0],
            age: parseInt(parts[1], 10),
            gender: parts[2],
            heel_pressure: parseFloat(parts[3]),
            heelPressure: parseFloat(parts[3]),
            toe_pressure: parseFloat(parts[4]),
            toePressure: parseFloat(parts[4]),
            tilt_angle: parseFloat(parts[5]),
            tiltAngle: parseFloat(parts[5]),
            step_duration: parseFloat(parts[6]),
            stepDuration: parseFloat(parts[6]),
            stride_length: parseFloat(parts[7]),
            strideLength: parseFloat(parts[7]),
            walking_speed: parseFloat(parts[8]),
            walkingSpeed: parseFloat(parts[8]),
            gait_class: parts[9],
            prediction: parts[9],
            confidence: 0.95,
            data_source: 'synthetic',
            created_at: new Date(Date.now() - (lines.length - i) * 86400000).toISOString(),
            date: new Date(Date.now() - (lines.length - i) * 86400000).toISOString()
          };
          records.push(rec);
        }
      }
      saveRecords();
      console.log(`[DB] Imported ${records.length} records from ${CSV_FILE}`);
    } catch (err) {
      console.error('[DB] CSV import error:', err.message);
    }
  }
}

function saveRecords() {
  try {
    fs.writeFileSync(JSON_DB, JSON.stringify(records, null, 2), 'utf8');
  } catch (err) {
    console.error('[DB] Failed to save records:', err.message);
  }
}

function classifyGait(data) {
  const tilt = parseFloat(data.tilt_angle ?? data.tiltAngle ?? 0);
  const duration = parseFloat(data.step_duration ?? data.stepDuration ?? 0);
  const stride = parseFloat(data.stride_length ?? data.strideLength ?? 0);
  const speed = parseFloat(data.walking_speed ?? data.walkingSpeed ?? 0);
  const heel = parseFloat(data.heel_pressure ?? data.heelPressure ?? 0);
  const toe = parseFloat(data.toe_pressure ?? data.toePressure ?? 0);

  let prediction = 'Normal';
  let confidence = 0.95;
  let recommendations = [
    'Symmetric bilateral gait pattern observed within normative thresholds.',
    'Continue routine developmental pediatric observation.',
    'Maintain age-appropriate physical play and recreational activities.'
  ];

  if (tilt >= 10.0 || (duration >= 0.70 && stride <= 65.0)) {
    prediction = 'Diplegic';
    confidence = 0.92;
    recommendations = [
      'Bilateral spasticity or crouch gait features detected across lower limbs.',
      'Recommend pediatric physical therapy evaluation for lower limb motor tone.',
      'Assess sagittal joint kinematics (hip flexion, knee extension, ankle equinus).',
      'Consider gait laboratory biomechanical evaluation and AFO orthotic suitability.'
    ];
  } else if (tilt >= 8.0 || (heel < 130 && speed > 1.0) || Math.abs(heel - toe) > 70) {
    prediction = 'Hemiplegic';
    confidence = 0.88;
    recommendations = [
      'Asymmetrical gait characteristics identified with unilateral bias.',
      'Pediatric neurological consultation advised to examine hemiparetic signs.',
      'Assess unilateral drop-foot, circumduction, or asymmetric weight acceptance.',
      'Targeted physical therapy focusing on single-limb stance balance and symmetry.'
    ];
  }

  return { prediction, confidence, recommendations };
}

loadInitialData();

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// BACKEND API SERVER (PORT 8000)
const backendServer = http.createServer(async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // Root endpoint
  if (pathname === '/' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      service: 'Child Gait Prediction Backend API',
      status: 'online',
      database: 'SQLite/JSON (gait_records)',
      endpoints: {
        health: '/api/health',
        records: '/api/records',
        predict: '/api/predict',
        docs: '/docs'
      },
      disclaimer: 'This application is a college-level machine learning prototype intended for educational and decision-support purposes.'
    }, null, 2));
    return;
  }

  // Health endpoint
  if (pathname === '/api/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      database: 'connected',
      table: 'gait_records',
      totalRecords: records.length
    }));
    return;
  }

  // Swagger UI docs
  if (pathname === '/docs' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`<!DOCTYPE html>
<html>
<head>
  <title>Child Gait Prediction Backend API — Swagger Docs</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body style="margin:0; background:#fafafa;">
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      dom_id: '#swagger-ui',
      spec: {
        openapi: '3.0.2',
        info: {
          title: 'Child Gait Prediction Backend API',
          version: '1.0.0',
          description: 'Data pipeline and persistence service for pediatric gait assessments.'
        },
        paths: {
          '/api/health': {
            get: {
              summary: 'Health Check',
              responses: { '200': { description: 'Health status' } }
            }
          },
          '/api/records': {
            get: {
              summary: 'List Gait Records',
              parameters: [{ name: 'childId', in: 'query', schema: { type: 'string' } }],
              responses: { '200': { description: 'List of gait assessment records' } }
            },
            post: {
              summary: 'Create Gait Record',
              requestBody: { content: { 'application/json': { schema: { type: 'object' } } } },
              responses: { '201': { description: 'Created record' } }
            }
          },
          '/api/predict': {
            post: {
              summary: 'Predict Gait and Store Assessment',
              requestBody: { content: { 'application/json': { schema: { type: 'object' } } } },
              responses: { '200': { description: 'Prediction result & persisted assessment record' } }
            }
          }
        }
      }
    });
  </script>
</body>
</html>`);
    return;
  }

  // GET /api/records or /api/records?childId=...
  if (pathname === '/api/records' && req.method === 'GET') {
    const childId = parsedUrl.query.childId || parsedUrl.query.child_id;
    let filtered = records;
    if (childId) {
      filtered = records.filter(r => (r.child_id || r.childId || '').toLowerCase() === String(childId).toLowerCase());
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(filtered));
    return;
  }

  // GET /api/records/child/:child_id
  if (pathname.startsWith('/api/records/child/') && req.method === 'GET') {
    const childId = decodeURIComponent(pathname.replace('/api/records/child/', ''));
    const filtered = records.filter(r => (r.child_id || r.childId || '').toLowerCase() === childId.toLowerCase());
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(filtered));
    return;
  }

  // GET /api/records/:record_id
  if (pathname.startsWith('/api/records/') && req.method === 'GET') {
    const id = decodeURIComponent(pathname.replace('/api/records/', ''));
    const record = records.find(r => r.id === id);
    if (!record) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Gait record not found' }));
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(record));
    return;
  }

  // DELETE /api/records/:record_id
  if (pathname.startsWith('/api/records/') && req.method === 'DELETE') {
    const id = decodeURIComponent(pathname.replace('/api/records/', ''));
    const idx = records.findIndex(r => r.id === id);
    if (idx === -1) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Gait record not found' }));
      return;
    }
    records.splice(idx, 1);
    saveRecords();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'deleted', id }));
    return;
  }

  // POST /api/records
  if (pathname === '/api/records' && req.method === 'POST') {
    try {
      const data = await parseBody(req);
      const classification = classifyGait(data);
      const newRec = {
        id: data.id || `gait-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
        child_id: String(data.child_id || data.childId || 'C-Unknown'),
        childId: String(data.child_id || data.childId || 'C-Unknown'),
        age: parseInt(data.age, 10) || 7,
        gender: String(data.gender || 'Unspecified'),
        heel_pressure: parseFloat(data.heel_pressure || data.heelPressure || 0),
        heelPressure: parseFloat(data.heel_pressure || data.heelPressure || 0),
        toe_pressure: parseFloat(data.toe_pressure || data.toePressure || 0),
        toePressure: parseFloat(data.toe_pressure || data.toePressure || 0),
        tilt_angle: parseFloat(data.tilt_angle || data.tiltAngle || 0),
        tiltAngle: parseFloat(data.tilt_angle || data.tiltAngle || 0),
        step_duration: parseFloat(data.step_duration || data.stepDuration || 0),
        stepDuration: parseFloat(data.step_duration || data.stepDuration || 0),
        stride_length: parseFloat(data.stride_length || data.strideLength || 0),
        strideLength: parseFloat(data.stride_length || data.strideLength || 0),
        walking_speed: parseFloat(data.walking_speed || data.walkingSpeed || 0),
        walkingSpeed: parseFloat(data.walking_speed || data.walkingSpeed || 0),
        gait_class: data.gait_class || data.prediction || classification.prediction,
        prediction: data.gait_class || data.prediction || classification.prediction,
        confidence: data.confidence !== undefined ? data.confidence : classification.confidence,
        recommendations: data.recommendations || classification.recommendations,
        data_source: data.data_source || 'user_entry',
        created_at: data.created_at || new Date().toISOString(),
        date: data.date || new Date().toISOString()
      };
      records.unshift(newRec);
      saveRecords();
      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(newRec));
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Invalid JSON payload' }));
    }
    return;
  }

  // POST /api/predict
  if (pathname === '/api/predict' && req.method === 'POST') {
    try {
      const data = await parseBody(req);
      const classification = classifyGait(data);
      const newRec = {
        id: `gait-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
        child_id: String(data.child_id || data.childId || 'C-Unknown'),
        childId: String(data.child_id || data.childId || 'C-Unknown'),
        age: parseInt(data.age, 10) || 7,
        gender: String(data.gender || 'Unspecified'),
        heel_pressure: parseFloat(data.heel_pressure || data.heelPressure || 0),
        heelPressure: parseFloat(data.heel_pressure || data.heelPressure || 0),
        toe_pressure: parseFloat(data.toe_pressure || data.toePressure || 0),
        toePressure: parseFloat(data.toe_pressure || data.toePressure || 0),
        tilt_angle: parseFloat(data.tilt_angle || data.tiltAngle || 0),
        tiltAngle: parseFloat(data.tilt_angle || data.tiltAngle || 0),
        step_duration: parseFloat(data.step_duration || data.stepDuration || 0),
        stepDuration: parseFloat(data.step_duration || data.stepDuration || 0),
        stride_length: parseFloat(data.stride_length || data.strideLength || 0),
        strideLength: parseFloat(data.stride_length || data.strideLength || 0),
        walking_speed: parseFloat(data.walking_speed || data.walkingSpeed || 0),
        walkingSpeed: parseFloat(data.walking_speed || data.walkingSpeed || 0),
        gait_class: classification.prediction,
        prediction: classification.prediction,
        confidence: classification.confidence,
        recommendations: classification.recommendations,
        data_source: 'live_prediction',
        created_at: new Date().toISOString(),
        date: new Date().toISOString()
      };
      records.unshift(newRec);
      saveRecords();

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        prediction: classification.prediction,
        confidence: classification.confidence,
        assessmentId: newRec.id,
        recommendations: classification.recommendations,
        record: newRec
      }));
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Invalid prediction payload' }));
    }
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ detail: 'Endpoint not found' }));
});

// FRONTEND APPLICATION SERVER (PORT 8080)
const frontendServer = http.createServer((req, res) => {
  setCors(res);
  const parsedUrl = url.parse(req.url, true);
  
  if (parsedUrl.pathname === '/' || parsedUrl.pathname === '/index.html' || !path.extname(parsedUrl.pathname)) {
    if (fs.existsSync(HTML_FILE)) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(fs.readFileSync(HTML_FILE, 'utf8'));
      return;
    }
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not Found');
});

// Start both servers
backendServer.listen(BACKEND_PORT, '0.0.0.0', () => {
  console.log(`[Backend API] Running on http://localhost:${BACKEND_PORT}`);
  console.log(`[Backend API] Interactive Swagger docs on http://localhost:${BACKEND_PORT}/docs`);
});

frontendServer.listen(FRONTEND_PORT, '0.0.0.0', () => {
  console.log(`[Frontend UI] Running on http://localhost:${FRONTEND_PORT}`);
});
