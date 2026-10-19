# Dataset and Model Details

## 1. Student Assessment Dataset

The dataset (`source_code/career_pred.csv`) contains 20,000 multi-dimensional student records with 38 predictor features and 1 target classification label.

### Feature Space Summary

| Category | Count | Key Features |
|---|:---:|---|
| **Academic Subjects** | 9 | Operating Systems, Algorithms, Programming Concepts, Software Engineering, Networks, Electronics, Computer Architecture, Math, Communication |
| **Cognitive & Practical** | 5 | Hours working per day, Logical quotient rating, Coding skills rating, Hackathons, Public speaking points |
| **Extracurricular Learning** | 6 | Self-learning capability, Extra-courses, Certifications, Workshops, Talent tests, Olympiads |
| **Behavioral & Career Traits** | 18 | Reading/writing skills, Memory score, Career interests, Company tier, Team collaboration, Personality traits |
| **Target Role** | 1 | Suggested Job Role (34 discrete IT specializations) |

---

## 2. Multi-Class Model Benchmark Evaluation

| Model Architecture | Hyperparameters | Top-1 Test Accuracy | Top-3 Accuracy | Top-5 Accuracy | Average CPU Latency |
|---|---|:---:|:---:|:---:|:---:|
| **XGBoost Classifier** | 30 estimators, max depth 5, lr 0.1 | **4.73%** | **11.2%** | **18.4%** | **6.4 ms** |
| **Random Forest** | 50 estimators, max depth 12 | **4.00%** | **9.8%** | **16.3%** | **7.2 ms** |
| **Decision Tree** | CART, max depth 12, Gini | **3.07%** | **7.4%** | **12.9%** | **1.8 ms** |
| *Random Guessing Baseline* | 1 / 34 Classes | *2.94%* | *8.82%* | *14.71%* | — |

---

## 3. Top-K Alternative Pathway Strategy

Because modern technical careers share extensive overlapping competencies (e.g., Python, SQL, REST APIs), the model provides a primary recommended role plus the top 3 alternative fallback careers based on posterior probability ranking.
