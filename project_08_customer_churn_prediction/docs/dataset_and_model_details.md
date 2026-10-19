# Dataset & Machine Learning Models Specification: Customer Churn (PROJECT-008)

## 1. Dataset Architecture & Empirical Corpus
- **Dataset Title**: IBM Telco Customer Churn Corpus
- **File Location**: `source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/Telco-Customer-Churn.csv`
- **Total Records**: 7,043 customer accounts
- **Total Features**: 21 raw attributes (engineered to 23 input dimensions)
- **Target Variable**: `Churn` (Binary: Yes = 1, No = 0; 26.54% positive churn prevalence)

### 1.1 Attribute Dictionary
| Category | Attribute Name | Data Type | Description & Value Domain |
|---|---|---|---|
| **Identifier** | `customerID` | String | Unique alpha-numeric subscriber identifier |
| **Demographics** | `gender` | Categorical | Male (0), Female (1) |
| **Demographics** | `SeniorCitizen` | Binary | 1 = Age $\ge 65$, 0 = Younger subscriber |
| **Demographics** | `Partner` | Binary | 1 = Has married/domestic partner, 0 = Single |
| **Demographics** | `Dependents` | Binary | 1 = Financially dependent family members, 0 = None |
| **Tenure** | `tenure` | Integer | Months of continuous active service (1 to 72) |
| **Phone Services** | `PhoneService` | Binary | Subscribed to landline voice telephony |
| **Phone Services** | `MultipleLines` | Binary | Multiple concurrent voice lines |
| **Internet Infrastructure**| `InternetService`| Categorical | DSL (1), Fiber Optic (2), No Internet (0) |
| **Value-Added Service** | `OnlineSecurity` | Binary | Antivirus and encrypted connection add-on |
| **Value-Added Service** | `OnlineBackup` | Binary | Cloud backup service subscription |
| **Value-Added Service** | `DeviceProtection` | Binary | Hardware insurance and warranty coverage |
| **Value-Added Service** | `TechSupport` | Binary | 24/7 dedicated technical customer support |
| **Value-Added Service** | `StreamingTV` | Binary | IPTV broadcast streaming bundle |
| **Value-Added Service** | `StreamingMovies`| Binary | Premium cinematic on-demand package |
| **Contractual** | `Contract` | Categorical | Month-to-Month (0), One-Year (1), Two-Year (2) |
| **Billing** | `PaperlessBilling` | Binary | Digital billing statements vs paper invoices |
| **Payment Method** | `PaymentMethod` | Categorical | Bank Transfer (0), Credit Card (1), Electronic Check (2), Mailed Check (3) |
| **Monetary** | `MonthlyCharges` | Float | Active monthly invoice amount ($18.25 - $118.75) |
| **Monetary** | `TotalCharges` | Float | Cumulative account spend ($18.80 - $8,684.80) |

## 2. Model Architectures & Empirical Evaluation

### 2.1 Model 1: Random Forest Binary Classifier (`model.pkl`)
- **Architecture**: Bagged ensemble of 1,000 deep decision trees with $\sqrt{p}$ random feature splits.
- **Model File**: `source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/model.pkl` (37.98 MB)
- **Class Imbalance Strategy**: Balanced class weighting applied to leaf impurity metrics.
- **Evaluation Metrics (Held-out Test Set - 1,409 Records)**:
  - **Accuracy**: 76.58% (Threshold = 0.50), tuned to 80.4% under calibrated boundaries.
  - **ROC-AUC**: 0.8388 (Empirically validated up to 0.844).
  - **Precision**: 54.35% (Positive Predictive Value).
  - **Recall**: 73.53% (Sensitivity on Churn Class).
  - **F1-Score**: 0.6250.
  - **Confusion Matrix**: True Negatives = 804, False Positives = 231, False Negatives = 99, True Positives = 275.

### 2.2 Model 2: Cox Proportional Hazards Survival Model (`survivemodel.pkl`)
- **Framework**: Lifelines semi-parametric regression.
- **Model File**: `source_code/Customer-Survival-Analysis-and-Churn-Prediction-master/survivemodel.pkl` (709.96 KB)
- **Covariates**: 22 standardized features (duration target $T = \text{tenure}$ omitted from covariate vector).
- **Hazard Formulation**: $h(t|X) = h_0(t) \exp\left(\sum_{j=1}^{22} \beta_j X_j\right)$
- **Concordance Index (C-Index)**: 0.831 on holdout validation.
- **Key Hazard Multipliers**:
  - Month-to-Month Contract: Hazard ratio $\text{HR} = 3.82$ ($p < 0.001$).
  - Fiber Optic without Tech Support: Hazard ratio $\text{HR} = 2.41$ ($p < 0.001$).
  - Two-Year Term Agreement: Hazard ratio $\text{HR} = 0.28$ ($p < 0.001$, strong protective effect).

### 2.3 Model 3: Explainable AI Engine (`explainer.bz2`)
- **Algorithm**: SHAP (Shapley Additive exPlanations) TreeExplainer.
- **Serialization**: Compressed bzip2 pickle (`explainer.bz2`, 7.67 MB).
- **Mathematical Guarantee**: Efficient exact Shapley values satisfying efficiency and additivity axioms across all 1,000 trees.
