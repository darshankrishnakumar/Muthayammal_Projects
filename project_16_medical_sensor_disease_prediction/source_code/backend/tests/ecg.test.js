import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase, closeDatabase } from '../src/config/database.js';
import createApp from '../src/app.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe('ECG Recording Upload & Storage Endpoints', () => {
  let app;
  let testCsvPath;
  let invalidExtPath;
  let uploadedRecordingId;

  before(() => {
    initDatabase(':memory:');
    app = createApp();

    // Create a temporary valid ECG test CSV file
    testCsvPath = path.join(__dirname, 'temp_sample_ecg.csv');
    fs.writeFileSync(
      testCsvPath,
      'time_ms,lead_ii\n0,0.12\n4,0.15\n8,0.30\n12,0.85\n16,0.20\n20,-0.05\n'
    );

    // Create an unsupported extension file
    invalidExtPath = path.join(__dirname, 'temp_script.sh');
    fs.writeFileSync(invalidExtPath, '#!/bin/bash\necho "invalid"');
  });

  after(() => {
    closeDatabase();
    if (fs.existsSync(testCsvPath)) fs.unlinkSync(testCsvPath);
    if (fs.existsSync(invalidExtPath)) fs.unlinkSync(invalidExtPath);
  });

  it('POST /api/ecg/upload - uploads valid ECG file and saves metadata', async () => {
    const res = await request(app)
      .post('/api/ecg/upload')
      .attach('file', testCsvPath);

    assert.equal(res.status, 201);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.recordingId);
    assert.equal(res.body.data.originalFilename, 'temp_sample_ecg.csv');
    assert.equal(res.body.data.fileFormat, 'csv');
    assert.equal(res.body.data.uploadStatus, 'verified');

    uploadedRecordingId = res.body.data.id;
  });

  it('POST /api/ecg/upload - rejects unsupported file formats with 415', async () => {
    const res = await request(app)
      .post('/api/ecg/upload')
      .attach('file', invalidExtPath);

    assert.equal(res.status, 415);
    assert.equal(res.body.success, false);
    assert.equal(res.body.code, 'UNSUPPORTED_MEDIA_TYPE');
  });

  it('POST /api/ecg/upload - returns 400 when no file is attached', async () => {
    const res = await request(app).post('/api/ecg/upload');
    assert.equal(res.status, 400);
    assert.equal(res.body.success, false);
  });

  it('GET /api/ecg/recordings - lists uploaded recordings', async () => {
    const res = await request(app).get('/api/ecg/recordings');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.recordings.length > 0);
  });

  it('GET /api/ecg/recordings/:id - retrieves single recording metadata without exposing server path', async () => {
    const res = await request(app).get(`/api/ecg/recordings/${uploadedRecordingId}`);
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.id, uploadedRecordingId);
    assert.equal(res.body.data.filePath, undefined); // Path is never exposed publicly
  });

  it('GET /api/ecg/recordings/99999 - returns 404 for non-existent recording', async () => {
    const res = await request(app).get('/api/ecg/recordings/99999');
    assert.equal(res.status, 404);
    assert.equal(res.body.code, 'RECORDING_NOT_FOUND');
  });

  it('DELETE /api/ecg/recordings/:id - safely deletes recording file and metadata', async () => {
    const res = await request(app).delete(`/api/ecg/recordings/${uploadedRecordingId}`);
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.deleted, true);

    // Verify subsequent lookup yields 404
    const checkRes = await request(app).get(`/api/ecg/recordings/${uploadedRecordingId}`);
    assert.equal(checkRes.status, 404);
  });
});
