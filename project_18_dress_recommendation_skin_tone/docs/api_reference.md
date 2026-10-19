# REST API Reference & Specification

PROJECT-018 provides a high-speed RESTful JSON API on Port 5018.

## Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | GET | Renders main interactive fashion recommender dashboard |
| `GET /health` | GET | Service status, port allocation, and loaded models metadata |
| `POST /api/recommend` | POST | Executes multi-modal hybrid recommendation and logs to SQLite |
| `GET /api/catalogue` | GET | Returns complete 20+ garment catalogue with metadata |
| `GET /api/models` | GET | Returns evaluation metrics for the Gradient Boosting model |
| `GET /api/history` | GET | Retrieves historical recommendation transactions from SQLite |

---

### `POST /api/recommend`
Executes hybrid scoring across melanin depth, undertone, body silhouette, aesthetic style, and budget.

**Form Request Parameters:**
- `skin_tone`: `Fair`, `Medium`, `Olive`, `Deep`
- `undertone`: `Warm`, `Cool`, `Neutral`
- `body_shape`: `Hourglass`, `Pear`, `Rectangle`, `Inverted Triangle`, `Apple`
- `preferred_styles`: `Classic`, `Modern`, `Bohemian`, `Minimalist`
- `preferred_occasions`: `Formal`, `Casual`, `Party`, `Ethnic`
- `preferred_colours`: `Navy Blue`, `Emerald`, `Crimson`, `White`, `Charcoal`, `Pastel`
- `budget_max`: Maximum price limit (e.g. `6000`)
- `query_text`: Optional free-form semantic keywords (e.g. `wrap maxi dress`)

**Response Body (200 OK):**
```json
{
  "status": "success",
  "latency_ms": 11.2,
  "gbm_predicted_category": "Dresses",
  "gbm_confidence": 82.0,
  "applied_weights": {
    "tfidf": 0.35,
    "gbm": 0.30,
    "attributes": 0.35
  },
  "total_candidates_analyzed": 20,
  "recommendations": [
    {
      "outfit_id": "OUTFIT_007",
      "outfit_name": "Emerald Green Wrap Maxi Dress",
      "category": "Dresses",
      "price": 3499.0,
      "final_score": 0.96,
      "component_scores": {
        "tfidf_score": 0.95,
        "gbm_score": 0.92,
        "attribute_score": 1.0
      },
      "recommendation_reasons": [
        "Strong textual alignment with query (emerald wrap dress)",
        "Matches ML predicted category (Dresses)",
        "Tailored for Fair skin tone & Hourglass silhouette",
        "Ideal for Party (Classic style)"
      ]
    }
  ]
}
```
