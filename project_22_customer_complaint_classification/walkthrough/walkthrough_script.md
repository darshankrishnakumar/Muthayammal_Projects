# Demonstration & Walkthrough Script: AI-Based Customer Complaint Classification and Priority Prediction Using NLP (PROJECT-022)

## Overview
- **Project Identifier**: PROJECT-022
- **Module**: `project_22_customer_complaint_classification`
- **Application Port**: Port 5022 (`http://127.0.0.1:5022/`)
- **Primary Technology Stack**: Python 3.12, Flask REST API, Scikit-Learn (TF-IDF + Calibrated Logistic Classifiers), Relational SQLite 3, Vanilla Glassmorphic HTML5/CSS3/JS, Chart.js 4.4.
- **Verification Standard**: 33 Automated Tests Passing (100%), Exact 180.0s H.264 MP4 Video Walkthrough.

---

## Chronological Walkthrough Sequence (Total Duration: 03:00 / 180.0 Seconds)

### 1. 00:00 - 00:30 | Overview & Telematics KPI Cockpit
- Launch and inspect the TRIAGE-AI Glassmorphic Command Center on Port 5022.
- Verify real-time operational KPI stat cards:
  - Total Tickets Ingested
  - Critical Priority Count
  - Average System Urgency (scaled /100)
  - Mean Model Confidence Percentage
- Scroll down to review the live Category Donut Chart and Priority Horizontal Bar Chart.

### 2. 00:30 - 01:00 | Critical Billing Dispute Classification & SLA Routing
- Select the `billing` scenario preset:
  > *"My corporate credit card ending in #4092 was charged $1,490 twice for order #88492. I need an immediate reversal and refund! This is an unauthorized charge."*
- Trigger the real NLP classification engine.
- Observe immediate triage response:
  - **Category**: 💳 Payment & Billing Dispute
  - **Assigned Department**: FinOps Billing & Fraud Team
  - **Priority Tier**: CRITICAL
  - **SLA Resolution Target**: 0.5 hours (30 minutes)
  - **Urgency Score**: 94/100 | Negative Sentiment Index: -0.85
  - **Explainability Hashtags**: `#charge`, `#refund`, `#billing`, `#unauthorized`
- Review the calibrated posterior probability distribution chart showing 98%+ confidence on `payment_issue`.

### 3. 01:00 - 01:30 | Hardware Defect & Warranty RMA Routing
- Select the `rma` scenario preset:
  > *"The industrial laser printer motor spindle cracked after 2 days of operation and burnt plastic smell is coming out. We need a replacement unit under warranty RMA."*
- Execute NLP inference.
- Observe real-time ticket categorization:
  - **Category**: 📦 Product Defect & Hardware RMA
  - **Routing Target**: Quality Engineering & RMA Desk
  - **Priority**: HIGH
  - **SLA Resolution Target**: 2.0 hours
- Observe the dynamic re-rendering of probability bars across the 6 departments.

### 4. 01:30 - 02:00 | Software Bug & Platform DevOps Outage
- Select the `api` scenario preset:
  > *"Our production webhook /v2/telemetry is throwing HTTP 500 internal server errors every 3 minutes. Latency is above 4000ms affecting 40k active IoT nodes."*
- Trigger classification.
- Observe triage output:
  - **Category**: 💻 Software Bug & Platform Outage
  - **Routing Target**: Tier-3 Engineering & DevOps
  - **Priority**: CRITICAL
  - **Urgency Score**: 98/100
  - **SLA Target**: 0.5 hours

### 5. 02:00 - 02:30 | IAM Security Lockout & Custom Freeform Ingestion
- Inject `auth` preset to demonstrate Identity & Access Management routing.
- Clear the input area and submit custom unconstrained text:
  > *"Air shipment container #ORB-99120 has been delayed in customs for 11 days. Assembly line blocked."*
- Observe real-time classification to 🚚 Global Supply Chain & Logistics with HIGH priority.

### 6. 02:30 - 03:00 | Ticket Management Table, Search Filters & CSV Export
- Scroll down to the interactive Ticket Management stream table.
- Demonstrate multi-criteria client-side filtering:
  - Filter by priority: `critical`
  - Filter by category: `payment_issue`
- Reset filters to inspect full ticket ledger.
- Trigger single-click CSV export generating a downloadable audit dossier.
- Verification of transactional persistence in `complaints.db` and conclusion.
