# Clinical Features Data Dictionary & Physiological Significance

| Feature Name | Clinical Domain | Type | Normal Baseline | Diagnostic Significance |
|---|---|---|---|---|
| `Age` | Demographic | Continuous | 18 - 65 yrs | Risk increases with arterial stiffening and age |
| `Sex` | Demographic | Categorical (0/1) | Female (0), Male (1) | Males exhibit higher incidence before age 60 |
| `ChestPainType` | Symptom | Categorical (0-3) | Typical (0), Atypical (1), Non-anginal (2), Asymptomatic (3) | Asymptomatic ischemia carries highest silent risk |
| `RestingBP` | Hemodynamic | Continuous | 90 - 120 mm Hg | Hypertension (>140 mm Hg) damages arterial walls |
| `Cholesterol` | Lipid Panel | Continuous | 125 - 200 mg/dL | Serum cholesterol (>240 mg/dL) accelerates plaque |
| `FastingBS` | Metabolic | Binary (0/1) | ≤ 120 mg/dL (0), > 120 mg/dL (1) | Fasting blood glucose > 120 flags diabetic vasculopathy |
| `RestingECG` | Electrophysiology | Categorical (0-2) | Normal (0), ST-T (1), LVH (2) | LVH and ST abnormalities indicate cardiac hypertrophy |
| `MaxHR` | Exercise Stress | Continuous | 140 - 180 bpm | Low max heart rate reflects chronotropic incompetence |
| `ExerciseAngina`| Exercise Stress | Binary (0/1) | No (0), Yes (1) | Provocation of chest pain confirms coronary ischemia |
| `Oldpeak` | Exercise Stress | Continuous | 0.0 - 1.0 mm | ST depression > 2.0 mm indicates severe myocardial strain |
| `ST_Slope` | Exercise Stress | Categorical (0-2) | Down (0), Flat (1), Up (2) | Downsloping and flat ST slopes correlate with CAD |
