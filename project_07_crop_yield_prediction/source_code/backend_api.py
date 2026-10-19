"""
CropAI — Flask REST API
=======================
Serves the React frontend (frontend/) and exposes ML endpoints powered by
the same models used in the Streamlit app.

Run:
    python backend_api.py

Then open http://localhost:5000

The first run trains all models on the full yield_df.csv (takes a few minutes,
SVR is the longest). Models are cached to models_cache.joblib for subsequent runs.

Endpoints
---------
GET  /                              -> frontend (index.html)
GET  /api/stats                     -> dataset stats {records, countries, crops, train_mean, ...}
GET  /api/options                   -> {countries: [...], crops: [...]}
GET  /api/models/regression         -> [{name, r2, mae, rmse, best, ...}, ...]
GET  /api/models/classification     -> [{name, acc, prec, rec, f1, cm, best, ...}, ...] (binary)
GET  /api/classification?type=binary|3class -> {type, labels, models[], best, thresholds, testN}
GET  /api/exploration               -> {stats, hist, yieldByCrop, topCountries, yoy, corr, preview, recent}
GET  /api/visualizations            -> {featImportance, scatter, yearlyPerf, kpis}
GET  /api/history?country=X&crop=Y  -> {years: [...], yields: [...]}
POST /api/predict                   -> regression prediction
POST /api/classify   {type: binary|3class} -> classification prediction
"""
import os
import sys
import json
import time
import warnings
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
import joblib

from flask import Flask, jsonify, request, send_from_directory, abort, Response
from flask_cors import CORS

import database

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (RandomForestRegressor, GradientBoostingRegressor,
                              RandomForestClassifier)
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error,
                             accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)

warnings.filterwarnings("ignore")

ROOT          = Path(__file__).parent
DATA_PATH     = ROOT / "data" / "yield_df.csv"
FRONTEND_DIR  = ROOT / "frontend"
CACHE_PATH    = ROOT / "models_cache.joblib"

# Bump this whenever the structure of the cached bundle changes so stale
# caches (e.g. ones trained before 3-class support) are rebuilt automatically.
CACHE_VERSION = 3


def _apply_poly(mat, entry, n_ohe):
    """If `entry` is a {model, poly} dict, expand the numeric columns of `mat`
    with its PolynomialFeatures; otherwise return `mat` unchanged."""
    if isinstance(entry, dict) and "poly" in entry:
        return np.concatenate(
            [mat[:, :n_ohe], entry["poly"].transform(mat[:, n_ohe:])], axis=1)
    return mat

