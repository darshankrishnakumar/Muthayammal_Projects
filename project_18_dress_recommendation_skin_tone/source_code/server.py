import os
import sys
import time
import json
import sqlite3
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(CURRENT_DIR, "personalized_outfit_recommendation_system")
sys.path.insert(0, PKG_DIR)

import config
from backend.recommendation_engine import HybridRecommendationEngine
from backend.profile_manager import ProfileManager
from backend.dataset_loader import load_catalogue
from backend.gbm_recommender import report_evaluation_metrics, predict_preferred_category
from backend.body_shape_analysis import analyze_body_shape
from backend.skin_tone_analysis import analyze_skin_tone

app = FastAPI(
    title="Skin Tone & Body Measurement Dress Recommendation System",
    description="Multi-Modal Hybrid Recommender Combining Gradient Boosting, TF-IDF Textual Modeling, and Color-Silhouette Rules",
    version="2.0.0"
)

# Static and Templates
app.mount("/static", StaticFiles(directory=os.path.join(CURRENT_DIR, "static")), name="static")
app.mount("/outfits", StaticFiles(directory=config.OUTFITS_DIR), name="outfits")
templates = Jinja2Templates(directory=os.path.join(CURRENT_DIR, "templates"))

# Initialize Recommender and Profile Manager
engine = HybridRecommendationEngine()
profile_manager = ProfileManager(config.DB_PATH)

def seed_history_if_needed():
    """Seeds historical recommendation records in SQLite if empty."""
    history = profile_manager.get_recommendation_history("user_default", limit=5)
    if not history:
        sample_seeds = [
            ("user_default", "OUTFIT_001", "Classic Crisp White Oxford Shirt", "Shirts", 0.94, "Strong textual alignment with classic style • Matches ML predicted category (Shirts) • Tailored for Medium skin tone & Hourglass"),
            ("user_default", "OUTFIT_003", "Charcoal Wool Tuxedo Blazer", "Formal wear", 0.91, "Matches Formal occasion • Color harmony for Cool Undertone • Structural lapels complement Pear silhouette"),
            ("user_default", "OUTFIT_007", "Emerald Green Wrap Maxi Dress", "Dresses", 0.88, "V-neck wrap enhances Hourglass waist • High contrast for Fair Warm tone • Formal evening elegance"),
            ("user_default", "OUTFIT_012", "Crimson Kanjeevaram Silk Saree", "Sarees", 0.96, "Rich traditional silk • Optimal jewel tone for Warm Olive skin • Premium ethnic wedding celebration"),
            ("user_default", "OUTFIT_016", "Sky Blue Breathable Linen Shirt", "Shirts", 0.87, "Breathable summer casual • Soft pastel palette for Cool Fair tone • Relaxed collar styling"),
            ("user_default", "OUTFIT_019", "Straight-Leg Dark Indigo Raw Denim", "Jeans", 0.89, "Classic dark wash denim • Balances Inverted Triangle proportions • Versatile weekend staple")
        ]
        for uid, oid, name, cat, score, rsn in sample_seeds:
            profile_manager.record_recommendation(uid, oid, name, cat, score, rsn)

seed_history_if_needed()

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Skin Tone & Body Measurement Dress Recommendation System",
        "port": 5018,
        "database": f"SQLite Connected ({os.path.basename(config.DB_PATH)})",
        "models": {
            "gbm_pipeline": "GradientBoostingClassifier (11 Garment Categories)",
            "tfidf_recommender": "TF-IDF Vectorizer + Cosine Similarity Matrix",
            "attribute_rules": "Skin Tone, Undertone & Body Silhouette Heuristic Rules Engine"
        },
        "catalogue_items_count": len(engine.catalogue)
    }

@app.get("/api/catalogue")
async def get_catalogue():
    catalogue_records = engine.catalogue.fillna("").to_dict(orient="records")
    return {"status": "success", "count": len(catalogue_records), "data": catalogue_records}

@app.get("/api/models")
async def get_model_evaluation():
    eval_metrics = report_evaluation_metrics()
    return {"status": "success", "metrics": eval_metrics}

@app.get("/api/history")
async def get_history(user_id: str = "user_default", limit: int = 50):
    records = profile_manager.get_recommendation_history(user_id=user_id, limit=limit)
    return {"status": "success", "count": len(records), "data": records}

@app.post("/api/recommend")
async def run_recommendation(
    skin_tone: str = Form("Medium"),
    undertone: str = Form("Warm"),
    body_shape: str = Form("Hourglass"),
    preferred_styles: str = Form("Classic"),
    preferred_occasions: str = Form("Formal"),
    preferred_colours: str = Form("Navy Blue"),
    preferred_categories: str = Form("All"),
    budget_max: float = Form(6000.0),
    query_text: Optional[str] = Form("")
):
    t0 = time.time()
    res = engine.recommend(
        skin_tone=skin_tone,
        undertone=undertone,
        body_shape=body_shape,
        preferred_styles=preferred_styles,
        preferred_occasions=preferred_occasions,
        preferred_colours=preferred_colours,
        preferred_categories=preferred_categories if preferred_categories != "All" else None,
        budget_max=budget_max,
        query_text=query_text,
        top_k=6
    )
    latency_ms = round((time.time() - t0) * 1000, 2)

    # Persist top recommendation to SQLite
    recs = res.get("recommendations", [])
    if recs:
        top = recs[0]
        profile_manager.record_recommendation(
            user_id="user_default",
            outfit_id=top.get("outfit_id", "N/A"),
            outfit_name=top.get("outfit_name", "N/A"),
            category=top.get("category", "General"),
            match_score=float(top.get("final_score", 0.0)),
            reason=top.get("summary_reason", "Matched via Multi-Modal Hybrid Engine")
        )

    return {
        "status": "success",
        "latency_ms": latency_ms,
        "gbm_predicted_category": res.get("gbm_predicted_category", "Shirts"),
        "gbm_confidence": round(float(res.get("gbm_confidence", 0.0)) * 100, 1),
        "applied_weights": res.get("applied_weights", {}),
        "total_candidates_analyzed": res.get("total_candidates", len(engine.catalogue)),
        "recommendations": recs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5018, reload=False)
