"""Data preparation and synthetic dataset generator for Stage 3."""

import os
import random
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import config

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

CATEGORIES_SPECS = {
    "Shirts": {
        "subcategories": ["Button-Down", "Oxford", "Linen Shirt", "Mandarin Collar"],
        "fabrics": ["Cotton", "Linen", "Poplin", "Flannel"],
        "price_range": (899, 2999),
        "styles": ["Classic", "Minimalist", "Modern"],
        "fits": ["Slim Fit", "Regular Fit", "Relaxed Fit"],
        "occasions": ["Office", "College", "Casual", "Party"],
        "shapes": ["Rectangle / Hourglass", "Inverted Triangle", "Triangle (Pear)"],
    },
    "T-shirts": {
        "subcategories": ["Crewneck Tee", "Polo Shirt", "Oversized Streetwear", "Henley"],
        "fabrics": ["Combed Cotton", "Organic Jersey", "Modal Blend", "Cotton Pique"],
        "price_range": (499, 1599),
        "styles": ["Casual", "Streetwear", "Minimalist"],
        "fits": ["Regular Fit", "Oversized", "Slim Fit"],
        "occasions": ["Casual", "College"],
        "shapes": ["Rectangle / Hourglass", "Inverted Triangle", "Triangle (Pear)"],
    },
    "Trousers": {
        "subcategories": ["Pleated Chinos", "Formal Slacks", "Cropped Trousers", "Linen Pants"],
        "fabrics": ["Wool Blend", "Cotton Twill", "Linen", "Polyester Viscose"],
        "price_range": (1199, 3999),
        "styles": ["Classic", "Modern", "Office"],
        "fits": ["Tailored", "Slim Fit", "Relaxed Fit"],
        "occasions": ["Office", "Formal", "Party"],
        "shapes": ["Rectangle / Hourglass", "Triangle (Pear)"],
    },
    "Jeans": {
        "subcategories": ["Straight Fit Raw", "Tapered Denim", "Relaxed Wide Leg", "Slim Stretch"],
        "fabrics": ["Rigid Denim", "Stretch Cotton Denim", "Selvedge Denim"],
        "price_range": (999, 3499),
        "styles": ["Casual", "Streetwear", "Classic"],
        "fits": ["Regular Fit", "Slim Fit", "Relaxed Fit"],
        "occasions": ["Casual", "College"],
        "shapes": ["Rectangle / Hourglass", "Triangle (Pear)", "Inverted Triangle"],
    },
    "Dresses": {
        "subcategories": ["Satin Wrap Dress", "Chiffon Sundress", "A-Line Midi", "Shift Dress"],
        "fabrics": ["Silk Satin", "Chiffon", "Georgette", "Cotton Poplin"],
        "price_range": (1499, 5999),
        "styles": ["Chic", "Modern", "Bohemian", "Classic"],
        "fits": ["Regular Fit", "Tailored", "Relaxed Fit"],
        "occasions": ["Party", "Casual", "Wedding"],
        "shapes": ["Hourglass", "Rectangle / Hourglass", "Triangle (Pear)"],
    },
    "Kurtis": {
        "subcategories": ["Anarkali Kurti", "Straight Ajrakh Kurti", "A-Line Embroidered", "Short Kurti"],
        "fabrics": ["Chanderi Silk", "Cotton Khadi", "Modal Silk", "Rayon"],
        "price_range": (799, 2999),
        "styles": ["Ethnic", "Traditional", "Modern"],
        "fits": ["Regular Fit", "Relaxed Fit", "Tailored"],
        "occasions": ["College", "Traditional", "Office", "Festival"],
        "shapes": ["Hourglass", "Rectangle", "Triangle (Pear)"],
    },
    "Chudidhar": {
        "subcategories": ["Zari Silk Suit", "Embroidered Chanderi Set", "Pastel Georgette Set"],
        "fabrics": ["Raw Silk", "Chanderi", "Georgette", "Cotton"],
        "price_range": (1999, 7999),
        "styles": ["Traditional", "Ethnic"],
        "fits": ["Tailored", "Regular Fit"],
        "occasions": ["Wedding", "Traditional", "Festival"],
        "shapes": ["Hourglass", "Triangle (Pear)", "Rectangle / Hourglass"],
    },
    "Sarees": {
        "subcategories": ["Kanjeevaram Silk", "Organza Floral", "Banarasi Brocade", "Linen Handloom"],
        "fabrics": ["Pure Silk", "Organza", "Tussar Silk", "Linen"],
        "price_range": (2499, 14999),
        "styles": ["Traditional", "Ethnic", "Classic"],
        "fits": ["Regular Fit"],
        "occasions": ["Wedding", "Traditional", "Festival"],
        "shapes": ["Hourglass", "Rectangle / Hourglass", "Triangle (Pear)", "Inverted Triangle"],
    },
    "Formal wear": {
        "subcategories": ["Wool Tuxedo", "Tailored Pantsuit", "Linen Blazer Suit", "Double-Breasted Suit"],
        "fabrics": ["Italian Wool", "Poly-Viscose", "Linen-Cotton Blend"],
        "price_range": (3999, 12999),
        "styles": ["Classic", "Modern"],
        "fits": ["Tailored", "Slim Fit"],
        "occasions": ["Office", "Party", "Formal"],
        "shapes": ["Rectangle / Hourglass", "Inverted Triangle"],
    },
    "Ethnic wear": {
        "subcategories": ["Royal Sherwani", "Kurta Pajama Set", "Bandhgala Suit", "Zari Lehenga"],
        "fabrics": ["Jacquard Silk", "Brocade", "Tussar Silk", "Velvet"],
        "price_range": (2999, 16999),
        "styles": ["Ethnic", "Traditional"],
        "fits": ["Tailored", "Regular Fit"],
        "occasions": ["Wedding", "Traditional", "Festival"],
        "shapes": ["Hourglass", "Rectangle / Hourglass", "Inverted Triangle"],
    },
    "Party wear": {
        "subcategories": ["Sequined Cocktail Gown", "Velvet Dinner Jacket", "Metallic Slip Dress"],
        "fabrics": ["Velvet", "Metallic Mesh", "Silk Georgette", "Satin"],
        "price_range": (3499, 11999),
        "styles": ["Modern", "Chic"],
        "fits": ["Slim Fit", "Tailored"],
        "occasions": ["Party"],
        "shapes": ["Hourglass", "Rectangle / Hourglass", "Inverted Triangle"],
    },
}