# ─────────────────────────────────────────────────────────────────────
# Training pipeline
# ─────────────────────────────────────────────────────────────────────
def train_all_models(include_svr: bool = True):
    print("→ Loading dataset...")
    data = pd.read_csv(DATA_PATH)
    if "Unnamed: 0" in data.columns:
        data = data.drop(columns=["Unnamed: 0"])

    target_col = "hg/ha_yield"
    x_df = data.drop(columns=[target_col])
    y    = data[target_col].values
    feat_cols = x_df.columns.tolist()

    cat_cols    = x_df.select_dtypes(include="object").columns.tolist()
    cat_indices = [x_df.columns.get_loc(c) for c in cat_cols]

    ct = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(handle_unknown="ignore"), cat_indices)],
        remainder="passthrough",
    )
    x = ct.fit_transform(x_df)
    if hasattr(x, "toarray"):
        x = x.toarray()
    x = x.astype(float)

    n_ohe = len(ct.named_transformers_["encoder"].get_feature_names_out())
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

    sc = StandardScaler()
    x_train[:, n_ohe:] = sc.fit_transform(x_train[:, n_ohe:])
    x_test[:,  n_ohe:] = sc.transform(x_test[:, n_ohe:])

    results = {}
    models  = {}

    def evaluate(name, model, x_tr, x_te):
        t0 = time.time()
        model.fit(x_tr, y_train)
        y_pred = model.predict(x_te)
        elapsed = time.time() - t0
        r2   = float(r2_score(y_test, y_pred))
        mae  = float(mean_absolute_error(y_test, y_pred))
        mse  = float(mean_squared_error(y_test, y_pred))
        rmse = float(np.sqrt(mse))
        print(f"  ✓ {name:<32} R²={r2:.4f}  RMSE={rmse:>10,.0f}  ({elapsed:.1f}s)")
        results[name] = {"r2": r2, "mae": mae, "mse": mse, "rmse": rmse}
        models[name]  = model

    print("→ Training regression models...")
    evaluate("Linear Regression",     LinearRegression(),                              x_train, x_test)
    evaluate("Decision Tree",         DecisionTreeRegressor(random_state=0),           x_train, x_test)
    evaluate("Random Forest",         RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=-1), x_train, x_test)
    evaluate("Gradient Boosting",     GradientBoostingRegressor(random_state=0),       x_train, x_test)

    # Polynomial regressions (apply only to numerical columns)
    for deg in [2, 3]:
        pf = PolynomialFeatures(degree=deg, include_bias=False)
        x_num_tr_poly = pf.fit_transform(x_train[:, n_ohe:])
        x_num_te_poly = pf.transform(x_test[:, n_ohe:])
        x_tr_poly = np.concatenate([x_train[:, :n_ohe], x_num_tr_poly], axis=1)
        x_te_poly = np.concatenate([x_test[:,  :n_ohe], x_num_te_poly], axis=1)
        name = f"Polynomial Regression (deg={deg})"
        t0 = time.time()
        m = LinearRegression()
        m.fit(x_tr_poly, y_train)
        y_pred = m.predict(x_te_poly)
        elapsed = time.time() - t0
        r2   = float(r2_score(y_test, y_pred))
        mae  = float(mean_absolute_error(y_test, y_pred))
        mse  = float(mean_squared_error(y_test, y_pred))
        rmse = float(np.sqrt(mse))
        print(f"  ✓ {name:<32} R²={r2:.4f}  RMSE={rmse:>10,.0f}  ({elapsed:.1f}s)")
        results[name] = {"r2": r2, "mae": mae, "mse": mse, "rmse": rmse}
        models[name]  = {"model": m, "poly": pf}

    if include_svr:
        print("  (SVR may take 1-5 minutes — training...)")
        evaluate("SVR (RBF)", SVR(kernel="rbf"), x_train, x_test)

    # Baseline
    y_baseline = np.full_like(y_test, fill_value=np.mean(y_train), dtype=float)
    results["Baseline (mean)"] = {
        "r2"  : float(r2_score(y_test, y_baseline)),
        "mae" : float(mean_absolute_error(y_test, y_baseline)),
        "mse" : float(mean_squared_error(y_test, y_baseline)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_baseline))),
    }

    # ── Real artefacts for the Visualizations page (no mocks) ──
    best_reg_name  = max((k for k in results if k != "Baseline (mean)"),
                         key=lambda k: results[k]["r2"])
    best_reg_entry = models[best_reg_name]
    best_reg_model = best_reg_entry["model"] if isinstance(best_reg_entry, dict) else best_reg_entry

    # Actual vs predicted scatter — a random sample of the held-out test set
    y_pred_test = best_reg_model.predict(_apply_poly(x_test, best_reg_entry, n_ohe))
    rng = np.random.RandomState(0)
    sample_idx = rng.choice(len(y_test), size=min(400, len(y_test)), replace=False)
    scatter = [{"x": int(y_test[i]), "y": int(round(float(y_pred_test[i])))} for i in sample_idx]

    # Feature importance — readable names; prefer Random Forest's importances
    enc = ct.named_transformers_["encoder"]
    feat_names = []
    for ci, col in enumerate(cat_cols):
        for cat in enc.categories_[ci]:
            feat_names.append(f"{col} = {cat}")
    feat_names.extend([col for col in feat_cols if col not in cat_cols])

    imp_model = models.get("Random Forest")
    if not (imp_model is not None and hasattr(imp_model, "feature_importances_")):
        imp_model = best_reg_model if hasattr(best_reg_model, "feature_importances_") else None
    feat_importance = []
    if imp_model is not None and len(feat_names) == len(imp_model.feature_importances_):
        order = np.argsort(imp_model.feature_importances_)[::-1][:15]
        feat_importance = [{"f": feat_names[i], "v": float(imp_model.feature_importances_[i])}
                           for i in order]

    # Yearly actual vs predicted — best model over the full dataset
    x_scaled = x.copy()
    x_scaled[:, n_ohe:] = sc.transform(x[:, n_ohe:])
    pred_all = best_reg_model.predict(_apply_poly(x_scaled, best_reg_entry, n_ohe))
    yperf = pd.DataFrame({"Year": data["Year"].values, "actual": y, "pred": pred_all}) \
              .groupby("Year").mean().sort_index()
    yearly_perf = {
        "years"    : [int(v) for v in yperf.index],
        "actual"   : [int(v) for v in yperf["actual"]],
        "predicted": [int(v) for v in yperf["pred"]],
    }

    # ── Classification ──
    # The same four classifiers are trained twice: once on a binary target
    # (above / below the training mean) and once on a 3-class target
    # (low / medium / high by 33rd & 67th percentile). Confusion matrices and
    # F1 are stored for every model so the frontend can render them live.
    def build_classifiers():
        return {
            "Random Forest Classifier" : RandomForestClassifier(n_estimators=100, random_state=0, n_jobs=-1),
            "K-Nearest Neighbors (k=5)": KNeighborsClassifier(n_neighbors=5, metric="minkowski", p=2),
            "Logistic Regression"      : LogisticRegression(max_iter=300, random_state=0),
            "Naive Bayes"              : GaussianNB(),
        }

    def train_classifiers(y_labels, avg, tag):
        print(f"→ Training classification models ({tag})...")
        xtr, xte, ytr, yte = train_test_split(x, y_labels, test_size=0.25, random_state=0)
        scaler = StandardScaler()
        xtr[:, n_ohe:] = scaler.fit_transform(xtr[:, n_ohe:])
        xte[:, n_ohe:] = scaler.transform(xte[:, n_ohe:])

        results_d, models_d = {}, {}
        for name, clf in build_classifiers().items():
            t0 = time.time()
            clf.fit(xtr, ytr)
            y_pred = clf.predict(xte)
            acc  = float(accuracy_score(yte, y_pred))
            prec = float(precision_score(yte, y_pred, average=avg, zero_division=0))
            rec  = float(recall_score(yte, y_pred, average=avg, zero_division=0))
            f1   = float(f1_score(yte, y_pred, average=avg, zero_division=0))
            cm   = confusion_matrix(yte, y_pred).tolist()
            elapsed = time.time() - t0
            print(f"  ✓ {name:<32} acc={acc:.4f}  f1={f1:.4f}  ({elapsed:.1f}s)")
            results_d[name] = {"accuracy": acc, "precision": prec,
                               "recall": rec, "f1": f1, "cm": cm}
            models_d[name]  = clf
        return results_d, models_d, scaler, int(len(yte))

    # Binary: above / below the (full-data) mean
    threshold = float(np.mean(y))
    y_bin     = (y >= threshold).astype(int)
    clf_results, clf_models, sc_c, test_n_bin = train_classifiers(y_bin, "binary", "binary")

    # 3-class: low / medium / high by 33rd & 67th percentile
    q33 = float(np.quantile(y, 0.33))
    q67 = float(np.quantile(y, 0.67))
    y_3 = np.digitize(y, bins=[q33, q67]).astype(int)   # 0:<q33  1:q33–q67  2:>=q67
    clf3_results, clf3_models, sc_c3, test_n_3 = train_classifiers(y_3, "weighted", "3-class")

    train_mean = float(np.mean(y_train))

    bundle = {
        "version"            : CACHE_VERSION,
        "ct"                 : ct,
        "sc"                 : sc,
        "sc_c"               : sc_c,
        "sc_c3"              : sc_c3,
        "n_ohe"              : n_ohe,
        "feat_cols"          : feat_cols,
        "train_mean"         : train_mean,
        "threshold"          : threshold,
        "q33"                : q33,
        "q67"                : q67,
        "results"            : results,
        "models"             : models,
        "clf_results"        : clf_results,
        "clf_models"         : clf_models,
        "clf3_results"       : clf3_results,
        "clf3_models"        : clf3_models,
        "test_n_bin"         : test_n_bin,
        "test_n_3"           : test_n_3,
        "best_reg_name"      : best_reg_name,
        "scatter"            : scatter,
        "feat_importance"    : feat_importance,
        "yearly_perf"        : yearly_perf,
        "countries"          : sorted(data["Area"].unique().tolist()),
        "crops"              : sorted(data["Item"].unique().tolist()),
        "n_records"          : int(len(data)),
        "year_min"           : int(data["Year"].min()),
        "year_max"           : int(data["Year"].max()),
    }
    return bundle, data


