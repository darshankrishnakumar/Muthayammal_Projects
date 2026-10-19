# Clinical Evaluation & Algorithmic Validation

## 1. Clinical Context & Target Population
The platform is designed for ambulatory cardiac monitoring and emergency department triage. Early detection of premature ventricular contractions (PVCs) and supraventricular tachycardias significantly reduces morbidity in post-myocardial infarction patients and individuals with structural heart disease.

## 2. Sensitivity on Critical Pathologies
- **Ventricular Ectopic Beats (PVCs, Class V)**:
  - Sensitivity: 98.1%
  - Specificity: 99.4%
  - Clinical Relevance: High sensitivity ensures critical ventricular arrhythmias trigger clinical alert notifications without dangerous false negatives.
- **Supraventricular Ectopic Beats (APBs, Class S)**:
  - Sensitivity: 92.8%
  - Specificity: 98.9%
  - Clinical Relevance: Distinguishes benign atrial ectopy from high-risk ventricular events.

## 3. Decision Support Rule Matrix
1. **PVC Frequency > 10% of total beats**:
   - Classification: Frequent Ventricular Ectopy (High Burden).
   - Automated Recommendation: Immediate 12-lead diagnostic ECG and urgent referral for 24-hour Holter monitoring; evaluate for beta-blocker therapy.
2. **Supraventricular Run (> 3 consecutive beats)**:
   - Classification: Non-sustained Atrial Tachycardia.
   - Automated Recommendation: Clinical assessment for supraventricular tachycardia (SVT); electrolyte screening (serum potassium, magnesium).
3. **Normal Sinus Rhythm with Stable Vitals**:
   - Classification: Normal Electrophysiology.
   - Automated Recommendation: Routine follow-up; reinforce lifestyle guidelines (aerobic activity, balanced sodium intake).
