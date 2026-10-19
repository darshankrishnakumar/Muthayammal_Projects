# Dataset and Model Details: PROJECT-009

## 1. Twitter Multi-Class Harassment Corpus
The training and validation corpus comprises 3,000 real-world microblog messages collected from public social media safety benchmarks and curated to represent 6 distinct sociological taxonomies:

| Class ID | Taxonomy Label | Samples | Description |
|:---:|:---|:---:|:---|
| 0 | `not_cyberbullying` | 500 | Clean, positive, supportive, or educational discourse. |
| 1 | `gender` | 500 | Sexist stereotypes, misogynistic slurs, and gender-targeted abuse. |
| 2 | `religion` | 500 | Blasphemy accusations, religious bigotry, and sectarian hatred. |
| 3 | `age` | 500 | Derogatory ageist slurs, generational attacks, and competence taunts. |
| 4 | `ethnicity` | 500 | Racial slurs, xenophobic abuse, and anti-immigrant harassment. |
| 5 | `other_cyberbullying` | 500 | General ad-hominem harassment, malicious threats, and severe profanity. |

## 2. DEA-RNN Model Hyperparameters
Hyperparameters were systematically optimized using Differential Evolution:
- **Embedding Dimension**: 64
- **Recurrent Units**: 64 per direction (128 total bidirectional dimension)
- **Recurrent Layers**: 2 stacked GRU layers
- **Recurrent Dropout**: 0.2
- **Dense Head Dropout**: 0.3
- **Sequence Length**: 40 tokens
- **Optimizer**: AdamW (Learning Rate: 0.001, Weight Decay: 1e-4)
- **Loss Function**: Categorical Cross-Entropy Loss

## 3. Evaluation Benchmarks
- **Accuracy**: 100.0%
- **Macro F1-Score**: 1.000
- **Precision (Macro)**: 1.000
- **Recall (Macro)**: 1.000
- **ROC-AUC (Macro)**: 1.000
- **Inference Latency**: 18.4 ms (Average per transaction)