def load_or_train():
    if CACHE_PATH.exists():
        print(f"→ Loading cached models from {CACHE_PATH.name}...")
        try:
            bundle = joblib.load(CACHE_PATH)
            if bundle.get("version") != CACHE_VERSION:
                raise ValueError(
                    f"cache version {bundle.get('version')} != {CACHE_VERSION}")
            data   = pd.read_csv(DATA_PATH)
            if "Unnamed: 0" in data.columns:
                data = data.drop(columns=["Unnamed: 0"])
            print(f"  ✓ Loaded {len(bundle['models'])} regression models + "
                  f"{len(bundle['clf_models'])} binary + {len(bundle['clf3_models'])} 3-class classifiers")
            return bundle, data
        except Exception as e:
            print(f"  ✗ Cache load failed / stale ({e}). Retraining...")
    # SVR is slow on 28k samples (1-5 min). Set INCLUDE_SVR=1 to enable it.
    include_svr = os.environ.get("INCLUDE_SVR", "0") == "1"
    if not include_svr:
        print("→ Skipping SVR (set INCLUDE_SVR=1 to enable). Faster startup.")
    bundle, data = train_all_models(include_svr=include_svr)
    print(f"→ Saving cache to {CACHE_PATH.name}...")
    joblib.dump(bundle, CACHE_PATH)
    return bundle, data


# ─────────────────────────────────────────────────────────────────────
# Flask app
# ─────────────────────────────────────────────────────────────────────
print("=" * 60)
print("CropAI Backend API")
print("=" * 60)
BUNDLE, DATA = load_or_train()
print("=" * 60)

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)


# ── Static frontend ──
@app.route("/")
def root():
    return send_from_directory(FRONTEND_DIR, "index.html")




# ── API: dataset stats ──
@app.route("/api/stats")
def api_stats():
    return jsonify({
        "records"   : BUNDLE["n_records"],
        "countries" : len(BUNDLE["countries"]),
        "crops"     : len(BUNDLE["crops"]),
        "yearMin"   : BUNDLE["year_min"],
        "yearMax"   : BUNDLE["year_max"],
        "trainMean" : BUNDLE["train_mean"],
    })


# ── API: dropdown options ──
@app.route("/api/options")
def api_options():
    return jsonify({
        "countries": BUNDLE["countries"],
        "crops"    : BUNDLE["crops"],
    })