COLOR_UNDERTONE_MAP = {
    "White": ["Warm", "Cool", "Neutral"],
    "Blue": ["Cool", "Neutral"],
    "Black": ["Warm", "Cool", "Neutral"],
    "Grey": ["Cool", "Neutral"],
    "Beige": ["Warm", "Neutral"],
    "Navy": ["Cool", "Neutral"],
    "Red": ["Warm", "Neutral"],
    "Emerald": ["Cool", "Neutral"],
    "Maroon": ["Warm", "Neutral"],
    "Teal": ["Cool", "Neutral"],
    "Peach": ["Warm", "Neutral"],
    "Pastel": ["Cool", "Neutral"],
    "Yellow": ["Warm"],
    "Olive": ["Warm", "Neutral"],
    "Pink": ["Cool", "Warm", "Neutral"],
}


def generate_synthetic_catalog(num_records: int = 1000) -> pd.DataFrame:
    """Generates clearly labelled synthetic starter dataset with at least 1,000 clothing records."""
    records = []
    cat_keys = list(CATEGORIES_SPECS.keys())
    existing_photos = [f for f in os.listdir(config.OUTFITS_DIR) if f.endswith(".jpg")] if os.path.exists(config.OUTFITS_DIR) else []

    for i in range(1, num_records + 1):
        item_id = f"SYNTH_{i:04d}"
        category = random.choice(cat_keys)
        spec = CATEGORIES_SPECS[category]

        subcategory = random.choice(spec["subcategories"])
        fabric = random.choice(spec["fabrics"])
        style = random.choice(spec["styles"])
        fit = random.choice(spec["fits"])
        occasion = random.choice(spec["occasions"])
        primary_color = random.choice(config.SUPPORTED_COLORS)
        secondary_color = random.choice([c for c in config.SUPPORTED_COLORS if c != primary_color] + ["None"])
        season = random.choice(config.SUPPORTED_SEASONS)
        price = float(random.randint(spec["price_range"][0], spec["price_range"][1]))

        # Undertone harmony tags
        undertones = COLOR_UNDERTONE_MAP.get(primary_color, ["Neutral"])
        undertone_tags = ", ".join(undertones)
        body_shapes = ", ".join(spec["shapes"])

        item_name = f"{primary_color} {fabric} {subcategory}"
        description = (
            f"Elegantly designed {fit.lower()} {subcategory.lower()} made from premium {fabric.lower()} "
            f"in vibrant {primary_color.lower()}. Ideal for {occasion.lower()} settings and {season.lower()} styling."
        )

        # Image path: map to existing realistic outfit images if available, else standard outfit path
        if existing_photos:
            img_file = existing_photos[(i - 1) % len(existing_photos)]
            image_path = f"outfits/{img_file}"
        else:
            image_path = f"outfits/{category.lower().replace(' ', '_')}_{i}.jpg"

        gender = "Women" if category in ["Dresses", "Kurtis", "Chudidhar", "Sarees", "Skirts"] else (
            "Men" if category in ["Shirts", "Formal wear"] and random.random() > 0.4 else "Unisex"
        )

        records.append({
            "item_id": item_id,
            "item_name": item_name,
            "category": category,
            "subcategory": subcategory,
            "description": description,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "style_tags": f"{style}, {fit}, {fabric}",
            "occasion": occasion,
            "fabric": fabric,
            "pattern": random.choice(["Solid", "Striped", "Floral", "Embroidered", "Checks", "Printed"]),
            "fit": fit,
            "season": season,
            "gender_or_style_category": gender,
            "price": price,
            "image_path": image_path,
            "body_shape_tags": body_shapes,
            "undertone_color_tags": undertone_tags,
            "user_preference_label": "synthetic_demonstration_record",
        })

    df = pd.DataFrame(records)
    return df


