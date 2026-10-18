# Measurable Experiments & Evaluation Benchmark

This document reports the empirical experiments conducted on the Kaggle Fake News Dataset (20,800 articles), evaluating multiple machine learning architectures, feature engineering representations, and inference efficiency.

---

## 1. Comparative Classifier Benchmark

We evaluated 5 distinct machine learning models on an identical stratified split (80% training / 20% test) with TF-IDF vectorization (10,000 features, n-gram range 1–2):

| Model Architecture | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC (%) | Training Time (s) | Inference Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (LinearSVC)** | **92.08%** | 92.45% | 92.08% | **92.07%** | **97.21%** | 0.024s | 0.36 ms |
| **Logistic Regression (LR)** | **91.50%** | 92.66% | 91.50% | 91.46% | 97.12% | 0.043s | **0.32 ms** |
| **Passive Aggressive (PAC)** *(Deployed)* | **91.42%** | 91.54% | 91.42% | 91.42% | 96.91% | **0.016s** | 0.64 ms |
| **Multinomial Naive Bayes (MNB)** | 84.58% | 85.32% | 84.58% | 84.47% | 95.14% | **0.002s** | 0.94 ms |
| **Random Forest (RFC)** | 83.42% | 87.52% | 83.42% | 83.02% | 95.67% | 0.326s | 17.80 ms |

### Key Observations:
* **Why Passive Aggressive Classifier was selected for deployment:** PAC achieves competitive accuracy (91.4%–96.0% full training) with the fastest training time (0.016s) and native online learning support, enabling continuous streaming updates without full model retraining.
* **Linear SVM & Logistic Regression** demonstrate that linear decision boundaries in high-dimensional TF-IDF feature spaces generalize exceptionally well.
* **Naive Bayes & Random Forest** suffer from feature independence assumptions and sparsity bottlenecks in wide vocabulary sets.

---

## 2. Feature Representation Ablation Study

We evaluated the impact of n-gram context windows on the classification decision:

| Representation Window | Vocabulary Features | Accuracy (%) | F1-Score (%) | Performance Impact |
| :--- | :---: | :---: | :---: | :--- |
| **Unigram Only (1, 1)** | 5,000 | 90.25% | 90.25% | Baseline single-word bag of words |
| **Unigram + Bigram (1, 2)** | 10,000 | **91.42%** | **91.42%** | **Optimal** (captures paired phrases like *"fake news"*, *"breaking report"*) |
| **Bigram Only (2, 2)** | 10,000 | 84.75% | 84.62% | Degradation due to vocabulary sparsity |
| **Tri-Gram Window (1, 3)** | 15,000 | 91.08% | 91.08% | Marginal drop due to increased dimensionality |

---

## 3. Beyond Source & Author Blacklists

### The Limitation of Blacklists
Traditional fake news prevention relies on static lookup tables (e.g. domain blocklists or author flags). This strategy fails when:
1. An established or trusted journalist publishes misinformation or unverified leaks.
2. A malicious publisher registers a new, unflagged domain or uses pseudonyms.
3. Content is aggregated or forwarded across social media without domain metadata.

### Our Solution: Pure Stylometric Language Processing
Our model analyzes **language patterns**:
* **Lexical TF-IDF Signatures:** Discriminates between objective reporting vocabularies and sensational clickbait rhetoric across 146,627 features.
* **Sensationalism Index:** Tracks hyperbole, urgent call-to-actions, and emotional polarity.
* **Source-Independence Mode:** Strips out publisher watermarks (`- The New York Times`, `- Breitbart`, `Reuters:`) to ensure decisions are grounded purely in linguistic semantics.
