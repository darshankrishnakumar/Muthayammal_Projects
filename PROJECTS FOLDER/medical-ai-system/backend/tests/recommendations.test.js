import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { initDatabase, closeDatabase } from '../src/config/database.js';
import createApp from '../src/app.js';

describe('Recommendations, Alerts & Reports Endpoints', () => {
  let app;

  before(() => {
    initDatabase(':memory:');
    app = createApp();
  });

  after(() => {
    closeDatabase();
  });

  it('GET /api/recommendations - returns reviewed illustrative recommendations', async () => {
    const res = await request(app).get('/api/recommendations');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.length >= 4);

    // Verify all recommendations are marked as illustrative
    res.body.data.forEach((r) => {
      assert.equal(r.reviewStatus, 'illustrative');
      assert.ok(r.explanation);
      assert.ok(r.nextStep);
    });
  });

  it('GET /api/recommendations - filters by category', async () => {
    const res = await request(app)
      .get('/api/recommendations')
      .query({ category: 'General wellness' });

    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    res.body.data.forEach((r) => {
      assert.equal(r.category, 'General wellness');
    });
  });

  it('GET /api/alerts - retrieves system and informational alerts', async () => {
    const res = await request(app).get('/api/alerts');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.length >= 2);
  });

  it('PATCH /api/alerts/:id/status - updates alert status', async () => {
    const res = await request(app)
      .patch('/api/alerts/AL-01/status')
      .send({ status: 'acknowledged' });

    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.equal(res.body.data.status, 'acknowledged');
  });

  it('GET /api/reports/summary - generates structured summary from genuine data', async () => {
    const res = await request(app).get('/api/reports/summary');
    assert.equal(res.status, 200);
    assert.equal(res.body.success, true);
    assert.ok(res.body.data.summary);
    assert.equal(res.body.data.systemNotes.cnnModelStatus, 'not_connected');
  });
});
