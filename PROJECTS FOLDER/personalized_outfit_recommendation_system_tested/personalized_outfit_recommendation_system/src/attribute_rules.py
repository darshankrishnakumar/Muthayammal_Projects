"""Stage 8: Transparent, Editable Rule Engine for Color Harmony & Silhouette Compatibility."""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import config

# Documented Color Harmony Rules
UNDERTONE_COMPATIBLE_COLORS = {
    "Warm": ["Beige", "Olive", "Maroon", "Yellow", "Gold", "Peach", "Red", "White", "Black"],
    "Cool": ["Navy", "Blue", "Emerald", "Pastel", "Teal", "Grey", "Pink", "White", "Black"],
    "Neutral": config.SUPPORTED_COLORS,
}

# Silhouette Proportion Styling Guidelines (Suggestions, not mandatory rules)
BODY_SHAPE_COMPATIBLE_CATEGORIES = {
    "Hourglass": ["Dresses", "Sarees", "Formal wear", "Shirts", "Kurtis", "Trousers"],
    "Rectangle / Hourglass": ["Shirts", "T-shirts", "Trousers", "Jeans", "Dresses", "Kurtis", "Formal wear"],
    "Rectangle": ["Shirts", "T-shirts", "Jeans", "Trousers", "Kurtis"],
    "Triangle (Pear)": ["Dresses", "Kurtis", "Chudidhar", "Sarees", "Shirts"],
    "Inverted Triangle": ["Trousers", "Jeans", "Formal wear", "Dresses", "T-shirts"],
}


def calculate_attribute_compatibility_score(
    item: Dict[str, Any],
    skin_tone: Optional[str] = None,
    undertone: Optional[str] = None,
    body_shape: Optional[str] = None,
    preferred_colors: Optional[List[str]] = None,
    preferred_styles: Optional[List[str]] = None,
    preferred_occasion: Optional[str] = None,
    preferred_fit: Optional[str] = None,
    budget_max: Optional[float] = None,
) -> Tuple[float, List[str]]:
    """Calculates attribute compatibility score in [0.0, 1.0] and returns human-readable explanations."""
    score = 0.5  # Neutral baseline
    bonuses = 0.0
    total_checks = 0
    reasons = []

    # 1. Budget Compatibility Check
    price = float(item.get("price", 0.0))
    if budget_max and budget_max > 0:
        total_checks += 1
        if price <= budget_max:
            bonuses += 0.25
            reasons.append(f"Matches your selected budget (Rs. {price:.0f} <= Rs. {budget_max:.0f}).")
        else:
            bonuses -= 0.20

    # 2. Undertone & Color Harmony
    primary_color = str(item.get("primary_color", "")).capitalize()
    if undertone and undertone in UNDERTONE_COMPATIBLE_COLORS:
        total_checks += 1
        compatible_palette = UNDERTONE_COMPATIBLE_COLORS[undertone]
        if primary_color in compatible_palette:
            bonuses += 0.25
            reasons.append(f"{primary_color} harmonizes naturally with your estimated {undertone} undertone.")
        else:
            bonuses += 0.05

    # 3. Explicit User Color Preference
    if preferred_colors and len(preferred_colors) > 0:
        total_checks += 1
        if any(c.lower() in primary_color.lower() for c in preferred_colors):
            bonuses += 0.25
            reasons.append(f"Matches your preferred color palette ({primary_color}).")

    # 4. Silhouette Proportion Guidelines
    category = str(item.get("category", ""))
    if body_shape and body_shape in BODY_SHAPE_COMPATIBLE_CATEGORIES:
        total_checks += 1
        if category in BODY_SHAPE_COMPATIBLE_CATEGORIES[body_shape]:
            bonuses += 0.20
            reasons.append(f"{category} aligns with standard styling suggestions for {body_shape} proportions.")

    # 5. Occasion Harmony
    item_occ = str(item.get("occasion", "")).lower()
    if preferred_occasion and preferred_occasion != "All":
        total_checks += 1
        if preferred_occasion.lower() in item_occ:
            bonuses += 0.20
            reasons.append(f"Specifically suited for your selected occasion ({preferred_occasion}).")

    # 6. Fit Preference
    item_fit = str(item.get("fit", "")).lower()
    if preferred_fit and preferred_fit.lower() in item_fit:
        total_checks += 1
        bonuses += 0.15
        reasons.append(f"Tailored to your preferred {preferred_fit} styling.")

    final_score = max(0.0, min(1.0, score + bonuses))
    if not reasons:
        reasons.append("General all-season fashion alignment.")

    return round(final_score, 3), reasons