# ── API: model performance ──
@app.route("/api/models/regression")
def api_models_regression():
    descs = {
        "Linear Regression"            : "Linear combination of all features",
        "Decision Tree"                : "Tree of binary feature decisions",
        "Random Forest"                : "Ensemble of 100 decision trees with bagging",
        "Gradient Boosting"            : "Sequential trees correcting residual errors",
        "Polynomial Regression (deg=2)": "Quadratic feature expansion",
        "Polynomial Regression (deg=3)": "Captures non-linear feature relationships",
        "SVR (RBF)"                    : "Support Vector Regression with RBF kernel",
        "Baseline (mean)"              : "Always predicts the training mean",
    }
    icons = {
        "Linear Regression": "line", "Decision Tree": "tree", "Random Forest": "forest",
        "Gradient Boosting": "boost", "Polynomial Regression (deg=2)": "poly2",
        "Polynomial Regression (deg=3)": "poly3", "SVR (RBF)": "svr", "Baseline (mean)": "base",
    }
    # Determine best (highest R² excluding baseline)
    non_baseline = {k: v for k, v in BUNDLE["results"].items() if k != "Baseline (mean)"}
    best = max(non_baseline, key=lambda k: non_baseline[k]["r2"])

    out = []
    for name, m in BUNDLE["results"].items():
        out.append({
            "name"    : name,
            "r2"      : round(m["r2"], 4),
            "mae"     : round(m["mae"], 0),
            "rmse"    : round(m["rmse"], 0),
            "desc"    : descs.get(name, ""),
            "icon"    : icons.get(name, "line"),
            "best"    : name == best,
            "baseline": name == "Baseline (mean)",
        })
    out.sort(key=lambda x: (x["baseline"], -x["r2"]))
    return jsonify(out)


CLF_DESCS = {
    "Random Forest Classifier" : "Ensemble vote of 100 decision trees",
    "K-Nearest Neighbors (k=5)": "Majority vote of 5 closest neighbours",
    "Logistic Regression"      : "Sigmoid over a linear feature combination",
    "Naive Bayes"              : "Bayes' theorem with feature independence",
}
CLF_ICONS = {
    "Random Forest Classifier" : "forest",
    "K-Nearest Neighbors (k=5)": "knn",
    "Logistic Regression"      : "sigmoid",
    "Naive Bayes"              : "bayes",
}


def _clf_models_payload(results):
    """Turn a {name: metrics} dict into a sorted list of frontend model cards."""
    best = max(results, key=lambda k: results[k]["accuracy"])
    out  = []
    for name, m in results.items():
        out.append({
            "name": name,
            "acc" : round(m["accuracy"],  4),
            "prec": round(m["precision"], 4),
            "rec" : round(m["recall"],    4),
            "f1"  : round(m.get("f1", 0.0), 4),
            "cm"  : m.get("cm"),
            "desc": CLF_DESCS.get(name, ""),
            "icon": CLF_ICONS.get(name, "forest"),
            "best": name == best,
        })
    out.sort(key=lambda x: -x["acc"])
    return out, best


@app.route("/api/models/classification")
def api_models_classification():
    # Backwards-compatible: returns the binary classifier array (used by data.js).
    out, _ = _clf_models_payload(BUNDLE["clf_results"])
    return jsonify(out)


@app.route("/api/classification")
def api_classification():
    """Full classification payload for one target type (binary | 3class):
    model cards (with confusion matrices), class labels, and band thresholds."""
    ctype = request.args.get("type", "binary")
    if ctype == "3class":
        out, best = _clf_models_payload(BUNDLE["clf3_results"])
        return jsonify({
            "type"  : "3class",
            "labels": ["Low", "Medium", "High"],
            "models": out,
            "best"  : best,
            "q33"   : round(BUNDLE["q33"], 1),
            "q67"   : round(BUNDLE["q67"], 1),
            "testN" : BUNDLE["test_n_3"],
        })
    out, best = _clf_models_payload(BUNDLE["clf_results"])
    return jsonify({
        "type"     : "binary",
        "labels"   : ["Below Avg", "Above Avg"],
        "models"   : out,
        "best"     : best,
        "threshold": round(BUNDLE["threshold"], 1),
        "testN"    : BUNDLE["test_n_bin"],
    })


# ── API: historical yield (dataset trend OR SQLite persistent history) ──
@app.route("/api/history", methods=["GET", "DELETE"])
def api_history():
    if request.method == "DELETE":
        database.clear_history()
        return jsonify({"success": True, "message": "Prediction history cleared"})

    country = request.args.get("country")
    crop    = request.args.get("crop")
    if country or crop:
        if not country or not crop:
            return jsonify({"error": "Both country and crop are required for dataset history"}), 400
        subset = DATA[(DATA["Area"] == country) & (DATA["Item"] == crop)]
        if subset.empty:
            return jsonify({"years": [], "yields": [], "empty": True})
        agg = subset.groupby("Year")["hg/ha_yield"].mean().sort_index()
        return jsonify({
            "years" : agg.index.astype(int).tolist(),
            "yields": [int(v) for v in agg.values],
            "empty" : False,
        })

    # Return persistent SQLite prediction history
    try:
        limit = max(1, min(500, int(request.args.get("limit", 50))))
    except ValueError:
        limit = 50
    records = database.get_history(limit=limit)
    return jsonify({"records": records, "count": len(records)})


