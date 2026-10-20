# System Architecture: AI Resume Screening & Contextual Job Matching (PROJECT-044)

## 1. System Topology Overview
The AI-Based Resume Screening and Contextual Job Matching Platform implements a dual-engine deep learning microservice architecture designed for enterprise talent acquisition, unbiased candidate ranking, and immutable cryptographic record-keeping.

```
+---------------------------------------------------------------------------------+
|                        APPLICANT PROFILE INGESTION                              |
|    [Unstructured Resume Parser / Structured Profile Formats]                    |
|    - Technical Skills, Experience Years, Certifications, Education Tier, Repos |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                     DUAL-ENGINE PYTORCH INFERENCE PIPELINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | TransformerSemanticMatcherNet       |   | CandidateCompetencyRegressorNet |  |
|  | - 128-D Contextual SBERT Projection |   | - 10-Feature Normalized Trunk   |  |
|  | - Cross-Attention Differential Core |   | - 4 Multi-Target Output Heads:  |  |
|  | - Candidate & Job Embedding Fusion  |   |   Overall Match % (MAE: 0.44%), |  |
|  | - 58,241 Parameters (238 KB)        |   |   Skill Overlap (MAE: 0.029),   |  |
|  | - Validation MAE: 16.26%            |   |   Experience Fit (MAE: 0.08 pts)|  |
|  |                                     |   |   Seniority Index (MAE: 5.83%)  |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Overall Match Score, Decisions, Evidence Hash)
+---------------------------------------------------------------------------------+
|                      ATS SHORTLISTING & SCREENING TIERS                         |
|  - Overall Match >= 80.0% --> SHORTLISTED (Interview Fast-Track Invitation)     |
|  - 60.0% <= Match < 80.0% --> REVIEW (Secondary Technical Recruiter Triage)    |
|  - Overall Match < 60.0%  --> REJECTED (Automated Feedback with Deficit Report)|
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [job_openings] [candidate_matches]                                             |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5044) & INTERACTIVE HUD                   |
|  - 60 FPS Attention Radar Canvas         - Competency Regressor Dimension Chart |
|  - Candidate Profile Presets Switcher    - Cryptographic Block Chain Explorer   |
+---------------------------------------------------------------------------------+
```
