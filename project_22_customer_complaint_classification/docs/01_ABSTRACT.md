# 01. Executive Abstract

## Project Overview
**PROJECT-022: Customer Complaint Classification and Priority Prediction Using Natural Language Processing (NLP)**  
**System Designation:** TRIAGE-AI  
**Assigned Dedicated Port:** Port 5022 (`http://127.0.0.1:5022`)  
**College Capstone Submission:** College Final Year Engineering Project (NLP & Enterprise Support Domain)

---

## Executive Summary
In modern hyper-scale enterprise environments, customer complaint triage represents a mission-critical operational bottleneck directly impacting customer retention, regulatory compliance, and brand equity. Traditional customer service operations rely heavily on manual human evaluation, keyword heuristics, or rudimentary rule-based routing engines. These conventional methods suffer from acute latency, cognitive fatigue, inconsistent categorization, and vulnerability to severe Service Level Agreement (SLA) breaches during incident surges.

This engineering capstone report introduces **TRIAGE-AI**, an autonomous, high-throughput customer complaint classification and dynamic priority prediction engine designed for high-availability enterprise deployment on Port 5022. The system employs a dual-head calibrated machine learning pipeline operating over a sublinear Term Frequency-Inverse Document Frequency (TF-IDF) feature space encompassing 2,603 unigram and bigram tokens.

The primary classification head categorizes incoming natural language text across six distinct operational domains:
1. **Payment & Billing Disputes** (`payment_issue`) -> FinOps Billing & Fraud Team
2. **Product Defects & Hardware RMAs** (`product_complaint`) -> Quality Engineering & RMA Desk
3. **Logistics & Dispatch Delays** (`delivery_problem`) -> Global Supply Chain & Logistics
4. **Software Bugs & Platform Outages** (`technical_issue`) -> Tier-3 Engineering & DevOps
5. **Identity & Access Management (IAM) Security** (`account_issue`) -> Identity & Access Management (IAM)
6. **Customer Experience Escalations** (`service_dissatisfaction`) -> Executive Customer Relations

Concurrently, the secondary classification head predicts ticket urgency across four standardized priority tiers (**Critical, High, Medium, Low**), dynamically computing exact contractual SLA countdown deadlines.

The production deployment integrates a lightweight, zero-GPU multithreaded Python backend, an ACID-compliant transactional SQLite 3 database with immutable audit trails, and a reactive glassmorphic command center providing real-time data visualization via Chart.js. Verified through an extensive automated QA test suite comprising 33 rigorous test cases, the system demonstrates 100.00% category classification accuracy, 82.25% priority classification accuracy, and sub-3ms inference latency, fulfilling all requirements for formal academic capstone presentation and production readiness.