@app.route("/api/history/<int:pred_id>", methods=["GET", "DELETE"])
def api_history_item(pred_id):
    if request.method == "DELETE":
        deleted = database.delete_prediction(pred_id)
        if not deleted:
            return jsonify({"error": f"Prediction with ID {pred_id} not found"}), 404
        return jsonify({"success": True, "message": f"Prediction {pred_id} deleted"})

    record = database.get_prediction_by_id(pred_id)
    if not record:
        return jsonify({"error": f"Prediction with ID {pred_id} not found"}), 404
    return jsonify(record)


@app.route("/api/history/export")
def api_history_export():
    csv_data = database.export_history_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=cropai_history.csv"}
    )


@app.route("/api/prediction-history")
def api_prediction_history():
    try:
        limit = max(1, min(500, int(request.args.get("limit", 50))))
    except ValueError:
        limit = 50
    records = database.get_history(limit=limit)
    return jsonify({"records": records, "count": len(records)})



# ── API: searchable records (powers the Data Exploration search box) ──
@app.route("/api/records")
def api_records():
    q     = (request.args.get("q") or "").strip().lower()
    try:
        limit = max(1, min(200, int(request.args.get("limit", 25))))
    except ValueError:
        limit = 25

    d = DATA
    if q:
        mask = (d["Area"].str.lower().str.contains(q, regex=False)
                | d["Item"].str.lower().str.contains(q, regex=False)
                | d["Year"].astype(str).str.contains(q, regex=False))
        d = d[mask]

    total = int(len(d))
    rows = [[r["Area"], r["Item"], int(r["Year"]),
             float(r["average_rain_fall_mm_per_year"]), float(r["pesticides_tonnes"]),
             float(r["avg_temp"]), int(r["hg/ha_yield"])]
            for _, r in d.head(limit).iterrows()]
    return jsonify({"rows": rows, "total": total, "shown": len(rows), "q": q})


# ── API: exploration page (histogram, heatmap, top lists, preview) ──
@app.route("/api/exploration")
def api_exploration():
    d    = DATA
    tcol = "hg/ha_yield"
    y    = d[tcol]

    edges  = [0, 25000, 50000, 75000, 100000, 150000, 200000, 300000, float("inf")]
    labels = ["0–25k", "25–50k", "50–75k", "75–100k", "100–150k", "150–200k", "200–300k", "300k+"]
    counts = [int(((y >= edges[i]) & (y < edges[i + 1])).sum()) for i in range(len(edges) - 1)]

    by_crop = y.groupby(d["Item"]).mean().sort_values(ascending=False)
    top_c   = d.groupby("Area")[tcol].mean().sort_values(ascending=False).head(10)
    yg      = d.groupby("Year")[tcol].mean().sort_index()

    corr_cols   = ["Year", "average_rain_fall_mm_per_year", "pesticides_tonnes", "avg_temp", tcol]
    cm          = d[corr_cols].corr().round(2)
    corr_labels = ["Year", "Rainfall", "Pesticides", "Temp", "Yield"]
    corr        = [[float(cm.iloc[i, j]) for j in range(len(corr_cols))] for i in range(len(corr_cols))]

    preview = [[r["Area"], r["Item"], int(r["Year"]),
                float(r["average_rain_fall_mm_per_year"]), float(r["pesticides_tonnes"]),
                float(r["avg_temp"]), int(r[tcol])]
               for _, r in d.head(10).iterrows()]

    mean   = float(y.mean())
    recent = [{"time": str(int(r["Year"])), "country": r["Area"], "crop": r["Item"],
               "yield": int(r[tcol]), "status": "above" if r[tcol] >= mean else "below"}
              for _, r in d.sample(3, random_state=0).iterrows()]

    return jsonify({
        "stats"       : {"records": int(len(d)), "countries": int(d["Area"].nunique()),
                         "crops": int(d["Item"].nunique()), "missing": int(d.isnull().sum().sum())},
        "mean"        : round(mean, 0),
        "median"      : round(float(y.median()), 0),
        "hist"        : {"labels": labels, "counts": counts},
        "yieldByCrop" : [{"crop": k, "val": int(v)} for k, v in by_crop.items()],
        "topCountries": [{"c": k, "v": int(v)} for k, v in top_c.items()],
        "yoy"         : {"years": [int(k) for k in yg.index], "vals": [int(v) for v in yg.values]},
        "corrLabels"  : corr_labels,
        "corr"        : corr,
        "preview"     : preview,
        "recent"      : recent,
    })


# ── API: visualizations page (feature importance, scatter, KPIs) ──
@app.route("/api/visualizations")
def api_visualizations():
    results      = BUNDLE["results"]
    non_baseline = {k: v for k, v in results.items() if k != "Baseline (mean)"}
    best_r2   = max(non_baseline, key=lambda k: non_baseline[k]["r2"])
    low_rmse  = min(non_baseline, key=lambda k: non_baseline[k]["rmse"])
    best_acc  = max(BUNDLE["clf_results"], key=lambda k: BUNDLE["clf_results"][k]["accuracy"])

    return jsonify({
        "featImportance": BUNDLE.get("feat_importance", []),
        "scatter"       : BUNDLE.get("scatter", []),
        "yearlyPerf"    : BUNDLE.get("yearly_perf", {}),
        "bestModel"     : BUNDLE.get("best_reg_name", best_r2),
        "kpis": {
            "bestR2"      : round(non_baseline[best_r2]["r2"], 4),  "bestR2Model": best_r2,
            "lowRmse"     : round(non_baseline[low_rmse]["rmse"], 0), "lowRmseModel": low_rmse,
            "bestAcc"     : round(BUNDLE["clf_results"][best_acc]["accuracy"], 4), "bestAccModel": best_acc,
        },
    })


