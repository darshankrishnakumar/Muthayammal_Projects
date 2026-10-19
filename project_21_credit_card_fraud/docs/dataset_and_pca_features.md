# Dataset Engineering & Principal Component Analysis (PCA)

## 1. Dataset Characteristics
The dataset is modeled on the gold-standard Kaggle European Cardholder benchmark:
- **Total Records**: 10,000 synthesized transactions.
- **Normal Transactions**: 9,750 ($97.5\%$).
- **Fraudulent Transactions**: 250 ($2.5\%$).
- **Dimensionality**: 30 input numerical features + 1 target class (`Class` $\in \{0, 1\}$).

## 2. Feature Dictionary & PCA Manifest
- **`Time`**: Number of elapsed seconds between the transaction and the initial dataset observation. Fraud clusters during off-peak night hours (01:00 - 05:00 UTC).
- **`Amount`**: Transaction transaction value in USD. Displays bimodal skew: micro-carding bot tests ($\\$0.85 - \\$4.50$) and high-value jewelry/crypto drains ($\\$1,200 - \\$6,000$).
- **`V1` through `V28`**: Principal Component Analysis (PCA) projection vectors concealing confidential cardholder PII.

### Critical PCA Threat Signatures
- **`V14` (Weight: 1.8)**: Primary fraud indicator. Severe negative deviation ($-6.5$ to $-4.0$) signifies unauthorized terminal cloning.
- **`V4` (Weight: 1.6)**: Elevated positive values ($+3.5$ to $+5.5$) reflect high geographic hop velocity.
- **`V12` (Weight: 1.5)**: Negative shift corresponds to abnormal transaction frequency.
- **`V10` & `V17` (Weight: 1.4 & 1.3)**: Corroborating markers of account takeover.
