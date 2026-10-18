"""
Dataset inspection and preprocessing pipeline for Child Gait Prediction.
Ensures zero data leakage by fitting transformers strictly on training splits.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer


INTENDED_FEATURES = [
    "heel_pressure",
    "toe_pressure",
    "tilt_angle",
    "step_duration",
    "stride_length",
    "walking_speed",
]

TARGET_CLASSES = ["Normal", "Diplegic", "Hemiplegic"]


@dataclass
class DatasetInspectionReport:
    filename: str
    num_rows: int
    num_columns: int
    column_names: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    duplicate_rows: int
    class_distribution: Optional[Dict[str, int]]
    candidate_target_column: Optional[str]
    numerical_features: List[str]
    categorical_features: List[str]
    unusable_columns: List[str]
    potential_leakage_columns: List[str]
    available_required_features: List[str]
    missing_required_features: List[str]
    is_suitable: bool
    suitability_summary: str

    def print_summary(self):
        print("=" * 60)
        print(f"DATASET INSPECTION REPORT: {self.filename}")
        print("=" * 60)
        print(f"Total Rows:    {self.num_rows}")
        print(f"Total Columns: {self.num_columns}")
        print(f"Duplicates:    {self.duplicate_rows}")
        print("\nColumns & Types:")
        for col, dtype in self.data_types.items():
            miss = self.missing_values.get(col, 0)
            print(f"  - {col} ({dtype}) | Missing: {miss}")
        print(f"\nCandidate Target Column: {self.candidate_target_column}")
        if self.class_distribution:
            print("Class Distribution:")
            for cls, count in self.class_distribution.items():
                print(f"  - {cls}: {count} ({count / self.num_rows * 100:.1f}%)")
        print("\nRequired Features Status:")
        print(f"  Available: {self.available_required_features}")
        print(f"  Missing:   {self.missing_required_features}")
        if self.potential_leakage_columns:
            print(f"\nPotential Leakage Columns: {self.potential_leakage_columns}")
        if self.unusable_columns:
            print(f"Unusable Columns: {self.unusable_columns}")
        print(f"\nProject Suitability: {'SUITABLE' if self.is_suitable else 'ACTION REQUIRED / UNSUITABLE'}")
        print(f"Summary: {self.suitability_summary}")
        print("=" * 60)


def inspect_dataset(filepath: str, target_col: Optional[str] = None) -> DatasetInspectionReport:
    """Inspects a user-provided dataset without modifying it and reports comprehensive diagnostics."""
    df = pd.read_csv(filepath)
    num_rows, num_cols = df.shape
    col_names = list(df.columns)
    dtypes = {c: str(df[c].dtype) for c in col_names}
    missing = df.isnull().sum().to_dict()
    duplicates = int(df.duplicated().sum())

    # Identify potential target
    candidate_target = target_col
    if not candidate_target:
        possible_targets = [c for c in col_names if any(k in c.lower() for k in ["gait", "class", "label", "pattern", "target", "diagnosis"])]
        if possible_targets:
            candidate_target = possible_targets[0]
        else:
            # fallback to last object column
            obj_cols = df.select_dtypes(include=["object", "category"]).columns
            if len(obj_cols) > 0:
                candidate_target = obj_cols[-1]

    class_dist = None
    if candidate_target and candidate_target in df.columns:
        class_dist = df[candidate_target].value_counts().to_dict()

    # Identify numerical and categorical
    numerical = list(df.select_dtypes(include=[np.number]).columns)
    if candidate_target in numerical:
        numerical.remove(candidate_target)
    categorical = list(df.select_dtypes(include=["object", "category"]).columns)
    if candidate_target in categorical:
        categorical.remove(candidate_target)

    # Detect unusable / ID columns
    unusable = []
    leakage = []
    for c in col_names:
        c_lower = c.lower()
        if any(id_kw in c_lower for id_kw in ["id", "identifier", "subject_id", "patient_id", "child_id", "index"]):
            unusable.append(c)
        elif any(leak_kw in c_lower for leak_kw in ["diagnosis_code", "outcome", "target_score"]) and c != candidate_target:
            leakage.append(c)

    # Check required features (case-insensitive fuzzy match)
    norm_cols = {c.lower().replace(" ", "_"): c for c in col_names}
    available_req = []
    missing_req = []
    for req in INTENDED_FEATURES:
        matched = False
        for n_col, orig_col in norm_cols.items():
            if req in n_col or n_col in req:
                available_req.append(orig_col)
                matched = True
                break
        if not matched:
            missing_req.append(req)

    # Evaluate suitability
    is_suitable = True
    reasons = []

    if num_rows < 15:
        is_suitable = False
        reasons.append("Sample size too small for statistical train/test evaluation.")
    if len(missing_req) > 0:
        is_suitable = False
        reasons.append(f"Missing required gait parameters: {missing_req}.")
    if not candidate_target:
        is_suitable = False
        reasons.append("No suitable classification target column found.")
    elif class_dist and len(class_dist) < 2:
        is_suitable = False
        reasons.append("Target column contains fewer than 2 distinct classes.")

    summary = "; ".join(reasons) if reasons else "Dataset contains required parameters and class labels to train the baseline model."

    return DatasetInspectionReport(
        filename=filepath,
        num_rows=num_rows,
        num_columns=num_cols,
        column_names=col_names,
        data_types=dtypes,
        missing_values=missing,
        duplicate_rows=duplicates,
        class_distribution=class_dist,
        candidate_target_column=candidate_target,
        numerical_features=numerical,
        categorical_features=categorical,
        unusable_columns=unusable,
        potential_leakage_columns=leakage,
        available_required_features=available_req,
        missing_required_features=missing_req,
        is_suitable=is_suitable,
        suitability_summary=summary,
    )


class GaitDataPreprocessor:
    """
    Leakage-free preprocessor that imputes and standardizes numerical features
    and encodes multiclass labels.
    """

    def __init__(self, feature_names: List[str]):
        self.feature_names = feature_names
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_fitted = False

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "GaitDataPreprocessor":
        X_selected = X[self.feature_names]
        X_imp = self.imputer.fit_transform(X_selected)
        self.scaler.fit(X_imp)

        if y is not None:
            self.label_encoder.fit(y)

        self.is_fitted = True
        return self

    def transform_features(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transforming features.")
        X_selected = X[self.feature_names]
        X_imp = self.imputer.transform(X_selected)
        return self.scaler.transform(X_imp)

    def transform_labels(self, y: pd.Series) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transforming labels.")
        return self.label_encoder.transform(y)

    def inverse_transform_labels(self, y_encoded: np.ndarray) -> np.ndarray:
        return self.label_encoder.inverse_transform(y_encoded)

    def transform_single_record(self, record_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single inference dictionary for prediction."""
        df = pd.DataFrame([record_dict])
        return self.transform_features(df)
