# Explainable AI (XAI) & Style Rationale

## Multi-Component Score Decomposition
For every recommendation card rendered in the studio, the system decomposes the final match score into three visual progress bars:
1. **TF-IDF Text Relevance**: Degree of semantic similarity between user search query and garment description.
2. **GBM Category Affinity**: Machine learning prediction alignment for target garment category.
3. **Skin Tone & Silhouette Harmony**: Rule-based score evaluating chromatic undertone synergy and anatomical drape.

## Human-Readable Rationale
Every recommended item generates transparent rationale bullets explaining *why* it was curated (e.g., 'Matches ML predicted category (Shirts) • Tailored for Medium skin tone & Hourglass • Ideal for Formal setting').
