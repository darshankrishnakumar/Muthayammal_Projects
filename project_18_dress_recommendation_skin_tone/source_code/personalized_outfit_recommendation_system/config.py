"""Central Configuration for Skin Tone Body Measurement Based Dress Recommendation."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SYNTHETIC_DATA_DIR = os.path.join(DATA_DIR, "synthetic")

CATALOGUE_PATH = os.path.join(DATA_DIR, "clothing_catalogue.csv")
SYNTHETIC_CATALOGUE_PATH = os.path.join(SYNTHETIC_DATA_DIR, "synthetic_clothing_catalogue.csv")
TRAINING_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "user_preference_training_data.csv")
DB_PATH = os.path.join(DATA_DIR, "user_data.db")
OUTFITS_DIR = os.path.join(BASE_DIR, "outfits")

# Models paths
MODELS_DIR = os.path.join(BASE_DIR, "models")
GBM_MODEL_PATH = os.path.join(MODELS_DIR, "gbm_pipeline.joblib")
MODEL_SAVE_PATH = GBM_MODEL_PATH
TFIDF_VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
TFIDF_MATRIX_PATH = os.path.join(MODELS_DIR, "tfidf_matrix.npz")
CLIP_CACHE_PATH = os.path.join(MODELS_DIR, "clip_embeddings", "catalog_embeddings.npz")
EVAL_METRICS_PATH = os.path.join(BASE_DIR, "reports", "gbm_evaluation.json")
EXPERIMENT_REPORT_PATH = os.path.join(BASE_DIR, "reports", "experiment_comparison.csv")

# Haar Cascade
HAARCASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")

# OpenVINO / MoveNet model paths
OV_MODELS_DIR = os.path.join(BASE_DIR, "ov_models")
OV_CLIP_PATH = os.path.join(OV_MODELS_DIR, "clip_image_encoder.xml")
OV_MOVENET_PATH = os.path.join(OV_MODELS_DIR, "saved_model.xml")

# CLIP Configuration
OPEN_CLIP_MODEL_NAME = "ViT-B-32"
OPEN_CLIP_PRETRAINED = "openai"

# Default Ensemble Weights (normalized to sum to 1.0)
DEFAULT_WEIGHTS = {
    "tfidf": 0.30,
    "clip": 0.30,
    "gbm": 0.25,
    "attributes": 0.15,
}

# Domain Attributes & Vocabulary
SUPPORTED_CATEGORIES = [
    "Shirts",
    "T-shirts",
    "Trousers",
    "Jeans",
    "Pants",
    "Chudidhar",
    "Kurtis",
    "Dresses",
    "Skirts",
    "Formal wear",
    "Casual wear",
    "Ethnic wear",
    "Party wear",
]

SUPPORTED_OCCASIONS = [
    "Casual",
    "College",
    "Office",
    "Party",
    "Wedding",
    "Traditional",
]

SUPPORTED_STYLES = [
    "Classic",
    "Minimalist",
    "Modern",
    "Ethnic",
    "Streetwear",
    "Bohemian",
    "Chic",
]

SUPPORTED_COLORS = [
    "White",
    "Blue",
    "Black",
    "Grey",
    "Beige",
    "Navy",
    "Red",
    "Emerald",
    "Maroon",
    "Teal",
    "Peach",
    "Pastel",
    "Yellow",
    "Olive",
    "Pink",
]

SUPPORTED_SKIN_TONES = [
    "Fair",
    "Medium",
    "Wheatish",
    "Dusky",
    "Dark",
]

SUPPORTED_UNDERTONES = [
    "Warm",
    "Cool",
    "Neutral",
]

SUPPORTED_BODY_SHAPES = [
    "Rectangle / Hourglass",
    "Triangle (Pear)",
    "Inverted Triangle",
    "Hourglass",
    "Rectangle",
]

SUPPORTED_FITS = [
    "Slim Fit",
    "Regular Fit",
    "Relaxed Fit",
    "Oversized",
    "Tailored",
]

SUPPORTED_SEASONS = [
    "Summer",
    "Winter",
    "Spring",
    "Autumn",
    "All-Season",
]
