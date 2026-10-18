import recommendationRepository from '../repositories/recommendationRepository.js';
import { AppError } from '../utils/response.js';

export const recommendationService = {
  /**
   * Retrieve recommendations with optional category filtering.
   */
  getRecommendations({ category } = {}) {
    const rows = recommendationRepository.findMany({ category });

    return rows.map((r) => ({
      id: r.code || `RC-${String(r.id).padStart(2, '0')}`,
      numericId: r.id,
      category: r.category,
      kind: r.kind,
      title: r.title,
      explanation: r.description,
      nextStep: r.suggestedAction,
      related: r.related || 'Biometric monitoring',
      reviewStatus: r.reviewStatus,
      clinicalNotice: 'Illustrative educational guidance only. Not medical advice or diagnosis.',
    }));
  },

  /**
   * Retrieve single recommendation by ID or Code.
   */
  getRecommendationById(id) {
    const row = recommendationRepository.findByCodeOrId(id);
    if (!row) {
      throw new AppError(`Recommendation '${id}' not found.`, 404, 'RECOMMENDATION_NOT_FOUND');
    }

    return {
      id: row.code || `RC-${String(row.id).padStart(2, '0')}`,
      numericId: row.id,
      category: row.category,
      kind: row.kind,
      title: row.title,
      explanation: row.description,
      nextStep: row.suggestedAction,
      related: row.related,
      reviewStatus: row.reviewStatus,
      clinicalNotice: 'Illustrative educational guidance only. Not medical advice or diagnosis.',
    };
  },
};

export default recommendationService;
