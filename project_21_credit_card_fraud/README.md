# Project 21: Credit Card Fraud Detection using Machine Learning Algorithms

| Attribute | Details |
|---|---|
| **Project Identifier** | Project 21 of 55 |
| **Domain** | Machine Learning & Fintech |
| **Directory** | `project_21_credit_card_fraud` |
| **Backend Port** | `http://localhost:5021` |
| **Frontend** | Standalone Interactive HTML (`frontend/index.html`) |

## 📄 Abstract
This Project is focused on credit card fraud detection in real world scenarios. Nowadays credit card frauds are drastically increasing in number as compared to earlier times. Criminals are using fake identity and various technologies to trap the users and get the money out of them. Therefore, it is very essential to find a solution to these types of frauds. In this proposed project we designed a model to detect the fraud activity in credit card transactions. This system can provide most of the important features required to detect illegal and illicit transactions. As technology changes constantly, it is becoming difficult to track the behavior and pattern of criminal transactions. To come up with the solution one can make use of technologies with the increase of machine learning, artificial intelligence and other relevant fields of information technology; it becomes feasible to automate this process and to save some of the intensive amounts of labor that is put into detecting credit card fraud. Initially, we will collect the credit card usage data-set by users and classify it as trained and testing dataset using a LSTM algorithm and decision trees.
Using this feasible algorithm, we can analyze the larger data-set and user provided current data-set. Then augment the accuracy of the result data. Proceeded with the application of processing of some of the attributes provided which can find affected fraud detection in viewing the graphical model of data visualization. The performance of the techniques is gauged based on accuracy, sensitivity, and specificity, precision.

## 🛠️ Implementation Phases & Methodology
### PROJECT 21 — PHASE 1
Phase 1 — Requirements, Data and Prototype
The first phase will convert the project concept into a measurable prototype for financial/business analytics. The work begins by defining the exact input, output, user flow and evaluation criteria from the project abstract. A small requirements specification will identify the primary prediction/detection task, expected classes or target value, acceptable response time, and the form in which results must be displayed.
1. Problem Definition and Scope
Define the operational scenario, target users, system boundaries, assumptions, success criteria and non-functional requirements. Separate what the model must predict from what the application must display or recommend. Identify cases that should be rejected, flagged for review, or returned with low confidence.
2. Data Preparation
Identify a suitable dataset or approved collection procedure matching the abstract. Build a data dictionary, remove unusable records, handle missing values, normalize or standardize numerical fields where appropriate, and verify labels. For image/video/audio/text projects, define preprocessing, augmentation and quality-control rules. Split data into training, validation and test sets without leakage.
3. Baseline Model and Experiment Setup
Implement a reproducible baseline using the algorithm/model family stated in the abstract when one is specified. Establish a simple reference result before introducing additional complexity. Record dataset version, preprocessing settings, model configuration, random seed, training time and evaluation metrics so that later improvements can be compared objectively.
4. Initial Application Prototype
Build the minimum user-facing workflow needed to demonstrate the core task. The prototype should accept valid input, run preprocessing, invoke the baseline model, and return the predicted result with an understandable confidence/score where supported. Keep model logic separate from the interface so the model can be replaced without rewriting the application.
Phase 1 Deliverables
Requirements and scope note; prepared dataset or data pipeline; baseline model; experiment log; initial application/prototype; and a short Phase 1 validation report documenting what works, what remains uncertain, and the measurements to be improved in Phase 2.
Project-Specific Phase 1 Work Items
• Create a clean feature/data dictionary directly from the variables described in the abstract.
• Establish baseline metrics before optimization and preserve the baseline for comparison.
• Document assumptions and data limitations that could affect generalization.

### PROJECT 21 — PHASE 2
Phase 2 — Optimization, Integration and Validation
The second phase will turn the Phase 1 prototype into a validated project for financial/business analytics. The emphasis is on improving model reliability, connecting the complete workflow, testing realistic edge cases, and producing evidence that the final system meets the defined objectives.
1. Model Improvement
Compare relevant model configurations, tune important hyperparameters, address class imbalance where present, and evaluate whether additional features or augmentation improve generalization. Use validation data for tuning and reserve the test set for final evaluation. Prefer measurable improvements over unnecessary model complexity.
2. End-to-End Integration
Connect the data/input layer, preprocessing, inference engine, result-processing logic, database or file storage where required, and user interface. Add input validation, error handling, logging and clear status messages. If recommendations, alerts, summaries, risk scores or dashboards are part of the abstract, implement them as a separate decision-support layer around the model.
3. Testing and Evaluation
Perform functional, model, integration and usability tests. Evaluate accuracy or regression error as appropriate, along with precision, recall, F1, confusion matrix, ROC-AUC, latency or other task-specific measures where relevant. Test difficult, noisy, incomplete and out-of-distribution inputs and document failure cases instead of hiding them.
4. Demonstration and Final Evidence
Prepare representative test cases, screenshots or result tables, model-comparison evidence and a final demonstration workflow. Document limitations, data constraints, privacy/security considerations where applicable, and future extensions. The final report should distinguish measured results from proposed future work.
Phase 2 Deliverables
Optimized model; integrated application; test and evaluation report; representative evidence; limitations and risk register; deployment/demo instructions; and final project documentation suitable for academic review or demonstration.
Project-Specific Phase 2 Validation
• Evaluate false positives and false negatives separately because both affect operational usefulness.
• Test previously unseen or abnormal patterns and document how the system behaves when confidence is low.
• Include basic access control, logging and protection of sensitive input/output data in the demonstration.
Final Expected Outcome
A reproducible, tested prototype that implements the project concept described in the supplied abstract, together with measurable evaluation evidence and clear documentation of limitations, assumptions and future enhancement opportunities.

## 🚀 Execution Instructions

### Step 1: Start Backend API
```bash
cd "/Users/balamurugan/Documents/orbyte globel /college project/project_21_credit_card_fraud/backend"
pip install -r requirements.txt
python3 app.py
```
The Flask REST API will start listening on `http://localhost:5021`.

### Step 2: Open Frontend Interface
- Open `/Users/balamurugan/Documents/orbyte globel /college project/project_21_credit_card_fraud/frontend/index.html` in any browser.
- Or open the central **[Master Launchpad (index.html)](../index.html)** to launch all projects from a single unified portal.
- The frontend is equipped with **dual-mode logic**: it automatically connects to the Python backend when online, and gracefully switches to intelligent client-side simulation when offline.
