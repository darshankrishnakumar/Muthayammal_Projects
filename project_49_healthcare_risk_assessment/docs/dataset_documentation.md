# Dataset Documentation — PROJECT-049
## Patient Clinical Telemetry Benchmark (6,000 Records)

### 1. Overview
The benchmark dataset is located at `source_code/data/patient_telemetry_6000.csv` and contains exactly 6,000 physical telemetry records balanced across 4 clinical cohorts:
- **DIABETIC_METABOLIC** (1,500 records): Decompensated diabetes, high HbA1c, elevated BMI.
- **HYPERTENSIVE_CVD** (1,500 records): Elevated SBP/DBP, dyslipidemia, high atherogenic LDL.
- **RENAL_CKD** (1,500 records): Impaired eGFR (<60 mL/min), secondary hypertension.
- **NORMOTENSIVE_CONTROL** (1,500 records): Healthy normal physiological baseline.

### 2. Feature Schema & Clinical Ranges
1. `assessment_id`: Unique assessment record key (RISK-2026-XXXX).
2. `patient_id`: Patient identifier (PAT-2026-XXXX).
3. `full_name`: Synthesized patient demographic name.
4. `cohort`: Clinical study cohort.
5. `age`: Patient chronological age (18 to 90 years).
6. `gender`: Patient sex (Male / Female).
7. `systolic_bp`: Systolic blood pressure (80 to 220 mmHg).
8. `diastolic_bp`: Diastolic blood pressure (50 to 125 mmHg).
9. `hba1c`: Glycated hemoglobin percentage (4.5% to 14.0%).
10. `fasting_glucose`: Fasting plasma glucose (70 to 350 mg/dL).
11. `total_cholesterol`: Serum total cholesterol (120 to 360 mg/dL).
12. `hdl_cholesterol`: High-density lipoprotein (20 to 85 mg/dL).
13. `ldl_cholesterol`: Low-density lipoprotein (50 to 260 mg/dL).
14. `egfr`: Estimated glomerular filtration rate (10 to 130 mL/min/1.73m²).
15. `bmi`: Body Mass Index (18.5 to 50.0 kg/m²).
16. `cardiovascular_risk_pct`: 10-year CVD risk percentage (4.0% to 96.0%).
17. `type2_diabetes_risk_pct`: Type 2 diabetes progression risk (3.0% to 98.0%).
18. `hypertension_risk_pct`: Essential hypertension risk (5.0% to 99.0%).
19. `ckd_risk_pct`: Chronic kidney disease risk (2.0% to 95.0%).
20. `composite_risk_tier`: Risk classification (LOW, MODERATE, HIGH, CRITICAL).
21. `ten_year_mortality_risk_pct`: All-cause 10-year mortality risk (2.0% to 92.0%).
22. `hospital_readmission_risk_pct`: 30-day hospital readmission risk (3.0% to 88.0%).
23. `polypharmacy_complexity_index`: Regimen complexity index (5.0% to 95.0%).
24. `renal_progression_hazard_pct`: Renal decline hazard (1.0% to 95.0%).

### 3. Data Integrity & Validation
- Null values: 0 across all 26 columns.
- Systolic BP correlates strongly with hypertension risk (r > 0.75).
- HbA1c correlates strongly with type-2 diabetes risk (r > 0.75).
- eGFR correlates negatively with CKD risk (r < -0.75).
