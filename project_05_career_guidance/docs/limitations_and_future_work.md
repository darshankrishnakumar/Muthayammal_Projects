# Limitations and Future Work - Career Guidance AI

## 1. Current System Limitations

1. **Multiclass Class Granularity**:
   The Kaggle dataset defines 34 distinct job titles (e.g., "Software Engineer", "Applications Developer", "Database Developer", "Web Developer"). In reality, many of these roles share overlapping academic and skill requirements, which compresses discrete Top-1 classification accuracy.
2. **Self-Reported Ratings**:
   Variables such as "Logical quotient rating" (1–9), "coding skills rating" (1–9), and "public speaking points" (1–9) rely on subjective student self-assessment, introducing variance compared to standardized psychometric evaluations.
3. **Static Skill Categorization**:
   The system maps fixed skills to technology roles. Emerging fields such as Generative AI Engineering, MLOps, and Quantum Computing are not represented in the legacy 34-class taxonomy.
4. **Standalone Local Architecture**:
   The application currently runs as a local Flask microservice with SQLite. It does not integrate campus-wide Single Sign-On (SSO) or institutional Learning Management Systems (LMS) such as Canvas or Moodle.

---

## 2. Roadmap & Future Work

1. **Hierarchical Multi-Level Classification**:
   Refactor the 34 classes into 5 primary clusters (Development, Systems/Cloud, Data/AI, Security, Product/Design) followed by second-stage specialized role prediction to improve Top-1 accuracy to >80%.
2. **Automated GitHub & Resume Parsing**:
   Integrate GitHub API scraping and PDF resume extraction using LangChain / LLM embeddings to automatically populate technical skills rather than relying on manual slider inputs.
3. **Real-Time Job Market Integration**:
   Connect live career APIs (LinkedIn, Indeed, Adzuna) to fetch real-time salary distributions, open vacancies, and demanded prerequisite certifications by geographic region.
4. **Personalized Skill Gap Roadmaps**:
   Generate dynamic 6-month learning pathways with curated Coursera/edX course recommendations addressing specific identified weaknesses.