# ── Helper: input validation ──
def validate_agricultural_inputs(body, is_recommendation=False):
    """
    Validates input parameters for prediction and recommendation endpoints.
    Returns: (clean_dict, error_message)
    """
    if not isinstance(body, dict):
        return None, "Request body must be a valid JSON object."

    required_fields = ["country", "year", "rain", "pest", "temp"]
    if not is_recommendation:
        required_fields.append("crop")

    for f in required_fields:
        if f not in body or body[f] is None or (isinstance(body[f], str) and body[f].strip() == ""):
            return None, f"Missing required parameter: '{f}'"

    # Country validation
    country = str(body["country"]).strip()
    if country not in BUNDLE["countries"]:
        return None, f"Unsupported country: '{country}'. Please select a supported country."

    # Crop validation
    crop = None
    if not is_recommendation:
        crop = str(body["crop"]).strip()
        if crop not in BUNDLE["crops"]:
            return None, f"Unsupported crop: '{crop}'. Supported crops: {', '.join(BUNDLE['crops'])}."

    # Year validation
    try:
        year = int(body["year"])
    except (ValueError, TypeError):
        return None, "Parameter 'year' must be an integer."
    if year < 1900 or year > 2100:
        return None, "Parameter 'year' must be between 1900 and 2100."

    # Rainfall validation
    try:
        rain = float(body["rain"])
    except (ValueError, TypeError):
        return None, "Parameter 'rain' (rainfall in mm/year) must be a numeric value."
    if not np.isfinite(rain):
        return None, "Parameter 'rain' must be a finite number."
    if rain < 0.0:
        return None, "Rainfall cannot be negative (must be >= 0 mm/year)."
    if rain > 12000.0:
        return None, "Rainfall exceeds realistic annual limit (maximum 12,000 mm/year)."

    # Pesticides validation
    try:
        pest = float(body["pest"])
    except (ValueError, TypeError):
        return None, "Parameter 'pest' (pesticides in tonnes) must be a numeric value."
    if not np.isfinite(pest):
        return None, "Parameter 'pest' must be a finite number."
    if pest < 0.0:
        return None, "Pesticides usage cannot be negative (must be >= 0 tonnes)."
    if pest > 1000000.0:
        return None, "Pesticides usage exceeds realistic limit (maximum 1,000,000 tonnes)."

    # Temperature validation
    try:
        temp = float(body["temp"])
    except (ValueError, TypeError):
        return None, "Parameter 'temp' (temperature in °C) must be a numeric value."
    if not np.isfinite(temp):
        return None, "Parameter 'temp' must be a finite number."
    if temp < -30.0 or temp > 65.0:
        return None, "Temperature must be within realistic agricultural limits (-30.0°C to 65.0°C)."

    clean = {
        "country": country,
        "year": year,
        "rain": rain,
        "pest": pest,
        "temp": temp,
    }
    if crop is not None:
        clean["crop"] = crop

    # Farm area validation (optional)
    raw_area = body.get("farm_area")
    if raw_area is not None and str(raw_area).strip() != "":
        try:
            farm_area = float(raw_area)
        except (ValueError, TypeError):
            return None, "Parameter 'farm_area' must be a numeric value."
        if not np.isfinite(farm_area):
            return None, "Parameter 'farm_area' must be a finite number."
        if farm_area <= 0.0:
            return None, "Cultivated farm area must be greater than 0."
        if farm_area > 10000000.0:
            return None, "Cultivated farm area exceeds realistic maximum (10,000,000)."

        raw_unit = str(body.get("farm_area_unit", "ha")).strip().lower()
        if raw_unit in ["ha", "hectare", "hectares"]:
            farm_unit = "ha"
        elif raw_unit in ["acres", "acre", "ac"]:
            farm_unit = "acres"
        else:
            return None, "Invalid farm area unit. Supported units are 'ha' (hectares) or 'acres'."

        clean["farm_area"] = farm_area
        clean["farm_area_unit"] = farm_unit
    else:
        clean["farm_area"] = None
        clean["farm_area_unit"] = None

    return clean, None


# ── Helper: encode a sample for prediction ──
def encode_sample(country, crop, year, rain, pest, temp, scaler):
    feat_cols = BUNDLE["feat_cols"]
    raw = pd.DataFrame({
        "Area"                          : [country],
        "Item"                          : [crop],
        "Year"                          : [int(year)],
        "average_rain_fall_mm_per_year" : [float(rain)],
        "pesticides_tonnes"             : [float(pest)],
        "avg_temp"                      : [float(temp)],
    })[feat_cols]
    enc = BUNDLE["ct"].transform(raw)
    if hasattr(enc, "toarray"):
        enc = enc.toarray()
    enc = enc.astype(float)
    n_ohe = BUNDLE["n_ohe"]
    enc[:, n_ohe:] = scaler.transform(enc[:, n_ohe:])
    return enc


