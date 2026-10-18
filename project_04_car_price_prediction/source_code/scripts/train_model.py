"""
Model Training and Evaluation Pipeline for Car Price Prediction.
Implements data preprocessing, outlier handling, feature encoding,
multi-algorithm benchmarking (Linear Regression, Decision Tree, Random Forest),
metric evaluation (R2, RMSE, MAE), and model serialization.
"""

import json
import logging
import os
import pickle
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

# Setup logging
_models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(_models_dir, exist_ok=True)
_log_file = os.path.join(_models_dir, "training.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_log_file, mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("CarPriceTrainer")


def extract_brand(car_name: str) -> str:
    """Extract standard brand name from car name string."""
    if not isinstance(car_name, str):
        return "Other"
    name = car_name.strip()
    first_word = name.split()[0]
    return first_word


def preprocess_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw dataset, drops rows missing target,
    and performs row-wise feature engineering (Car_Age, Brand).
    Imputation and scaling are handled within the Pipeline to prevent data leakage.
    """
    logger.info("Starting data preprocessing (leak-free row-wise transformations)...")
    df = raw_df.dropna(subset=["Selling_Price"]).copy()

    # Feature Engineering (purely row-wise, zero leakage across samples)
    current_year = 2024
    df["Car_Age"] = current_year - df["Year"]
    df["Brand"] = df["Car_Name"].apply(extract_brand)

    return df


def build_pipeline(regressor, numerical_cols, categorical_cols):
    """Creates an end-to-end Pipeline with preprocessing and regressor."""
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_cols),
            ("cat", categorical_transformer, categorical_cols)
        ]
    )

    full_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", regressor)
    ])

    return full_pipeline


def train_and_evaluate(dataset_path: str = "data/car_data.csv", models_dir: str = "models"):
    os.makedirs(models_dir, exist_ok=True)

    logger.info(f"Loading dataset from {dataset_path}...")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    raw_df = pd.read_csv(dataset_path)
    logger.info(f"Raw dataset shape: {raw_df.shape}")

    clean_df = preprocess_data(raw_df)

    # Define feature subsets
    numerical_cols = ["Car_Age", "Present_Price", "Kms_Driven", "Owner"]
    categorical_cols = ["Fuel_Type", "Seller_Type", "Transmission", "Brand"]
    feature_cols = numerical_cols + categorical_cols
    target_col = "Selling_Price"

    X = clean_df[feature_cols]
    y = clean_df[target_col]

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    logger.info(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Leak-free outlier handling: compute 99th percentile strictly from training set
    kms_99 = float(X_train["Kms_Driven"].dropna().quantile(0.99))
    logger.info(f"Train-derived Kms_Driven 99th-percentile cap: {kms_99:.0f} km")
    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train["Kms_Driven"] = np.clip(X_train["Kms_Driven"], 0, kms_99)
    X_test["Kms_Driven"] = np.clip(X_test["Kms_Driven"], 0, kms_99)

    # Candidate regression models
    candidate_models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regression": DecisionTreeRegressor(
            max_depth=7, min_samples_split=4, random_state=42
        ),
        "Random Forest Regression": RandomForestRegressor(
            n_estimators=150, max_depth=12, min_samples_split=3, random_state=42
        )
    }

    results = {}
    fitted_pipelines = {}

    for name, model in candidate_models.items():
        logger.info(f"Training {name}...")
        pipeline = build_pipeline(model, numerical_cols, categorical_cols)
        pipeline.fit(X_train, y_train)

        # Predictions
        y_train_pred = pipeline.predict(X_train)
        y_test_pred = pipeline.predict(X_test)

        # Metrics
        train_r2 = float(r2_score(y_train, y_train_pred))
        test_r2 = float(r2_score(y_test, y_test_pred))
        test_mae = float(mean_absolute_error(y_test, y_test_pred))
        test_rmse = float(np.sqrt(mean_squared_error(y_test, y_test_pred)))

        logger.info(
            f"[{name}] Test R²: {test_r2:.4f} | RMSE: {test_rmse:.4f} | MAE: {test_mae:.4f}"
        )

        results[name] = {
            "train_r2": round(train_r2, 4),
            "test_r2": round(test_r2, 4),
            "test_rmse": round(test_rmse, 4),
            "test_mae": round(test_mae, 4),
            "params": str(model.get_params())
        }

        fitted_pipelines[name] = pipeline

        # Save individual model pipeline
        slug = name.lower().replace(" ", "_")
        joblib.dump(pipeline, os.path.join(models_dir, f"{slug}.joblib"))

    # Select best model based on highest test R²
    best_model_name = max(results.keys(), key=lambda k: results[k]["test_r2"])
    best_pipeline = fitted_pipelines[best_model_name]
    logger.info(f"==> Best Model Selected: {best_model_name} (R²: {results[best_model_name]['test_r2']})")

    # Serialize best model to standard paths
    best_model_path_joblib = os.path.join(models_dir, "best_car_price_model.joblib")
    best_model_path_pkl = os.path.join(models_dir, "best_car_price_model.pkl")
    joblib.dump(best_pipeline, best_model_path_joblib)
    with open(best_model_path_pkl, "wb") as f:
        pickle.dump(best_pipeline, f)

    # Extract feature list and categories for UI dropdowns
    available_brands = sorted(clean_df["Brand"].dropna().unique().tolist())
    fuel_types = sorted(clean_df["Fuel_Type"].dropna().unique().tolist())
    seller_types = sorted(clean_df["Seller_Type"].dropna().unique().tolist())
    transmissions = sorted(clean_df["Transmission"].dropna().unique().tolist())

    # Extract car models grouped by brand and price guidance
    models_by_brand = {}
    model_price_lookup = {}
    for car_name in clean_df["Car_Name"].dropna().unique():
        brand = extract_brand(car_name)
        parts = car_name.strip().split(" ", 1)
        model_sub = parts[1] if len(parts) > 1 else parts[0]
        if brand not in models_by_brand:
            models_by_brand[brand] = []
        if model_sub not in models_by_brand[brand]:
            models_by_brand[brand].append(model_sub)

    for brand in models_by_brand:
        models_by_brand[brand].sort()

    for name, grp in clean_df.groupby("Car_Name"):
        model_price_lookup[name] = round(float(grp["Present_Price"].dropna().median()), 2)

    # Compute Random Forest feature importance breakdown
    rf_pipeline = fitted_pipelines.get("Random Forest Regression")
    feature_importance_list = []
    if rf_pipeline and hasattr(rf_pipeline.named_steps["regressor"], "feature_importances_"):
        rf_model = rf_pipeline.named_steps["regressor"]
        preprocessor = rf_pipeline.named_steps["preprocessor"]
        raw_feature_names = preprocessor.get_feature_names_out()
        raw_importances = rf_model.feature_importances_

        parent_map = {}
        for fname, imp in zip(raw_feature_names, raw_importances):
            clean_name = fname.split("__")[-1]
            parent = None
            for base in ["Present_Price", "Car_Age", "Kms_Driven", "Owner", "Fuel_Type", "Seller_Type", "Transmission", "Brand"]:
                if clean_name.startswith(base):
                    parent = base
                    break
            parent = parent or clean_name
            parent_map[parent] = parent_map.get(parent, 0.0) + float(imp)

        label_map = {
            "Present_Price": "Showroom Price (Ex-Showroom)",
            "Car_Age": "Vehicle Age",
            "Kms_Driven": "Odometer (Kms Driven)",
            "Transmission": "Transmission Type",
            "Fuel_Type": "Fuel Powertrain",
            "Brand": "Manufacturer Brand",
            "Owner": "Previous Owners",
            "Seller_Type": "Seller Channel (Dealer vs Direct)"
        }

        feature_importance_list = [
            {
                "feature": label_map.get(k, k),
                "key": k,
                "importance_pct": round(v * 100, 2)
            }
            for k, v in sorted(parent_map.items(), key=lambda x: x[1], reverse=True)
        ]

    metadata = {
        "best_model": best_model_name,
        "metrics": results,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importances": feature_importance_list,
        "numerical_features": numerical_cols,
        "categorical_features": categorical_cols,
        "models_by_brand": models_by_brand,
        "model_price_lookup": model_price_lookup,
        "categorical_options": {
            "Brand": available_brands,
            "Fuel_Type": fuel_types,
            "Seller_Type": seller_types,
            "Transmission": transmissions,
            "Owner": [0, 1, 2, 3]
        },
        "stats": {
            "min_year": int(clean_df["Year"].dropna().min()),
            "max_year": int(clean_df["Year"].dropna().max()),
            "min_present_price": float(clean_df["Present_Price"].dropna().min()),
            "max_present_price": float(clean_df["Present_Price"].dropna().max()),
            "avg_present_price": float(clean_df["Present_Price"].dropna().mean()),
            "min_selling_price": float(clean_df["Selling_Price"].dropna().min()),
            "max_selling_price": float(clean_df["Selling_Price"].dropna().max()),
            "avg_selling_price": float(clean_df["Selling_Price"].dropna().mean()),
        }
    }

    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Model artifacts and metadata saved to '{models_dir}/'")
    return metadata


if __name__ == "__main__":
    train_and_evaluate()
