# System Architecture: AI Skill-Gap Analysis & Career Recommendation (PROJECT-045)

## 1. System Topology Overview
The AI-Powered Skill-Gap Analysis and Personalized Career Path Recommendation Platform implements a dual-engine deep learning microservice architecture designed for enterprise workforce intelligence, automated upskilling navigation, and immutable cryptographic record-keeping.

```
+---------------------------------------------------------------------------------+
|                       USER COMPETENCY PROFILE INGESTION                         |
|    [Self-Reported / Evaluated Competency Tokens, Experience, Certs, Budget]     |
|    - Target Career Role Aspiration (AI, Cloud, Data Science, Cybersecurity)     |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                     DUAL-ENGINE PYTORCH INFERENCE PIPELINE                      |
|  +-------------------------------------+   +---------------------------------+  |
|  | CompetencyEmbeddingNet              |   | CareerTrajectoryForecastNet     |  |
|  | - 64-D Latent Competency Space      |   | - 10-Feature Normalized Trunk   |  |
|  | - Non-Linear User/Role Projections  |   | - 4 Multi-Target Output Heads:  |  |
|  | - Joint Embedding Fusion (128-D)    |   |   Role Readiness % (MAE: 2.77%) |  |
|  | - 25,000 Parameters (phase2_model)  |   |   Skill Gap % (MAE: 2.81%)      |  |
|  | - Gap & Timeline Latent Prediction  |   |   Transition Wks (MAE: 0.78 wks)|  |
|  |                                     |   |   Salary Growth (MAE: 2.75%)    |  |
|  +-------------------------------------+   +---------------------------------+  |
+---------------------------------------------------------------------------------+
                                       |
                                       v (Readiness, Gap, Transition Weeks, Curated Courses)
+---------------------------------------------------------------------------------+
|                    TOPOLOGICAL LEARNING ROADMAP GENERATOR                       |
|  - High Readiness (>= 80%)    --> Fast-Track Capstone Projects & Specializations|
|  - Moderate Gap (60% to 79%)  --> Targeted Certification & Intermediate Labs   |
|  - Significant Gap (< 60%)    --> Structured Foundation-to-Advanced Roadmap    |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                 PERSISTENT RELATIONAL SQLITE (WAL MODE)                         |
|  [career_roles] [roadmaps]                                                      |
|  [audit_ledger (SHA-256 Merkle Block Chaining with Genesis Seeding)]            |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|               REST API MICROSERVICE (:5045) & INTERACTIVE HUD                   |
|  - 60 FPS Competency Graph Canvas        - Trajectory Multi-Head Breakdown Chart|
|  - Profile Presets & Study Controls      - Cryptographic Block Chain Explorer   |
+---------------------------------------------------------------------------------+
```
