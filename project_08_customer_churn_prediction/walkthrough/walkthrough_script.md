# Walkthrough Video Demonstration Script: Customer Churn Intelligence (PROJECT-008)

## Demonstration Metadata
- **Duration**: 03:00 (180.0 seconds)
- **Target Video File**: `walkthrough/walkthrough_video.mp4`
- **Resolution**: 1280x800, 24 fps, H.264 / AAC
- **Target URL**: `http://127.0.0.1:5008`

---

## Script Breakdown

### Section 1: Executive Analytics Dashboard & KPI Overview (00:00 - 00:25)
- **Visual**: The browser loads `http://127.0.0.1:5008/`. The camera focuses on the executive metric cards: Total Customers Analysed (7,043), Active Churn Rate (26.5%), Retained Subscriber Base, and the interactive Donut chart showing customer retention breakdown.
- **Narration**: "Welcome to the demonstration of Project 8: Customer Survival Analysis and Churn Prediction. In modern subscription telecommunications, acquiring new customers costs up to seven times more than retaining active accounts. Our enterprise retention platform unifies classical ensemble classification, semi-parametric survival hazard modeling, and explainable AI to proactively identify and deflect subscriber churn."

### Section 2: Interactive Subscriber Risk Assessment Portal (00:25 - 00:55)
- **Visual**: Navigate to `/predict`. The user reviews the comprehensive subscriber intake form structured across three cards: Section A (Demographics), Section B (Services & Add-ons), and Section C (Contract Terms, Payment Method, Monthly Charges, and Account Tenure).
- **Narration**: "Navigating to the predictive inference workspace, customer success managers can evaluate individual subscriber risk profiles. The interface accepts 21 multi-modal parameters covering demographics, fiber optic versus DSL infrastructure, value-added security bundles, contract length, and billing amounts, with real-time client-side validation."

### Section 3: Random Forest Inference & Real-Time Churn Evaluation (00:55 - 01:25)
- **Visual**: The user submits the form for a month-to-month, Fiber Optic customer. The system executes real-time inference through our 1,000-tree Random Forest classifier ($ROC-AUC = 0.844$) and scrolls down to the dedicated Navy Blue Prediction Assessment panel. The risk speedometer needle points to 78.4% (HIGH RISK), and the system calculates an expected CLTV of $477.50.
- **Narration**: "Executing real-time inference, the ensemble engine computes an estimated churn probability of 78.4%, stratifying the account into the Critical Risk tier. The model dynamically generates an automated retention prescription—recommending immediate outreach with a complimentary 3-month Tech Support bundle and a discounted 1-year contract migration."

### Section 4: Time-to-Event Survival Analysis & Hazard Trajectory (01:25 - 01:50)
- **Visual**: The user scrolls down to inspect the dual survival analysis plots: the green Kaplan-Meier & Cox Survival Probability Decay Curve and the red Cumulative Hazard Curve, with a blue vertical indicator marking the subscriber's current tenure position.
- **Narration**: "Moving beyond binary labels, our integrated Cox Proportional Hazards engine reveals the time-to-event dynamics. The green survival curve tracks retention decay across 72 tenure months, while the cumulative hazard trajectory identifies acute inflection windows, enabling retention teams to time promotional offers before defection risk peaks."

### Section 5: Explainable AI (XAI) via SHAP Feature Attribution (01:50 - 02:15)
- **Visual**: The page scrolls to the SHAP Feature Impact Breakdown waterfall visualization. Key drivers are highlighted: month-to-month contract terms and high monthly charges heavily increase churn likelihood, while the absence of online security removes key retention anchors.
- **Narration**: "To satisfy regulatory compliance and ensure operational transparency, the platform integrates SHAP game-theoretic explainability. The waterfall chart decomposes the exact mathematical contribution of each subscriber attribute, proving to stakeholders precisely why the model arrived at its high-risk verdict."

### Section 6: Model Performance Benchmarks & Validation Leaderboard (02:15 - 02:35)
- **Visual**: Navigate to `/model-performance`. The screen displays the held-out test evaluation suite: Accuracy (80.4%), ROC-AUC (0.844), Precision (66.8%), Recall (54.2%), the Confusion Matrix (804 TN, 275 TP), and the global Feature Importance ranking.
- **Narration**: "On the Model Performance dashboard, empirical validation on 1,409 unseen test records confirms outstanding discrimination capability with an ROC-AUC of 0.844. Feature importance rankings demonstrate that account tenure and contractual commitment drive over 40% of overall predictive variance."

### Section 7: Relational Transaction History & SQLite Audit Trail (02:35 - 02:50)
- **Visual**: Navigate to `/history`. The table displays the chronological log of all predictions stored in the SQLite `predictions.db` ledger, showing customer IDs, timestamps, churn probabilities, risk levels, and suggested retention actions.
- **Narration**: "Every evaluation generated through the portal or REST API is transactionally committed to our ACID-compliant SQLite audit ledger, establishing a permanent record for compliance review and longitudinal effectiveness tracking."

### Section 8: Summary & Final Capstone Acceptance (02:50 - 03:00)
- **Visual**: Return to `/` executive dashboard.
- **Narration**: "Project 8 delivers a complete, verified, enterprise-ready retention intelligence platform uniting machine learning classification, survival analysis, explainability, and relational auditing. Thank you."
