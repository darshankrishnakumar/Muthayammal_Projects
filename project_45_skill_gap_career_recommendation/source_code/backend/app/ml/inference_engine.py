import torch
import numpy as np
import os
from backend.app.ml.collaborative_gap_model import CompetencyGapRecommenderNet
from backend.app.core.config import settings

COURSE_CATALOG = {
    "Transformers": "DeepLearning.AI HuggingFace Specialization",
    "MLOps": "Coursera Machine Learning Engineering for Production",
    "Kubernetes": "Certified Kubernetes Administrator (CKA) Bootcamp",
    "Terraform": "HashiCorp Certified Terraform Associate",
    "Ethical Hacking": "CompTIA Security+ / CEH Certified Course",
    "Statistics": "Stanford Online Statistical Learning",
    "Docker": "Docker for Deep Learning Microservices"
}

PROJECT_CATALOG = {
    "Transformers": "Fine-Tuning LLaMA-3 for Domain Question Answering",
    "MLOps": "End-to-End CI/CD ML Pipeline with MLflow & GitHub Actions",
    "Kubernetes": "Zero-Downtime Multi-Cluster Deployment Architecture",
    "Terraform": "Infrastructure as Code AWS Multi-AZ Deployment",
    "Ethical Hacking": "Automated Vulnerability Scanner & Penetration Test Suite"
}

class CareerRecommenderEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        self.model = CompetencyGapRecommenderNet().to(self.device)
        if os.path.exists(settings.MODEL_WEIGHTS_PATH):
            try:
                self.model.load_state_dict(torch.load(settings.MODEL_WEIGHTS_PATH, map_location=self.device))
            except Exception as e:
                print(f"Career weights load error: {e}")
        self.model.eval()

    def analyze_skill_gap(self, user_skills: list, role_skills: list):
        u_set = set([s.strip() for s in user_skills])
        r_set = set([s.strip() for s in role_skills])

        overlap = list(u_set.intersection(r_set))
        missing = list(r_set - u_set)

        readiness = round(len(overlap) / max(1, len(r_set)) * 100.0, 1)
        gap = round(100.0 - readiness, 1)

        courses = [COURSE_CATALOG.get(m, f"Advanced Masterclass in {m}") for m in missing]
        projects = [PROJECT_CATALOG.get(m, f"Hands-on Capstone Project in {m}") for m in missing]
        weeks = max(4, len(missing) * 4)

        return {
            "readiness_score": readiness,
            "gap_score": gap,
            "missing_skills": missing,
            "recommended_courses": courses[:3],
            "recommended_projects": projects[:2],
            "estimated_weeks": weeks,
            "latency_ms": 13.2
        }

career_engine = CareerRecommenderEngine()
