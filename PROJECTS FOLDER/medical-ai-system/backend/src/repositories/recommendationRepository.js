import { getDatabase } from '../config/database.js';

export const recommendationRepository = {
  /**
   * Insert recommendation record.
   */
  create({
    code = null,
    category,
    kind = 'wellness',
    title,
    description,
    suggestedAction,
    related = null,
    sourceType = 'reviewed_guideline',
    reviewStatus = 'illustrative',
  }) {
    const db = getDatabase();
    const stmt = db.prepare(`
      INSERT INTO recommendations (
        code, category, kind, title, description, suggested_action,
        related, source_type, review_status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const info = stmt.run(
      code,
      category,
      kind,
      title,
      description,
      suggestedAction,
      related,
      sourceType,
      reviewStatus
    );

    return this.findById(info.lastInsertRowid);
  },

  /**
   * Find recommendation by ID.
   */
  findById(id) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        code,
        category,
        kind,
        title,
        description,
        suggested_action as suggestedAction,
        related,
        source_type as sourceType,
        review_status as reviewStatus,
        created_at as createdAt
      FROM recommendations
      WHERE id = ?
    `).get(id);
  },

  /**
   * Find recommendation by code or numeric ID.
   */
  findByCodeOrId(codeOrId) {
    const db = getDatabase();
    return db.prepare(`
      SELECT
        id,
        code,
        category,
        kind,
        title,
        description,
        suggested_action as suggestedAction,
        related,
        source_type as sourceType,
        review_status as reviewStatus,
        created_at as createdAt
      FROM recommendations
      WHERE id = ? OR code = ?
    `).get(codeOrId, codeOrId);
  },

  /**
   * Find recommendations with category and reviewStatus filtering.
   */
  findMany({ category, reviewStatus } = {}) {
    const db = getDatabase();
    const conditions = [];
    const params = [];

    if (category) {
      conditions.push('category = ?');
      params.push(category);
    }
    if (reviewStatus) {
      conditions.push('review_status = ?');
      params.push(reviewStatus);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    return db.prepare(`
      SELECT
        id,
        code,
        category,
        kind,
        title,
        description,
        description as explanation,
        suggested_action as suggestedAction,
        suggested_action as nextStep,
        related,
        source_type as sourceType,
        review_status as reviewStatus,
        created_at as createdAt
      FROM recommendations
      ${whereClause}
      ORDER BY id ASC
    `).all(...params);
  },

  /**
   * Count recommendations.
   */
  count() {
    const db = getDatabase();
    const row = db.prepare('SELECT COUNT(*) as total FROM recommendations').get();
    return row.total;
  },
};

export default recommendationRepository;
