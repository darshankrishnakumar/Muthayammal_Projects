import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase, closeDatabase, getDatabase } from '../src/config/database.js';
import createApp from '../src/app.js';

import modelAdapter from '../src/services/modelAdapter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe('CNN Prediction Endpoints & Safety Invariants', () => {
  let app;
  let testRecordingId;
  let testCsvPath;

  before(async () => {
    initDatabase(':memory:');
    app = createApp();

    // Create an ECG recording to test predictions against
    testCsvPath = path.join(__dirname, 'temp_pred_ecg.csv');
    const lines = ['sample,val'];
    for (let i = 0; i < 50; i++) {
      lines.push(`${i},${(Math.sin(i / 5) * 0.5).toFixed(4)}`);
    }
    fs.writeFileSync(testCsvPath, lines.join('\n'));

    const uploadRes = await request(app)
      .post('/api/ecg/upload')
      .attach('file', testCsvPath);

    testRecordingId = uploadRes.body.data.id;
  });

  after(() => {
    closeDatabase();
    if (fs.existsSync(testCsvPath)) fs.unlinkSync(testCsvPath);
  });

  it('POST /api/predictions - returns 503 MODEL_NOT_CONNECTED when CNN model is not connected', async () => {
    const origUrl = modelAdapter.serviceUrl;
    modelAdapter.serviceUrl = null;
    try {
      const res = await request(app)
        .post('/api/predictions')
        .send({ ecgRecordingId: testRecordingId });

      assert.equal(res.status, 503);
      assert.equal(res.body.success, false);
      assert.equal(res.body.code, 'MODEL_NOT_CONNECTED');
      assert.match(res.body.message, /CNN model has not been connected/i);
    } finally {
      modelAdapter.serviceUrl = origUrl;
    }
  });

  it('CRITICAL SAFETY INVARIANT: No fabricated prediction record is stored in database', async () => {
    const db = getDatabase();
    const rows = db.prepare('SELECT * FROM predictions').all();
    assert.equal(rows.length, 0, 'Predictions table must not contain fabricated entries');
  });

  it('POST /api/predictions - returns 404 for non-existent recording ID', async () => {
    const res = await request(app)
      .post('/api/predictions')
      .send({ ecgRecordingId: 99999 });

    assert.equal(res.status, 404);
    assert.equal(res.body.code, 'RECORDING_NOT_FOUND');
  });

  it('GET /api/predictions/history - returns empty array when no genuine predictions exist', async () => {
    const res = await request(app).get('/api/predictions/history');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.deepEqual(res.body.data, []);
  });

  it('POST /api/predictions - executes real inference and stores genuine prediction when model is connected', async () => {
    const isConnected = await modelAdapter.isModelConnected();
    if (!isConnected) return;

    const res = await request(app)
      .post('/api/predictions')
      .send({ ecgRecordingId: testRecordingId });

    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.predictedClass);
    assert.ok(typeof res.body.data.confidenceScore === 'number');

    const db = getDatabase();
    const rows = db.prepare('SELECT * FROM predictions').all();
    assert.ok(rows.length > 0, 'Genuine prediction record must be persisted to database');
  });
});
