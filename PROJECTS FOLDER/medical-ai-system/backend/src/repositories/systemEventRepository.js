import { getDatabase } from '../config/database.js';

export const systemEventRepository = {
  /**
   * Log non-sensitive system events (database, backend, storage, model).
   */
  create({ component, eventType, status }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO system_events (component, event_type, status)
      VALUES (?, ?, ?)
    `);

    const info = stmt.run(component, eventType, status);
    return {
      id: info.lastInsertRowid,
      component,
      eventType,
      status,
    };
  },

  /**
   * Find recent system events.
   */
  findMany({ component, limit = 20, offset = 0 } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (component) {
      conditions.push('component = ?');
      params.push(component);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        id,
        component,
        event_type as eventType,
        status,
        created_at as createdAt
      FROM system_events
      ${whereClause}
      ORDER BY id DESC
      LIMIT ? OFFSET ?
    `).all(...params, limit, offset);
  },
};

export default systemEventRepository;
