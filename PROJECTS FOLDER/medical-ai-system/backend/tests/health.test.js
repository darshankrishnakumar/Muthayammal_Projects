import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { initDatabase, closeDatabase } from '../src/config/database.js';
import createApp from '../src/app.js';

describe('Health & Measurement Endpoints', () => {
  let app;

  before(() => {
    // In-memory isolated database for tests
    initDatabase(':memory:');
    app = createApp();
  });

  after(() => {
    closeDatabase();
  });

  it('GET /health - responds with 200 and healthy status', async () => {
    const res = await request(app).get('/health');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.status, 'healthy');
  });

  it('GET /api/system/status - responds with honest status without fake model', async () => {
    const res = await request(app).get('/api/system/status');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.backend, 'online');
    assert.equal(res.body.data.database, 'connected');
    assert.ok(['not_connected', 'connected'].includes(res.body.data.cnnModel));
  });

  it('POST /api/health/measurements - creates a valid heart rate measurement', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'heart_rate',
        value: 75,
        unit: 'bpm',
        source: 'manual',
        measuredAt: '2026-10-09T10:00:00.000Z',
      });

    assert.equal(res.status, 201);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.value, 75);
    assert.equal(res.body.data.unit, 'bpm');
    assert.equal(res.body.data.dataQualityStatus, 'valid');
  });

  it('POST /api/health/measurements - creates a valid blood pressure measurement', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'blood_pressure',
        systolic: 120,
        diastolic: 80,
        unit: 'mmHg',
        source: 'manual',
        measuredAt: '2026-10-09T10:15:00.000Z',
      });

    assert.equal(res.status, 201);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.systolic, 120);
    assert.equal(res.body.data.diastolic, 80);
  });

  it('POST /api/health/measurements - rejects physiologically implausible heart rate (< 30 or negative)', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'heart_rate',
        value: -10,
        unit: 'bpm',
        source: 'manual',
      });

    assert.equal(res.status, 400);
    assert.equal(res.body.success, false);
    assert.equal(res.body.code, 'VALIDATION_ERROR');
  });

  it('POST /api/health/measurements - rejects blood pressure where systolic <= diastolic', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'blood_pressure',
        systolic: 80,
        diastolic: 120,
        unit: 'mmHg',
      });

    assert.equal(res.status, 400);
    assert.equal(res.body.success, false);
  });

  it('POST /api/health/measurements - rejects SpO2 outside 0-100%', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'spo2',
        value: 125,
        unit: '%',
      });

    assert.equal(res.status, 400);
    assert.equal(res.body.success, false);
  });

  it('POST /api/health/measurements - accepts compound multi-sensor reading', async () => {
    const res = await request(app)
      .post('/api/health/measurements')
      .send({
        heartRate: 72,
        systolic: 118,
        diastolic: 78,
        spo2: 98,
        temperature: 36.6,
        source: 'manual',
      });

    assert.equal(res.status, 201);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.createdCount, 4);
  });

  it('GET /api/health/measurements - filters by date range', async () => {
    const res = await request(app)
      .get('/api/health/measurements')
      .query({ startDate: '2026-10-09', limit: 10 });

    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(Array.isArray(res.body.data.records));
  });

  it('GET /api/health/summary - returns metric aggregates and latest values', async () => {
    const res = await request(app).get('/api/health/summary');
    assert.equal(res.status, 200);
    assert.ok(res.body.data.heart_rate);
    assert.ok(res.body.data.blood_pressure);
  });

  it('GET /api/health/trends - returns time-series data for Recharts', async () => {
    const res = await request(app).get('/api/health/trends');
    assert.equal(res.status, 200);
    assert.ok(Array.isArray(res.body.data));
  });

  it('PUT /api/health/measurements/:id - updates an existing measurement', async () => {
    const postRes = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'heart_rate',
        value: 75,
        unit: 'bpm',
        source: 'manual',
      });
    const id = postRes.body.data.id;

    const putRes = await request(app)
      .put(`/api/health/measurements/${id}`)
      .send({ value: 82 });

    assert.equal(putRes.status, 200);
    assert.equal(putRes.body.data.value, 82);
  });

  it('DELETE /api/health/measurements/:id - safely deletes a measurement', async () => {
    const postRes = await request(app)
      .post('/api/health/measurements')
      .send({
        measurementType: 'heart_rate',
        value: 70,
        unit: 'bpm',
        source: 'manual',
      });
    const id = postRes.body.data.id;

    const delRes = await request(app).delete(`/api/health/measurements/${id}`);
    assert.equal(delRes.status, 200);
    assert.equal(delRes.body.data.deleted, true);

    const getRes = await request(app).get(`/api/health/measurements/${id}`);
    assert.equal(getRes.status, 404);
  });

  it('GET /api/unknown-endpoint - returns 404 JSON', async () => {
    const res = await request(app).get('/api/unknown-endpoint');
    assert.equal(res.status, 404);
    assert.equal(res.body.code, 'RESOURCE_NOT_FOUND');
  });
});
