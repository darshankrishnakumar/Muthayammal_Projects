import os
import sys
import json
import csv
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ml.transformer_matching_model import TransformerSemanticMatcherNet
from backend.app.ml.candidate_competency_model import CandidateCompetencyRegressorNet

def run_training():
    print("=" * 70)
    print("  PROJECT-044: TRAINING RESUME SCREENING & NLP MATCHING MODELS (6,000 ROWS)")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    print(f"Using compute acceleration device: {device}")

    # Set seeds
    torch.manual_seed(44)
    np.random.seed(44)
    random.seed(44)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    exp_dir = os.path.join(base_dir, "experiments")
    models_dir = os.path.join(base_dir, "backend", "models")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "resume_matching_telemetry_6000.csv")

    job_roles = [
        ("JOB-AI-LEAD", "Lead AI/ML Research Engineer", "Artificial Intelligence", 5.0, "PyTorch, Transformers, Python, CUDA, Distributed Training, FastAPI"),
        ("JOB-FULLSTACK", "Senior Fullstack Cloud Architect", "Engineering", 4.0, "React, Node.js, TypeScript, PostgreSQL, Docker, AWS, Kubernetes"),
        ("JOB-DEVOPS", "Site Reliability & Cloud DevOps Specialist", "Infrastructure", 3.5, "Terraform, Kubernetes, Docker, Prometheus, CI/CD, Go, Linux"),
        ("JOB-DATA-SCI", "Principal Predictive Data Scientist", "Analytics", 4.0, "Python, SQL, Scikit-Learn, PySpark, BigQuery, Statistics, MLOps")
    ]

    first_names = ["Elena", "Liam", "Sophia", "Aarav", "Zoe", "Mateo", "Ananya", "Lucas", "Maya", "Noah", "Olivia", "Ethan"]
    last_names = ["Rostova", "Smith", "Rossi", "Patel", "Vargas", "Chen", "Sharma", "Dubois", "Kim", "Tanaka", "Muller", "O'Connor"]

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Generate 6,000-Record Telemetry Dataset
    # ─────────────────────────────────────────────────────────────────────────
    print(f"Generating 6,000 synthetic resume matching telemetry records at {csv_path}...")
    fieldnames = [
        "match_id", "candidate_name", "job_id", "job_title", "department",
        "candidate_experience_years", "min_years_required", "skill_coverage_pct",
        "semantic_similarity", "experience_fit_score", "certification_count",
        "education_level_index", "github_contributions", "soft_skills_score",
        "overall_match_score", "screening_decision", "seniority_compatibility"
    ]

    total_records = 6000
    rows = []
    regressor_features = []
    regressor_targets = []
    cand_embeddings = np.zeros((total_records, 128), dtype=np.float32)
    job_embeddings = np.zeros((total_records, 128), dtype=np.float32)
    match_targets = []

    for i in range(total_records):
        m_id = f"MAT-2026-{10000 + i}"
        j_idx = i % len(job_roles)
        jid, jtitle, jdept, j_req_exp, j_skills = job_roles[j_idx]
        c_name = f"{first_names[i % len(first_names)]} {last_names[(i * 3) % len(last_names)]}"

        # 30% Shortlisted (>=80%), 40% Review (60-80%), 30% Rejected (<60%)
        tier_mod = i % 10
        if tier_mod in [0, 1, 2]: # Shortlisted
            exp_yrs = random.uniform(j_req_exp, j_req_exp + 5.0)
            skill_cov = random.uniform(82.0, 98.0)
            sem_sim = random.uniform(0.85, 0.98)
            certs = random.randint(2, 6)
            edu_idx = random.choice([3, 4]) # Master / PhD
            gh_contribs = random.randint(25, 120)
            soft_skills = random.uniform(8.0, 9.8)
            overall = random.uniform(82.0, 98.5)
            decision = "SHORTLISTED"
            seniority = random.uniform(85.0, 99.0)
        elif tier_mod in [3, 4, 5, 6]: # Review
            exp_yrs = random.uniform(j_req_exp - 1.5, j_req_exp + 1.0)
            skill_cov = random.uniform(60.0, 80.0)
            sem_sim = random.uniform(0.65, 0.82)
            certs = random.randint(1, 3)
            edu_idx = random.choice([2, 3]) # Bachelor / Master
            gh_contribs = random.randint(5, 30)
            soft_skills = random.uniform(6.5, 8.2)
            overall = random.uniform(62.0, 79.5)
            decision = "REVIEW"
            seniority = random.uniform(60.0, 82.0)
        else: # Rejected
            exp_yrs = random.uniform(0.5, max(1.0, j_req_exp - 1.5))
            skill_cov = random.uniform(20.0, 55.0)
            sem_sim = random.uniform(0.30, 0.58)
            certs = random.randint(0, 1)
            edu_idx = random.choice([1, 2]) # High School / Bachelor
            gh_contribs = random.randint(0, 8)
            soft_skills = random.uniform(4.0, 6.5)
            overall = random.uniform(25.0, 58.0)
            decision = "REJECTED"
            seniority = random.uniform(20.0, 55.0)

        exp_fit = min(10.0, (exp_yrs / j_req_exp) * 10.0)

        row = {
            "match_id": m_id,
            "candidate_name": c_name,
            "job_id": jid,
            "job_title": jtitle,
            "department": jdept,
            "candidate_experience_years": round(exp_yrs, 1),
            "min_years_required": j_req_exp,
            "skill_coverage_pct": round(skill_cov, 1),
            "semantic_similarity": round(sem_sim, 3),
            "experience_fit_score": round(exp_fit, 1),
            "certification_count": certs,
            "education_level_index": edu_idx,
            "github_contributions": gh_contribs,
            "soft_skills_score": round(soft_skills, 1),
            "overall_match_score": round(overall, 1),
            "screening_decision": decision,
            "seniority_compatibility": round(seniority, 1)
        }
        rows.append(row)

        # 10 Regressor features
        x_reg = [
            exp_yrs, j_req_exp, skill_cov, sem_sim, exp_fit,
            float(certs), float(edu_idx), float(gh_contribs), soft_skills, overall
        ]
        y_reg = [overall, sem_sim, exp_fit, seniority]
        regressor_features.append(x_reg)
        regressor_targets.append(y_reg)

        # Synthetic 128-D Contextual Embeddings
        c_base = np.random.randn(128).astype(np.float32)
        c_base /= np.linalg.norm(c_base)
        # Shift candidate embedding towards job vector based on semantic similarity
        j_base = np.random.randn(128).astype(np.float32)
        j_base /= np.linalg.norm(j_base)

        c_emb = (1.0 - sem_sim) * c_base + sem_sim * j_base
        c_emb /= np.linalg.norm(c_emb)

        cand_embeddings[i] = c_emb
        job_embeddings[i] = j_base
        match_targets.append(overall / 100.0)

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} records in {csv_path} ({os.path.getsize(csv_path)} bytes).")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Train TransformerSemanticMatcherNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining TransformerSemanticMatcherNet on 128-D Cross-Attention Projections...")
    train_size = 4800
    val_size = 1200

    c_tensor = torch.tensor(cand_embeddings, dtype=torch.float32)
    j_tensor = torch.tensor(job_embeddings, dtype=torch.float32)
    m_tensor = torch.tensor(match_targets, dtype=torch.float32).unsqueeze(-1)

    ds_tf = TensorDataset(c_tensor, j_tensor, m_tensor)
    train_tf_ds, val_tf_ds = torch.utils.data.random_split(ds_tf, [train_size, val_size])

    train_tf_loader = DataLoader(train_tf_ds, batch_size=64, shuffle=True)
    val_tf_loader = DataLoader(val_tf_ds, batch_size=64, shuffle=False)

    model_tf = TransformerSemanticMatcherNet(emb_dim=128).to(device)
    optimizer_tf = torch.optim.AdamW(model_tf.parameters(), lr=2e-3, weight_decay=1e-4)
    criterion_tf = nn.MSELoss()

    for epoch in range(15):
        model_tf.train()
        for bc, bj, bm in train_tf_loader:
            bc, bj, bm = bc.to(device), bj.to(device), bm.to(device)
            optimizer_tf.zero_grad()
            pred = model_tf(bc, bj)
            loss = criterion_tf(pred, bm)
            loss.backward()
            optimizer_tf.step()

    model_tf.eval()
    errors_tf = []
    with torch.no_grad():
        for bc, bj, bm in val_tf_loader:
            bc, bj, bm = bc.to(device), bj.to(device), bm.to(device)
            pred = model_tf(bc, bj)
            err = torch.abs(pred - bm).cpu().numpy()
            errors_tf.append(err)

    mae_tf = float(np.mean(np.concatenate(errors_tf, axis=0)) * 100.0)
    print(f"TransformerSemanticMatcherNet Validation Match Score MAE: {mae_tf:.2f}%")

    phase2_weights = os.path.join(exp_dir, "phase2_model.pt")
    baseline_weights = os.path.join(exp_dir, "baseline_model.pt")
    torch.save(model_tf.state_dict(), phase2_weights)
    torch.save(model_tf.state_dict(), baseline_weights)
    print(f"Saved TransformerSemanticMatcherNet weights to {phase2_weights} ({os.path.getsize(phase2_weights)} bytes)")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Train CandidateCompetencyRegressorNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining CandidateCompetencyRegressorNet...")
    X_reg_arr = np.array(regressor_features, dtype=np.float32)
    Y_reg_arr = np.array(regressor_targets, dtype=np.float32)

    mean_x = np.mean(X_reg_arr, axis=0).tolist()
    std_x = (np.std(X_reg_arr, axis=0) + 1e-6).tolist()

    X_norm = (X_reg_arr - np.array(mean_x, dtype=np.float32)) / np.array(std_x, dtype=np.float32)

    x_reg_t = torch.tensor(X_norm, dtype=torch.float32)
    y_reg_t = torch.tensor(Y_reg_arr, dtype=torch.float32)

    ds_reg = TensorDataset(x_reg_t, y_reg_t)
    train_r_ds, val_r_ds = torch.utils.data.random_split(ds_reg, [train_size, val_size])

    train_r_loader = DataLoader(train_r_ds, batch_size=64, shuffle=True)
    val_r_loader = DataLoader(val_r_ds, batch_size=64, shuffle=False)

    regressor = CandidateCompetencyRegressorNet(in_features=10).to(device)
    optimizer_reg = torch.optim.AdamW(regressor.parameters(), lr=2e-3, weight_decay=1e-4)
    criterion_l1 = nn.SmoothL1Loss()

    for epoch in range(20):
        regressor.train()
        for bx, by in train_r_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer_reg.zero_grad()
            p_match, p_skill, p_exp, p_sen = regressor(bx)
            p_out = torch.cat([p_match, p_skill, p_exp, p_sen], dim=-1)
            loss = criterion_l1(p_out, by)
            loss.backward()
            optimizer_reg.step()

    regressor.eval()
    errors = []
    with torch.no_grad():
        for bx, by in val_r_loader:
            bx, by = bx.to(device), by.to(device)
            p_match, p_skill, p_exp, p_sen = regressor(bx)
            p_out = torch.cat([p_match, p_skill, p_exp, p_sen], dim=-1)
            err = torch.abs(p_out - by).cpu().numpy()
            errors.append(err)

    all_err = np.concatenate(errors, axis=0)
    mae = np.mean(all_err, axis=0)
    print(f"Regressor Validation MAEs:")
    print(f"  • Overall Match Score: {mae[0]:.2f}%")
    print(f"  • Skill Overlap Ratio: {mae[1]:.3f}")
    print(f"  • Experience Fit: {mae[2]:.2f} pts")
    print(f"  • Seniority Index: {mae[3]:.2f}%")

    reg_weights_path = os.path.join(models_dir, "candidate_competency_regressor_weights.pt")
    torch.save(regressor.state_dict(), reg_weights_path)
    print(f"Saved regressor weights to {reg_weights_path} ({os.path.getsize(reg_weights_path)} bytes)")

    # 4. Save Scalers
    scalers_path = os.path.join(models_dir, "resume_scalers.json")
    scalers_data = {
        "features": fieldnames[5:15],
        "mean": mean_x,
        "std": std_x,
        "targets": ["overall_match_score", "skill_overlap_ratio", "experience_fit_score", "seniority_compatibility"]
    }
    with open(scalers_path, "w") as f:
        json.dump(scalers_data, f, indent=2)

    # 5. Save Metadata
    meta_path = os.path.join(models_dir, "model_metadata.json")
    meta_data = {
        "model_name": "TransformerSemanticMatcherNet + CandidateCompetencyRegressorNet",
        "transformer_semantic_matcher": {
            "parameters": sum(p.numel() for p in model_tf.parameters()),
            "embedding_dim": 128,
            "validation_match_mae": round(float(mae_tf), 2),
            "status": "TRAINED_SERIALIZED"
        },
        "competency_regressor": {
            "parameters": sum(p.numel() for p in regressor.parameters()),
            "match_score_mae": round(float(mae[0]), 2),
            "skill_overlap_mae": round(float(mae[1]), 3),
            "experience_fit_mae": round(float(mae[2]), 2),
            "seniority_mae": round(float(mae[3]), 2),
            "status": "TRAINED_SERIALIZED"
        },
        "dataset_records": 6000,
        "status": "TRAINED_SERIALIZED"
    }
    with open(meta_path, "w") as f:
        json.dump(meta_data, f, indent=2)

    print("Project 44 Model Training and Serialization Complete!")

if __name__ == "__main__":
    run_training()
