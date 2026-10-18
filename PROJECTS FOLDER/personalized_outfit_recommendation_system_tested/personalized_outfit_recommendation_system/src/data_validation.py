"""Dataset validation and schema checks for clothing catalog and preference data."""

import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from PIL import Image
import config

REQUIRED_CATALOGUE_COLUMNS = [
    "item_id",
    "item_name",
    "category",
    "subcategory",
    "description",
    "primary_color",
    "secondary_color",
    "style_tags",
    "occasion",
    "fabric",
    "pattern",
    "fit",
    "season",
    "gender_or_style_category",
    "price",
    "image_path",
    "body_shape_tags",
    "undertone_color_tags",
]

REQUIRED_TRAINING_COLUMNS = [
    "body_shape",
    "skin_tone",
    "undertone",
    "preferred_style",
    "preferred_occasion",
    "preferred_colour",
    "budget_max",
    "preferred_clothing_category",
]


def validate_catalogue_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validates dataframe columns against required catalogue schema."""
    errors = []
    missing_cols = [c for c in REQUIRED_CATALOGUE_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required catalogue columns: {missing_cols}")

    if "item_id" in df.columns:
        dups = df["item_id"].duplicated().sum()
        if dups > 0:
            errors.append(f"Found {dups} duplicate item_id records.")

    if "price" in df.columns:
        invalid_prices = (df["price"] < 0).sum()
        if invalid_prices > 0:
            errors.append(f"Found {invalid_prices} negative price values.")

    return len(errors) == 0, errors


def validate_image_files(df: pd.DataFrame, base_dir: str = config.BASE_DIR) -> Dict[str, Any]:
    """Validates whether referenced images exist and can be loaded."""
    valid_count = 0
    missing_paths = []
    corrupted_files = []

    for _, row in df.iterrows():
        rel_path = str(row.get("image_path", ""))
        full_path = os.path.join(base_dir, rel_path) if not os.path.isabs(rel_path) else rel_path

        if not os.path.exists(full_path):
            missing_paths.append(rel_path)
            continue

        try:
            with Image.open(full_path) as img:
                img.verify()
            valid_count += 1
        except Exception as e:
            corrupted_files.append((rel_path, str(e)))

    return {
        "total_records": len(df),
        "valid_images": valid_count,
        "missing_images": len(missing_paths),
        "corrupted_images": len(corrupted_files),
        "missing_examples": missing_paths[:5],
        "corrupted_examples": corrupted_files[:5],
    }
