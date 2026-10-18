"""Dataset Loader and Catalogue Manager."""

import os
import pandas as pd
from PIL import Image, ImageDraw
import config

CATALOGUE_DATA = [
    # Shirts
    {
        "outfit_id": "OUTFIT_001",
        "outfit_name": "Classic Crisp White Oxford Shirt",
        "category": "Shirts",
        "garment_type": "Button-Down Shirt",
        "description": "Premium 100% breathable cotton slim-fit button-down white shirt suitable for business meetings and semi-formal evening dinners.",
        "dominant_colour": "White",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle, Triangle (Pear)",
        "occasion": "Formal",
        "style": "Classic",
        "season": "All-Season",
        "price": 1899.0,
        "image_path": "outfits/shirts_white_oxford.jpg"
    },
    {
        "outfit_id": "OUTFIT_002",
        "outfit_name": "Sky Blue Linen Casual Shirt",
        "category": "Shirts",
        "garment_type": "Casual Shirt",
        "description": "Lightweight pastel sky blue linen shirt featuring mandarin collar and roll-up sleeves for relaxed weekend brunch.",
        "dominant_colour": "Blue",
        "suitable_skin_tones": "Fair, Medium/Wheatish",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Casual",
        "style": "Minimalist",
        "season": "Summer",
        "price": 1499.0,
        "image_path": "outfits/shirts_sky_blue_linen.jpg"
    },
    # T-shirts
    {
        "outfit_id": "OUTFIT_003",
        "outfit_name": "Charcoal Minimalist Crewneck T-Shirt",
        "category": "T-shirts",
        "garment_type": "Crewneck Tee",
        "description": "Ultra-soft combed organic cotton crewneck tee in charcoal heather grey. Great base layer or standalone casual wear.",
        "dominant_colour": "Grey",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Casual",
        "style": "Minimalist",
        "season": "All-Season",
        "price": 799.0,
        "image_path": "outfits/tshirts_charcoal_crew.jpg"
    },
    {
        "outfit_id": "OUTFIT_004",
        "outfit_name": "Graphic Urban Oversized Streetwear T-Shirt",
        "category": "T-shirts",
        "garment_type": "Oversized Tee",
        "description": "Heavyweight cotton drop-shoulder streetwear graphic t-shirt in washed black with subtle typography on chest.",
        "dominant_colour": "Black",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Cool, Neutral",
        "compatible_body_shapes": "Inverted Triangle, Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Casual",
        "style": "Streetwear",
        "season": "All-Season",
        "price": 1199.0,
        "image_path": "outfits/tshirts_oversized_black.jpg"
    },
    # Trousers
    {
        "outfit_id": "OUTFIT_005",
        "outfit_name": "Tailored Charcoal Pleated Trousers",
        "category": "Trousers",
        "garment_type": "Formal Trousers",
        "description": "Sharp tapered pleated dress trousers crafted from wrinkle-resistant poly-wool blend with concealed waistband adjusters.",
        "dominant_colour": "Grey",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Formal",
        "style": "Classic",
        "season": "All-Season",
        "price": 2299.0,
        "image_path": "outfits/trousers_charcoal_pleated.jpg"
    },
    # Jeans
    {
        "outfit_id": "OUTFIT_006",
        "outfit_name": "Indigo Blue Straight Fit Raw Denim Jeans",
        "category": "Jeans",
        "garment_type": "Denim Jeans",
        "description": "Authentic 13oz selvedge raw indigo denim jeans with classic 5-pocket styling and straight leg cut.",
        "dominant_colour": "Blue",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear), Inverted Triangle",
        "occasion": "Casual",
        "style": "Casual",
        "season": "All-Season",
        "price": 2499.0,
        "image_path": "outfits/jeans_indigo_straight.jpg"
    },
    # Dresses
    {
        "outfit_id": "OUTFIT_007",
        "outfit_name": "Emerald Green Satin Wrap Midi Dress",
        "category": "Dresses",
        "garment_type": "Wrap Dress",
        "description": "Elegant jewel-toned emerald green satin wrap midi dress with V-neckline and tie waist that beautifully defines silhouette.",
        "dominant_colour": "Emerald",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Party",
        "style": "Modern",
        "season": "Autumn",
        "price": 3499.0,
        "image_path": "outfits/dresses_emerald_wrap.jpg"
    },
    {
        "outfit_id": "OUTFIT_008",
        "outfit_name": "Floral Pastel Chiffon Summer Sundress",
        "category": "Dresses",
        "garment_type": "A-Line Sundress",
        "description": "Breezy blush pink and lavender floral chiffon sundress with ruffled hem and adjustable spaghetti straps.",
        "dominant_colour": "Pastel",
        "suitable_skin_tones": "Fair, Medium/Wheatish",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Inverted Triangle, Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Casual",
        "style": "Bohemian",
        "season": "Summer",
        "price": 2199.0,
        "image_path": "outfits/dresses_pastel_chiffon.jpg"
    },
    # Kurtis
    {
        "outfit_id": "OUTFIT_009",
        "outfit_name": "Maroon Hand-Block Printed Cotton Kurti",
        "category": "Kurtis",
        "garment_type": "A-line Kurti",
        "description": "Artisanal pure cotton A-line kurti in deep maroon featuring traditional Ajrakh geometric hand-block prints and wooden buttons.",
        "dominant_colour": "Red",
        "suitable_skin_tones": "Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Triangle (Pear), Rectangle / Hourglass",
        "occasion": "Casual",
        "style": "Traditional",
        "season": "All-Season",
        "price": 1299.0,
        "image_path": "outfits/kurtis_maroon_ajrakh.jpg"
    },
    # Chudidhars
    {
        "outfit_id": "OUTFIT_010",
        "outfit_name": "Teal Chanderi Embroidered Chudidhar Set",
        "category": "Chudidhars",
        "garment_type": "Chudidhar Suit Set",
        "description": "Regal teal green Chanderi silk straight kurta paired with matching fitted chudidhar and organza zari dupatta.",
        "dominant_colour": "Emerald",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Festival",
        "style": "Traditional",
        "season": "All-Season",
        "price": 3899.0,
        "image_path": "outfits/chudidhars_teal_chanderi.jpg"
    },
    # Sarees
    {
        "outfit_id": "OUTFIT_011",
        "outfit_name": "Crimson Kanjeevaram Pure Silk Saree",
        "category": "Sarees",
        "garment_type": "Traditional Silk Saree",
        "description": "Exquisite crimson red authentic Kanjeevaram silk saree adorned with intricate gold zari brocade pallu and contrasting borders.",
        "dominant_colour": "Red",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear), Inverted Triangle",
        "occasion": "Wedding",
        "style": "Traditional",
        "season": "All-Season",
        "price": 7999.0,
        "image_path": "outfits/sarees_crimson_kanjeevaram.jpg"
    },
    {
        "outfit_id": "OUTFIT_012",
        "outfit_name": "Pastel Peach Organza Floral Embroidered Saree",
        "category": "Sarees",
        "garment_type": "Organza Designer Saree",
        "description": "Contemporary sheer peach organza saree with delicate cut-work scalloped borders and hand-embroidered sequin floral motifs.",
        "dominant_colour": "Pastel",
        "suitable_skin_tones": "Fair, Medium/Wheatish",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Party",
        "style": "Modern",
        "season": "Spring",
        "price": 4599.0,
        "image_path": "outfits/sarees_peach_organza.jpg"
    },
    # Formal wear
    {
        "outfit_id": "OUTFIT_013",
        "outfit_name": "Midnight Navy Italian Wool Two-Piece Suit",
        "category": "Formal wear",
        "garment_type": "Business Suit",
        "description": "Impeccably tailored midnight navy 2-piece wool suit with notch lapels, flap pockets, and flat-front matching trousers.",
        "dominant_colour": "Navy",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Formal",
        "style": "Formal",
        "season": "All-Season",
        "price": 6999.0,
        "image_path": "outfits/formal_navy_wool_suit.jpg"
    },
    {
        "outfit_id": "OUTFIT_014",
        "outfit_name": "Charcoal Double-Breasted Power Tuxedo",
        "category": "Formal wear",
        "garment_type": "Tuxedo",
        "description": "Modern charcoal double-breasted formal blazer jacket with satin peak lapels and structured shoulder construction.",
        "dominant_colour": "Grey",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Inverted Triangle, Rectangle / Hourglass",
        "occasion": "Formal",
        "style": "Classic",
        "season": "Winter",
        "price": 7499.0,
        "image_path": "outfits/formal_charcoal_tuxedo.jpg"
    },
    # Casual wear
    {
        "outfit_id": "OUTFIT_015",
        "outfit_name": "Olive Utility Overshirt and Chino Set",
        "category": "Casual wear",
        "garment_type": "Casual Layering Set",
        "description": "Rugged yet refined olive green cotton-twill shacket layered over neutral beige stretch chino pants.",
        "dominant_colour": "Emerald",
        "suitable_skin_tones": "Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Triangle (Pear), Rectangle / Hourglass",
        "occasion": "Casual",
        "style": "Casual",
        "season": "Autumn",
        "price": 2899.0,
        "image_path": "outfits/casual_olive_utility.jpg"
    },
    # Ethnic wear
    {
        "outfit_id": "OUTFIT_016",
        "outfit_name": "Royal Ivory Silk Embroidered Sherwani Set",
        "category": "Ethnic wear",
        "garment_type": "Sherwani Ensemble",
        "description": "Luxury ivory raw silk groom sherwani detailed with subtle French knot hand embroidery, accompanied by churidar and stole.",
        "dominant_colour": "White",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Wedding",
        "style": "Traditional",
        "season": "Winter",
        "price": 11999.0,
        "image_path": "outfits/ethnic_ivory_sherwani.jpg"
    },
    {
        "outfit_id": "OUTFIT_017",
        "outfit_name": "Golden Ochre Tussar Silk Kurta Pajama",
        "category": "Ethnic wear",
        "garment_type": "Kurta Pajama",
        "description": "Rich golden ochre yellow textured Tussar silk knee-length kurta paired with white tapered cotton pajama for festive celebrations.",
        "dominant_colour": "Gold",
        "suitable_skin_tones": "Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Festival",
        "style": "Traditional",
        "season": "All-Season",
        "price": 2999.0,
        "image_path": "outfits/ethnic_golden_kurta.jpg"
    },
    # Party wear
    {
        "outfit_id": "OUTFIT_018",
        "outfit_name": "Metallic Midnight Sequined Cocktail Gown",
        "category": "Party wear",
        "garment_type": "Cocktail Dress",
        "description": "Sensational floor-sweeping midnight blue gown encrusted with micro-sequins, featuring thigh-high side slit and open back.",
        "dominant_colour": "Navy",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Party",
        "style": "Modern",
        "season": "All-Season",
        "price": 5899.0,
        "image_path": "outfits/party_metallic_gown.jpg"
    },
    {
        "outfit_id": "OUTFIT_019",
        "outfit_name": "Velvet Embroidered Tuxedo Dinner Jacket",
        "category": "Party wear",
        "garment_type": "Blazer Jacket",
        "description": "Sumptuous black velvet evening dinner blazer jacket with intricate tone-on-tone paisley lapel embroidery.",
        "dominant_colour": "Black",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Cool, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Inverted Triangle",
        "occasion": "Party",
        "style": "Modern",
        "season": "Winter",
        "price": 6499.0,
        "image_path": "outfits/party_velvet_tuxedo.jpg"
    },
    {
        "outfit_id": "OUTFIT_020",
        "outfit_name": "Beige Relaxed Italian Linen Suit",
        "category": "Formal wear",
        "garment_type": "Summer Linen Suit",
        "description": "Effortless light beige linen-cotton unconstructed blazer and trousers for destination weddings and daytime garden galas.",
        "dominant_colour": "White",
        "suitable_skin_tones": "Fair, Medium/Wheatish, Dusky/Dark",
        "suitable_undertones": "Warm, Neutral",
        "compatible_body_shapes": "Rectangle / Hourglass, Triangle (Pear)",
        "occasion": "Wedding",
        "style": "Classic",
        "season": "Summer",
        "price": 5499.0,
        "image_path": "outfits/formal_beige_linen.jpg"
    }
]

