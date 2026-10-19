# Model Card: Gradient Boosting Multi-Modal Recommender

## Model Overview
- **Primary Estimator**: `GradientBoostingClassifier` (Scikit-Learn).
- **Target Variable**: Preferred Garment Category (11 classes: Chudidhar, Dresses, Ethnic wear, Formal wear, Jeans, Kurtis, Party wear, Sarees, Shirts, T-shirts, Trousers).
- **Training Corpus**: 1,000 multi-attribute consumer purchase cycles (800 train, 200 test).
- **Input Features**: Body silhouette, melanin depth, vascular undertone, style preference, occasion, preferred accent color, max budget.
- **NLP Textual Model**: TF-IDF Vectorizer with unigram/bigram tokenization and sublinear TF scaling.
- **Heuristic Modules**: Optical melanin absorption matrix and anatomical silhouette proportion rules.
