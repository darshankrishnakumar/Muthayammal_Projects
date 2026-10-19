# Demonstration & Walkthrough Script: Skin Tone & Body Measurement Dress Recommendation System (PROJECT-018)

## Overview
- **Project Identifier**: PROJECT-018
- **Module**: `project_18_dress_recommendation_skin_tone`
- **Application Port**: Port 5018 (`http://127.0.0.1:5018`)
- **Video Target Duration**: Exactly 180.0 seconds (03:00.00), 1280x800, 30 fps H.264 MP4.

---

## Detailed Demonstration Sequence (Exact 180 Seconds)

### Phase 1: System Overview & Problem Formulation (00:00 - 00:30 | 30s)
- **Visual**: Landing view on Port 5018 (`tab-studio`), showcasing the dark-mode glassmorphic styling studio, input controls for skin tone, undertone, body silhouette, and the 4 preset personas.
- **Narration**: Introduction to PROJECT-018: An AI-powered fashion recommendation system tackling the 35% e-commerce return rate crisis. Explains the multi-modal hybrid score formulation fusing Gradient Boosting category prediction, TF-IDF NLP description matching, optical melanin chromatic absorption theory, and anatomical silhouette geometry.

### Phase 2: Persona 1 Curation: Fair-Cool Evening Gala (00:30 - 01:05 | 35s)
- **Visual**: Click preset `Fair Cool Gala` (`button[data-preset="p1"]`), displaying automatic attribute mapping (Fair tone, Cool undertone, Hourglass silhouette, Party occasion, Emerald color).
- **Narration**: Live execution of the hybrid recommender. The system identifies the **Emerald Green Wrap Maxi Dress** as the #1 match (96% Match, ₹3,499), highlighting how jewel emerald dyes illuminate fair cool complexions while the wrap silhouette flatters the natural Hourglass waist taper.

### Phase 3: Persona 2 Curation: Medium-Warm Business Formal (01:05 - 01:40 | 35s)
- **Visual**: Click preset `Medium Warm Formal` (`button[data-preset="p2"]`), auto-populating Medium tone, Warm undertone, Pear silhouette, Formal occasion, Navy/White palette.
- **Narration**: Demonstrating adaptation to different body morphology. The engine ranks the **Classic Crisp White Oxford Shirt** (94% Match) and **Charcoal Tuxedo Suit** (91% Match), showing how structured collars balance Pear proportions and elevate warm golden undertones.

### Phase 4: Persona 3 Curation: Olive-Warm Traditional Ethnic (01:40 - 02:10 | 30s)
- **Visual**: Click preset `Olive Warm Ethnic` (`button[data-preset="p3"]`), showing Olive tone, Warm undertone, Rectangle silhouette, Ethnic occasion, Crimson palette.
- **Narration**: The system curates the **Crimson Kanjeevaram Silk Saree** (96% Match, ₹8,999) and **Golden Silk Kurta** (93% Match), demonstrating chromatic warmth without clashing on olive skin tones. Highlights forensic style rationale bullets.

### Phase 5: Multi-Modal Model Evaluation & Catalogue Explorer (02:10 - 02:35 | 25s)
- **Visual**: Switch to `.nav-tab[data-tab="catalogue"]` showcasing the 20+ item inventory with photographs and metadata, then switch to `.nav-tab[data-tab="models"]` reviewing the GBM 11-class metrics and ensemble weight allocation bars.
- **Narration**: Quantitative evaluation of the Gradient Boosting Machine across 1,000 consumer purchase cycles, explaining the 35% TF-IDF, 30% GBM, 20% Color Harmony, and 15% Silhouette weight distribution.

### Phase 6: SQLite Audit Trail, Architecture & Submission Summary (02:35 - 03:00 | 25s)
- **Visual**: Switch to `.nav-tab[data-tab="history"]` showcasing the SQLite `RECOMMENDATION_HISTORY` log from `user_data.db`, then briefly preview `.nav-tab[data-tab="architecture"]`.
- **Narration**: ACID transactional audit logging in SQLite, verifying 33/33 automated tests passing, 9 high-res UI screenshots, 15 widescreen presentation slides, 50+ paragraph formal academic documentation, and complete capstone compliance.
