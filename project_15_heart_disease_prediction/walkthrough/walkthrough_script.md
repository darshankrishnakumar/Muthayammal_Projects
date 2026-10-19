# Walkthrough Script: Heart Disease Prediction & Diagnostic Intelligence (PROJECT-015)

## Project Overview
- **Identifier**: PROJECT-015
- **Title**: CardioPredict: Multi-Factor Heart Disease Prediction and Cardiovascular Diagnostic Intelligence Using Random Forest Ensemble Learning
- **Port**: 5015 (`http://127.0.0.1:5015`)
- **Target Video Duration**: Exactly 180.0 Seconds (03:00)

---

### Step 1: Architecture & Clinical Portal (00:00 - 00:20)
**Spoken Narration**:
"Welcome to the formal demonstration of PROJECT-015: CardioPredict, an advanced cardiovascular diagnostic intelligence platform powered by Random Forest ensemble learning. Cardiovascular diseases represent the leading cause of mortality globally. By deploying machine learning across 11 non-invasive biomarkers, CardioPredict provides rapid, non-invasive risk stratification to support clinical decision-making."
**Visual Focus**:
- Full clinical portal at `http://127.0.0.1:5015/` showing hospital disclaimer, brand header, and theme controls.

---

### Step 2: Clinical Feature Form & BMI Calculator (00:20 - 00:45)
**Spoken Narration**:
"The input console organizes 11 physiological parameters into demographic, hemodynamic, metabolic, and exercise stress domains. The system includes an integrated BMI calculator that provides real-time anthropometric classification alongside blood pressure and cholesterol tracking."
**Visual Focus**:
- Form grid focusing on input fields, tooltip info icons, and dynamic BMI computation.

---

### Step 3: High-Risk Patient Assessment (00:45 - 01:15)
**Spoken Narration**:
"We input a 64-year-old male presenting with asymptomatic chest pain, resting blood pressure of 160 mm Hg, serum cholesterol of 290 mg/dL, exercise-induced angina, and 3.2 mm ST depression. Submitting the profile triggers instant Random Forest inference across 100 bagged trees, yielding a high-confidence positive alert: 'Heart Disease Detected'."
**Visual Focus**:
- Submission of high-risk profile, appearance of crimson result card, and display of one-click action buttons ('Download PDF Report' and 'View Dashboard').

---

### Step 4: Vital Signs Comparison Chart (01:15 - 01:45)
**Spoken Narration**:
"Scrolling to the interactive dashboard, our first Chart.js visualizer contrasts the patient's vital signs directly against normal population baselines. Blood pressure, max heart rate, and cholesterol readings are juxtaposed, clearly illustrating significant systolic hypertension and hypercholesterolemia."
**Visual Focus**:
- Smooth scroll to Dashboard bar chart. Inspection of Blue (Patient) vs Green (Normal Average) bars.

---

### Step 5: Multi-Factor Cardiovascular Radar Profile (01:45 - 02:10)
**Spoken Narration**:
"The cardiovascular radar profile synthesizes five normalized risk axes: Age, Blood Pressure, Cholesterol, Max Heart Rate, and ST Depression. The resulting polygon footprint provides clinicians with an instantaneous visual signature of myocardial stress."
**Visual Focus**:
- Smooth scroll to Radar chart, displaying multi-axis stress geometry and interactive vertex tooltips.

---

### Step 6: Risk Breakdown & Trend Analytics (02:10 - 02:35)
**Spoken Narration**:
"Next, the risk distribution pie chart illustrates the proportional breakdown between ischemic risk and healthy reserve, while the accompanying line chart models cardiovascular stress curves under variable physiological loads."
**Visual Focus**:
- Exploration of Pie and Line chart sections in the dashboard.

---

### Step 7: Low-Risk Patient Clearance (02:35 - 02:50)
**Spoken Narration**:
"To demonstrate diagnostic specificity, we simulate a 32-year-old female with normal blood pressure of 115 mm Hg, healthy cholesterol of 175 mg/dL, and no exercise-induced angina. The model promptly clears the patient, displaying an emerald 'No Heart Disease Detected' result."
**Visual Focus**:
- Form reset, entry of healthy parameters, and display of green safe result card.

---

### Step 8: REST API & Capstone Defense Sign-Off (02:50 - 03:00)
**Spoken Narration**:
"All 25 automated unit, API, and database tests pass with a 100% success rate. CardioPredict is fully documented, equipped with on-demand PDF report generation, and submission-ready for final-year engineering evaluation."
**Visual Focus**:
- Return to top of portal / REST API `/api/health` displaying 11 features and database connectivity. Final sign-off.
