import recommendationService from '../services/recommendationService.js';
import { sendSuccess } from '../utils/response.js';

export const recommendationController = {
  async getRecommendations(req, res, next) {
    try {
      const recommendations = recommendationService.getRecommendations(req.query);
      return sendSuccess(res, recommendations, 'Recommendations retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },

  async getRecommendationById(req, res, next) {
    try {
      const recommendation = recommendationService.getRecommendationById(req.params.id);
      return sendSuccess(res, recommendation, 'Recommendation retrieved successfully.');
    } catch (err) {
      next(err);
    }
  },
};

export default recommendationController;