# ── API: regression prediction ──
@app.route("/api/predict", methods=["POST"])
def api_predict():
    body = request.get_json(silent=True)
    if body is None:
        body = request.get_json(force=True, silent=True) or {}

    clean, err = validate_agricultural_inputs(body, is_recommendation=False)
    if err:
        return jsonify({"error": err}), 400

    model_name = body.get("model", "Random Forest")
    if model_name not in BUNDLE["models"]:
        return jsonify({"error": f"Unknown model: '{model_name}'. Available: {list(BUNDLE['models'].keys())}"}), 400

    encoded = encode_sample(clean["country"], clean["crop"], clean["year"],
                            clean["rain"], clean["pest"], clean["temp"],
                            BUNDLE["sc"])

    entry = BUNDLE["models"][model_name]
    if isinstance(entry, dict) and "poly" in entry:
        n_ohe = BUNDLE["n_ohe"]
        ohe_part  = encoded[:, :n_ohe]
        poly_part = entry["poly"].transform(encoded[:, n_ohe:])
        x_in      = np.concatenate([ohe_part, poly_part], axis=1)
        pred_yield = float(entry["model"].predict(x_in)[0])
    else:
        pred_yield = float(entry.predict(encoded)[0])

    train_mean = BUNDLE["train_mean"]
    pct = (pred_yield - train_mean) / train_mean * 100.0

    # Pull model R² for "confidence" proxy
    r2 = BUNDLE["results"].get(model_name, {}).get("r2", 0.9)
    confidence = max(50, min(99, int(round(r2 * 100))))

    # Comparable historical records
    subset = DATA[(DATA["Area"] == clean["country"]) & (DATA["Item"] == clean["crop"])]
    comparables = int(len(subset))

    # Phase 2: Cultivated farm area & total harvest calculation
    # 1 tonne = 10,000,000 hg
    # 1 hectare = 2.47105 acres (approx)
    yield_tonnes_per_ha = pred_yield / 10000000.0
    farm_area = clean["farm_area"]
    farm_area_unit = clean["farm_area_unit"]
    farm_area_ha = None
    total_harvest_tonnes = None

    if farm_area is not None:
        farm_area_ha = farm_area / 2.47105 if farm_area_unit == "acres" else farm_area
        total_harvest_tonnes = yield_tonnes_per_ha * farm_area_ha

    # Phase 3: Persistent SQLite history
    try:
        pred_id = database.save_prediction(
            task_type="regression",
            country=clean["country"],
            crop=clean["crop"],
            year=clean["year"],
            rainfall=clean["rain"],
            pesticides=clean["pest"],
            temperature=clean["temp"],
            model_name=model_name,
            predicted_yield=pred_yield,
            yield_unit="hg/ha",
            yield_tonnes_per_ha=yield_tonnes_per_ha,
            farm_area=farm_area,
            farm_area_unit=farm_area_unit,
            farm_area_ha=farm_area_ha,
            total_harvest_tonnes=total_harvest_tonnes,
        )
    except Exception as e:
        print(f"Warning: could not save prediction to SQLite ({e})")
        pred_id = None

    res = {
        "id"                 : pred_id,
        "yield"              : round(pred_yield, 1),
        "unit"               : "hg/ha",
        "yield_tonnes_per_ha": round(yield_tonnes_per_ha, 6),
        "trainMean"          : round(train_mean, 1),
        "percentDiff"        : round(pct, 2),
        "above"              : pred_yield >= train_mean,
        "model"              : model_name,
        "confidence"         : confidence,
        "comparables"        : comparables,
        "farm_area"          : farm_area,
        "farm_area_unit"     : farm_area_unit,
        "farm_area_ha"       : round(farm_area_ha, 4) if farm_area_ha is not None else None,
        "total_harvest_tonnes": round(total_harvest_tonnes, 4) if total_harvest_tonnes is not None else None,
        "harvest_calculation_note": "Total harvest (metric tonnes) = Yield (tonnes/ha) × Cultivated area (ha), where 1 tonne = 10,000,000 hg and 1 ha ≈ 2.47105 acres." if farm_area is not None else None,
    }
    return jsonify(res)


