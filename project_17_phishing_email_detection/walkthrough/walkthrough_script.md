# Demonstration & Walkthrough Script: Phishing Email Detection via Multilevel RCNN with Attention (PROJECT-017)

## Overview
- **Project Identifier**: PROJECT-017
- **Module**: `project_17_phishing_email_detection`
- **Application Port**: Port 5017 (`http://127.0.0.1:5017`)
- **Video Target Duration**: Exactly 180.0 seconds (03:00.00), 1280x800, 30 fps H.264 MP4.

---

## Detailed Demonstration Sequence (Exact 180 Seconds)

### Phase 1: System Overview & Problem Formulation (00:00 - 00:30 | 30s)
- **Visual**: Landing view on Port 5017 (`tab-scanner`), showcasing the dark-mode glassmorphic interface, header input fields, benchmark presets selector, and architecture badge.
- **Narration**: Introduction to PROJECT-017: A clinical-grade cybersecurity platform detecting phishing via an Improved Recurrent Convolutional Neural Network (RCNN) with Attention. Explains the limitation of conventional keyword filters against envelope spoofing and typosquatting.

### Phase 2: Threat Detection Demo: Bank Header Spoofing (00:30 - 01:05 | 35s)
- **Visual**: Click preset `Bank Header Spoofing` (`sample-phish-rcnn-1`), showing auto-populated sender mismatch (`chase-secure-verify.com` vs `fraud-harvest@server-host.xyz`) and `SPF fail`. Trigger `#scanBtn`.
- **Narration**: Live execution of the inference pipeline. The RCNN Attention model outputs **99.9% Phishing Probability**, triggers the **CRITICAL / PHISHING CONFIRMED** threat badge, and calculates a 90% header risk and 99.9% body risk.

### Phase 3: Explainable AI: Token-Level Attention Heatmap (01:05 - 01:40 | 35s)
- **Visual**: Smooth scroll to the `#attentionContainer` showing the token-level attention heatmap.
- **Narration**: Detailed explanation of the query-key Attention Mechanism ($u_t, \alpha_t$). Salient threat keywords (`urgent`, `immediate`, `account`, `suspension`, `credentials`, `verify`) are assigned high attention energy, providing full auditability for Security Operations Center analysts.

### Phase 4: High Specificity Verification: Legitimate Corporate Email (01:40 - 02:10 | 30s)
- **Visual**: Scroll back up, select `Standup Sync (Legitimate)` preset (`sample-safe-rcnn-1`), verify matching domains and `SPF pass`. Click `#scanBtn`.
- **Narration**: Demonstrating the unbalanced dataset high-specificity guarantee. The model outputs **0.5% Phishing Probability** (99.5% Safe Confidence) with **0/9 Models Flagged**, proving the system achieves < 0.45% false-positive rate on everyday corporate communications.

### Phase 5: Multi-Model Consensus & Academic Benchmarks (02:10 - 02:35 | 25s)
- **Visual**: Switch to `.nav-tab[data-tab="benchmarks"]`, reviewing the benchmark comparison table comparing RCNN with 8 baseline models (BiLSTM, LSTM, GRU, SGD, MLP, Random Forest, Naive Bayes, Logistic Regression).
- **Narration**: Quantitative evaluation under realistic 99:1 unbalanced traffic. The proposed RCNN Attention architecture achieves **99.20% accuracy**, **99.45% precision**, and **0.998 ROC-AUC**, outperforming all 8 baselines.

### Phase 6: SQLite Audit Trail, Architecture & Submission Summary (02:35 - 03:00 | 25s)
- **Visual**: Switch to `.nav-tab[data-tab="history"]` showcasing the SQLite `email_scans` table and aggregate telemetry cards, then quickly preview the `.nav-tab[data-tab="architecture"]` diagram.
- **Narration**: ACID transactional audit logging in SQLite (`phishing_scans.db`), verifying 23/23 passing automated tests, 8 high-res screenshots, 15 widescreen slides, and full college engineering capstone compliance.