PALETTE = {
    "White": (240, 240, 245),
    "Blue": (70, 130, 180),
    "Grey": (80, 85, 95),
    "Black": (30, 30, 35),
    "Emerald": (25, 110, 80),
    "Pastel": (220, 190, 205),
    "Red": (155, 30, 45),
    "Navy": (20, 40, 80),
    "Gold": (190, 150, 50),
}


def ensure_catalogue_images(catalogue_df: pd.DataFrame):
    """Ensures each item in the catalogue has an associated image file."""
    os.makedirs(config.OUTFITS_DIR, exist_ok=True)
    for _, row in catalogue_df.iterrows():
        rel_path = row["image_path"]
        abs_path = os.path.join(config.BASE_DIR, rel_path) if not os.path.isabs(rel_path) else rel_path
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        if not os.path.exists(abs_path):
            bg = PALETTE.get(row.get("dominant_colour", "Grey"), (100, 100, 100))
            img = Image.new("RGB", (450, 600), color=bg)
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 430, 580], outline=(255, 255, 255), width=3)
            draw.rectangle([30, 420, 420, 560], fill=(15, 15, 20))
            draw.text((45, 435), str(row["category"]).upper(), fill=(220, 180, 100))
            draw.text((45, 460), str(row["outfit_name"])[:32], fill=(255, 255, 255))
            draw.text((45, 490), f"Rs. {float(row['price']):.0f} | {row['occasion']}", fill=(200, 200, 200))
            draw.text((45, 515), f"Style: {row['style']} | Colour: {row['dominant_colour']}", fill=(180, 180, 180))
            img.save(abs_path, quality=92)


def load_catalogue(csv_path: str = config.CATALOGUE_PATH) -> pd.DataFrame:
    """Loads the clothing catalogue, creating starter catalogue if absent."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    if not os.path.exists(csv_path):
        df = pd.DataFrame(CATALOGUE_DATA)
        df.to_csv(csv_path, index=False)
    else:
        df = pd.read_csv(csv_path)

    # Ensure required columns
    required_cols = [
        "outfit_id", "outfit_name", "category", "garment_type", "description",
        "dominant_colour", "suitable_skin_tones", "suitable_undertones",
        "compatible_body_shapes", "occasion", "style", "season", "price", "image_path"
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Catalogue missing required column: {col}")

    ensure_catalogue_images(df)
    return df