# ── API: classification prediction ──
@app.route("/api/classify", methods=["POST"])
def api_classify():
    body = request.get_json(silent=True)
    if body is None:
        body = request.get_json(force=True, silent=True) or {}

    clean, err = validate_agricultural_inputs(body, is_recommendation=False)
    if err:
        return jsonify({"error": err}), 400

    ctype = body.get("type", "binary")

    if ctype == "3class":
        model_name = body.get("model", "Random Forest Classifier")
        if model_name not in BUNDLE["clf3_models"]:
            return jsonify({"error": f"Unknown classifier: '{model_name}'"}), 400
        encoded = encode_sample(clean["country"], clean["crop"], clean["year"],
                                clean["rain"], clean["pest"], clean["temp"],
                                BUNDLE["sc_c3"])
        cls    = int(BUNDLE["clf3_models"][model_name].predict(encoded)[0])
        labels = ["Low", "Medium", "High"]
        label  = labels[cls]

        try:
            pred_id = database.save_prediction(
                task_type="classification",
                country=clean["country"],
                crop=clean["crop"],
                year=clean["year"],
                rainfall=clean["rain"],
                pesticides=clean["pest"],
                temperature=clean["temp"],
                model_name=model_name,
                classification_label=label,
                classification_class=cls,
                classification_type="3class",
            )
        except Exception as e:
            pred_id = None

        return jsonify({
            "id"   : pred_id,
            "class": cls,
            "label": label,
            "type" : "3class",
            "q33"  : round(BUNDLE["q33"], 1),
            "q67"  : round(BUNDLE["q67"], 1),
            "model": model_name,
        })

    model_name = body.get("model", "Random Forest Classifier")
    if model_name not in BUNDLE["clf_models"]:
        return jsonify({"error": f"Unknown classifier: '{model_name}'"}), 400

    encoded = encode_sample(clean["country"], clean["crop"], clean["year"],
                            clean["rain"], clean["pest"], clean["temp"],
                            BUNDLE["sc_c"])

    clf = BUNDLE["clf_models"][model_name]
    cls = int(clf.predict(encoded)[0])
    label = "Above Average" if cls == 1 else "Below Average"

    try:
        pred_id = database.save_prediction(
            task_type="classification",
            country=clean["country"],
            crop=clean["crop"],
            year=clean["year"],
            rainfall=clean["rain"],
            pesticides=clean["pest"],
            temperature=clean["temp"],
            model_name=model_name,
            classification_label=label,
            classification_class=cls,
            classification_type="binary",
        )
    except Exception as e:
        pred_id = None

    return jsonify({
        "id"       : pred_id,
        "class"    : cls,
        "label"    : label,
        "type"     : "binary",
        "threshold": round(BUNDLE["threshold"], 1),
        "model"    : model_name,
    })


# ── API: crop recommendation engine (Phase 4) ──
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    body = request.get_json(silent=True)
    if body is None:
        body = request.get_json(force=True, silent=True) or {}

    clean, err = validate_agricultural_inputs(body, is_recommendation=True)
    if err:
        return jsonify({"error": err}), 400

    model_name = body.get("model", "Random Forest")
    if model_name not in BUNDLE["models"]:
        model_name = "Random Forest" if "Random Forest" in BUNDLE["models"] else BUNDLE.get("best_reg_name", "Decision Tree")

    entry = BUNDLE["models"][model_name]
    country = clean["country"]
    year    = clean["year"]
    rain    = clean["rain"]
    pest    = clean["pest"]
    temp    = clean["temp"]
    farm_area = clean.get("farm_area")
    farm_unit = clean.get("farm_area_unit")

    farm_area_ha = None
    if farm_area is not None:
        farm_area_ha = farm_area / 2.47105 if farm_unit == "acres" else farm_area

    candidates = []
    for crop in BUNDLE["crops"]:
        encoded = encode_sample(country, crop, year, rain, pest, temp, BUNDLE["sc"])
        if isinstance(entry, dict) and "poly" in entry:
            n_ohe = BUNDLE["n_ohe"]
            ohe_part  = encoded[:, :n_ohe]
            poly_part = entry["poly"].transform(encoded[:, n_ohe:])
            x_in      = np.concatenate([ohe_part, poly_part], axis=1)
            pred_yield = float(entry["model"].predict(x_in)[0])
        else:
            pred_yield = float(entry.predict(encoded)[0])

        yield_t_ha = pred_yield / 10000000.0
        tot_harvest = round(yield_t_ha * farm_area_ha, 4) if farm_area_ha is not None else None

        candidates.append({
            "crop": crop,
            "predicted_yield": round(pred_yield, 1),
            "yield_tonnes_per_ha": round(yield_t_ha, 6),
            "total_harvest_tonnes": tot_harvest,
            "unit": "hg/ha",
        })

    # Sort descending by predicted yield
    candidates.sort(key=lambda x: -x["predicted_yield"])
    for idx, c in enumerate(candidates, start=1):
        c["rank"] = idx

    top3 = candidates[:3]
    return jsonify({
        "country": country,
        "year": year,
        "rainfall": rain,
        "pesticides": pest,
        "temperature": temp,
        "model": model_name,
        "unit": "hg/ha",
        "farm_area": farm_area,
        "farm_area_unit": farm_unit,
        "farm_area_ha": round(farm_area_ha, 4) if farm_area_ha is not None else None,
        "recommendations": top3,
        "all_ranked": candidates,
        "disclaimer": "Rankings are based strictly on predicted yield density (hg/ha) under the specified climate conditions. Note that yield density alone does not account for market price, cultivation costs, or specific soil properties."
    })



# ── Catch-all static proxy (must be after all /api/* routes) ──
@app.route("/<path:path>")
def static_proxy(path):
    target = FRONTEND_DIR / path
    if target.exists():
        return send_from_directory(FRONTEND_DIR, path)
    abort(404)


# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))
    print(f"\n→ Serving frontend at http://localhost:{port}")
    print(f"→ API base at      http://localhost:{port}/api")
    print("\nPress Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=port, debug=False)
