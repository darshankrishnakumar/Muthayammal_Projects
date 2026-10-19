# Customer Survival Analysis and Churn Prediction System (PROJECT-008)

## 1. Project Overview & Abstract
In the modern subscription-driven telecommunications industry, customer retention directly governs organizational profitability and customer lifetime value (CLTV). While conventional customer churn models treat defection purely as a static binary classification problem, this approach fails to convey the temporal risk trajectory—obscuring *when* a customer is most vulnerable to churn and *why* specific service combinations accelerate defection.

PROJECT-008 implements an enterprise-grade, dual-model retention intelligence system combining:
1. **Instantaneous Churn Probability Estimation**: A calibrated Random Forest Classifier achieving 80.4% accuracy and 0.844 ROC-AUC on the benchmark IBM Telco Churn corpus.
2. **Dynamic Time-to-Event Survival Modeling**: A semi-parametric Cox Proportional Hazards model mapping individual subscriber survival probability $S(t)$ and cumulative hazard $H(t)$ across 72 tenure months.
3. **Explainable AI (XAI)**: SHAP (Shapley Additive exPlanations) TreeExplainer decomposing exact feature contributions and hazard multipliers per customer.
4. **Relational Transaction Ledger**: An embedded SQLite database (`predictions.db`) providing full audit persistence, historical analytics, and automated retention recommendations.

## 2. Directory Architecture
```
project_08_customer_churn_prediction/
├── docs/                               # Comprehensive academic documentation
│   ├── README.md                       # High-level system overview (this document)
│   ├── architecture.md                 # System diagrams, dataflow, and design patterns
│   ├── dataset_and_model_details.md    # IBM Telco schema, Cox theory, and Random Forest tuning
│   ├── api_documentation.md            # REST API endpoints and payload schemas
│   ├── setup_and_execution.md          # Installation, dependency management, and run guide
│   ├── testing_report.md               # Automated testing suite and validation results
│   ├── limitations_and_future_work.md  # Production trade-offs and future enhancements
│   ├── third_party_notices.md          # Open-source licensing disclosures
│   ├── acceptance_report.md            # Capstone verification and audit findings
│   ├── screenshots/                    # High-resolution application UI captures
│   └── technical_documentation.docx    # Formal 50+ paragraph academic technical report
├── presentations/                      # 15-slide widescreen presentation deck
│   └── project_presentation.pptx       # Slide deck embedding real UI screenshots
├── source_code/                        # Microservice application source code
│   ├── Customer-Survival-Analysis-and-Churn-Prediction-master/
│   │   ├── app.py                      # Flask WSGI web application and REST API server
│   │   ├── database.py                 # SQLite database schema, CRUD, and transaction logging
│   │   ├── seed_db.py                  # Database bootstrap and demo record seeder
│   │   ├── model.pkl                   # Trained Random Forest Classifier (38 MB)
│   │   ├── survivemodel.pkl            # Trained Cox Proportional Hazards Model (710 KB)
│   │   ├── explainer.bz2               # Compressed serialized SHAP TreeExplainer
│   │   ├── Telco-Customer-Churn.csv    # 7,043 customer records dataset
│   │   ├── templates/                  # Jinja2 HTML5 UI templates (Bootstrap 5)
│   │   └── static/                     # CSS stylesheets, JavaScript, and asset branding
│   ├── ml-service/                     # Complementary FastAPI inference service
│   │   ├── app.py                      # FastAPI endpoints
│   │   └── train_model.py              # Scikit-learn Pipeline trainer
│   └── tests/                          # Automated QA test suite
├── walkthrough/                        # Video demonstration recording and scripts
│   ├── walkthrough_script.md           # Second-by-second narration script
│   ├── walkthrough_timestamps.md       # Exact timestamp breakdown
│   └── walkthrough_video.mp4           # 03:00 (180.0s) high-definition video recording
└── requirements.txt                    # Project root Python dependencies
```

## 3. Key Technical Specifications
- **Frameworks**: Python 3.12, Flask, Scikit-learn, Lifelines, SHAP, SQLite3, Bootstrap 5, Matplotlib
- **Port Allocation**: Port 5008 (`http://127.0.0.1:5008`)
- **Dataset Size**: 7,043 subscriber records, 21 attributes
- **Test Suite**: 20+ automated unit and integration tests passing with 100% pass rate
