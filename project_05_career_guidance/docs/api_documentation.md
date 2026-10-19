# REST API Documentation - Career Guidance AI

The Career Guidance AI microservice provides asynchronous REST endpoints running on `http://127.0.0.1:5005`.

---

## 1. System Health & Status

### `GET /api/health`
Returns system status, active ML models, real-time dataset evaluation metrics, and SQLite database connection stats.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Career Guidance & Job Role Recommendation AI",
  "models_available": ["XGBoost", "Random Forest", "Decision Tree"],
  "metrics": {
    "XGBoost": {
      "accuracy": 0.04725,
      "top3_accuracy": 0.11875,
      "top5_accuracy": 0.16375,
      "f1_macro": 0.0458
    },
    "Random Forest": {
      "accuracy": 0.03825,
      "top3_accuracy": 0.0995,
      "top5_accuracy": 0.1475,
      "f1_macro": 0.0369
    },
    "Decision Tree": {
      "accuracy": 0.0315,
      "top3_accuracy": 0.0825,
      "top5_accuracy": 0.1245,
      "f1_macro": 0.0308
    }
  },
  "database": {
    "status": "operational",
    "file": ".../source_code/career_guidance.db",
    "total_assessments": 14
  },
  "timestamp": 1776584000.12
}
```

---

## 2. Pre-configured Student Profiles

### `GET /api/presets`
Returns curated student archetypes covering 5 dominant career paths for one-click testing and demonstration.

**Response (200 OK):**
```json
{
  "status": "success",
  "presets": {
    "fullstack_dev": {
      "title": "Full-Stack Software Developer",
      "profile": { ... }
    },
    "cloud_devops": {
      "title": "Cloud & Systems Architect",
      "profile": { ... }
    },
    "cyber_security": {
      "title": "Cybersecurity & Network Analyst",
      "profile": { ... }
    },
    "database_admin": {
      "title": "Database & Big Data Architect",
      "profile": { ... }
    },
    "ui_ux_designer": {
      "title": "UI/UX & Product Experience",
      "profile": { ... }
    }
  }
}
```

---

## 3. Comparative Model Evaluation Metrics

### `GET /api/metrics`
Returns multiclass evaluation metrics across all 34 career roles for XGBoost, Random Forest, and CART Decision Tree.

**Response (200 OK):**
```json
{
  "status": "success",
  "metrics": {
    "XGBoost": {
      "accuracy": 0.04725,
      "top3_accuracy": 0.11875,
      "top5_accuracy": 0.16375,
      "f1_macro": 0.0458,
      "f1_weighted": 0.0465,
      "total_test_samples": 4000,
      "classes_count": 34
    },
    "Random Forest": { ... },
    "Decision Tree": { ... }
  }
}
```

---

## 4. Career Prediction & Assessment

### `POST /api/predict`
Evaluates a student's 38-dimensional profile against the selected machine learning model, persists the assessment into SQLite, and returns primary career recommendation, confidence, alternative career pathways, and skill radar vectors.

**Request Payload:**
```json
{
  "student_name": "Alex Rivera",
  "model_name": "XGBoost",
  "profile": {
    "Acedamic percentage in Operating Systems": 85,
    "percentage in Algorithms": 88,
    "Percentage in Programming Concepts": 92,
    "Percentage in Software Engineering": 86,
    "Percentage in Computer Networks": 84,
    "Percentage in Electronics Subjects": 75,
    "Percentage in Computer Architecture": 80,
    "Percentage in Mathematics": 85,
    "Percentage in Communication skills": 82,
    "Hours working per day": 8,
    "Logical quotient rating": 8,
    "hackathons": 4,
    "coding skills rating": 8,
    "public speaking points": 6,
    "can work long time before system?": "yes",
    "self-learning capability?": "yes",
    "Extra-courses did": "yes",
    "certifications": "app development",
    "workshops": "web technologies",
    "talenttests taken?": "yes",
    "olympiads": "yes",
    "reading and writing skills": "medium",
    "memory capability score": "excellent",
    "Interested subjects": "Software Engineering",
    "interested career area ": "developer",
    "Job/Higher Studies?": "job",
    "Type of company want to settle in?": "Web Services",
    "Taken inputs from seniors or elders": "yes",
    "interested in games": "no",
    "Interested Type of Books": "Technical books",
    "Salary Range Expected": "salary",
    "In a Realtionship?": "no",
    "Gentle or Tuff behaviour?": "gentle",
    "Management or Technical": "Technical",
    "Salary/work": "work",
    "hard/smart worker": "smart worker",
    "worked in teams ever?": "yes",
    "Introvert": "no"
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "assessment_id": 15,
  "student_name": "Alex Rivera",
  "model_used": "XGBoost",
  "recommended_role": "Full-Stack Software Developer",
  "confidence": 0.245,
  "category": "Software Engineering & Architecture",
  "description": "Designs, architects, and implements end-to-end client and server applications...",
  "recommended_certifications": ["AWS Certified Solutions Architect", "CKA", "Meta Professional Developer"],
  "salary_bracket": "$95,000 - $145,000 / year",
  "top_pathways": [
    { "role": "Full-Stack Software Developer", "probability": 0.245 },
    { "role": "Software Engineer", "probability": 0.182 },
    { "role": "Web Developer", "probability": 0.125 },
    { "role": "Applications Developer", "probability": 0.089 },
    { "role": "Database Developer", "probability": 0.064 }
  ],
  "radar_vectors": {
    "academics": 84.1,
    "coding": 88.9,
    "problem_solving": 80.0,
    "collaboration": 85.0,
    "self_learning": 90.0
  }
}
```

---

## 5. Historical Assessment Records

### `GET /api/history`
Retrieves past student evaluation logs from SQLite with pagination.

**Query Parameters:**
- `limit` (int, default=20): Max records to retrieve.

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 15,
  "history": [
    {
      "id": 15,
      "timestamp": "2026-10-19 13:10:22",
      "student_name": "Alex Rivera",
      "model_used": "XGBoost",
      "recommended_role": "Full-Stack Software Developer",
      "confidence": 0.245,
      "category": "Software Engineering & Architecture"
    }
  ]
}
```

---

## 6. Clear History

### `POST /api/history/clear`
Clears assessment records for fresh batch evaluation demonstrations.