def generate_synthetic_interaction_training_data(num_samples: int = 1000) -> pd.DataFrame:
    """Generates synthetic preference training samples for GBM demonstration."""
    samples = []
    categories = list(CATEGORIES_SPECS.keys())

    for i in range(num_samples):
        b_shape = random.choice(config.SUPPORTED_BODY_SHAPES)
        s_tone = random.choice(config.SUPPORTED_SKIN_TONES)
        u_tone = random.choice(config.SUPPORTED_UNDERTONES)
        p_style = random.choice(config.SUPPORTED_STYLES)
        p_occ = random.choice(config.SUPPORTED_OCCASIONS)
        p_color = random.choice(config.SUPPORTED_COLORS)
        b_max = float(random.choice([1500, 2500, 4000, 6000, 10000, 15000]))

        # Semi-structured correlation for demonstration
        if p_occ in ["Wedding", "Traditional"]:
            pref_cat = random.choice(["Ethnic wear", "Sarees", "Chudidhar", "Kurtis"])
        elif p_occ in ["Office", "Formal"]:
            pref_cat = random.choice(["Formal wear", "Shirts", "Trousers"])
        elif p_occ in ["Party"]:
            pref_cat = random.choice(["Party wear", "Dresses", "Shirts"])
        else:
            pref_cat = random.choice(["T-shirts", "Jeans", "Shirts", "Kurtis"])

        samples.append({
            "sample_id": f"SMPL_{i:05d}",
            "body_shape": b_shape,
            "skin_tone": s_tone,
            "undertone": u_tone,
            "preferred_style": p_style,
            "preferred_occasion": p_occ,
            "preferred_colour": p_color,
            "budget_max": b_max,
            "preferred_clothing_category": pref_cat,
            "data_provenance": "synthetic_academic_demonstration",
        })

    return pd.DataFrame(samples)
