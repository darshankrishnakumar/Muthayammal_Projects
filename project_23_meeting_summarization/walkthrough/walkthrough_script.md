# Demonstration & Walkthrough Script: AI-Based Meeting Summarization and Action-Item Extraction (PROJECT-023)

## Overview
- **Project Identifier**: PROJECT-023
- **Module**: `project_23_meeting_summarization`
- **Application Port**: Port 5023 (`http://127.0.0.1:5023/`)
- **Primary Technology Stack**: Python 3.12, Flask REST API, Scikit-Learn (TF-IDF + Calibrated Dialogue Act Classifiers), TextRank Sentence Centrality, Relational SQLite 3, Vanilla Glassmorphic HTML5/CSS3/JS, Chart.js 4.4.
- **Verification Standard**: 30 Automated Tests Passing (100%), Exact 180.0s H.264 MP4 Video Walkthrough.

---

## Chronological Walkthrough Sequence (Total Duration: 03:00 / 180.0 Seconds)

### 1. 00:00 - 00:30 | Overview & Telematics Metric Strip
- Launch and inspect the SYNAPSE-MEET Glassmorphic Cockpit on Port 5023.
- Observe real-time operational KPI stat cards:
  - Total Meetings Indexed
  - Total Action Items Extracted
  - Decisions Logged
  - Average Engagement Percentage
- Review the HTML5 Canvas animated audio wave visualizer.
- Scroll down to review the Speaker Donut Chart and 5-Axis Meeting Quality Radar Profile.

### 2. 00:30 - 01:00 | Cloud Architecture Review Summarization
- Inject `cloud` preset scenario:
  > *"Q3 Cloud Architecture & Security Review"* (Kafka migration, Canary deployment, EU failover).
- Click `btnSummarize` to trigger the real NLP pipeline.
- Observe real-time TextRank executive abstractive summary, key bullet points, and extracted action items:
  - Task: *Deploy canary release v2.4 to staging cluster by Friday* -> Elena (DevOps SRE) | High
  - Task: *Sync with Finance on cloud infrastructure budget allocation* -> David (Engineering Mgr) | Medium
  - Task: *Train fine-tuned embedding model on internal documentation* -> Priya (Data Lead) | High
- Observe extracted strategic decision: *Approved Kafka as standard messaging backbone*.

### 3. 01:00 - 01:30 | Sprint Planning & Blocker Triage Summarization
- Inject `sprint` preset scenario:
  > *"Sprint Planning & Blocker Sync"* (PostgreSQL query timeout, Let's Encrypt bot, API deprecation).
- Run summarization.
- Observe updated task register:
  - *Optimize PostgreSQL index scan on payments ledger table* -> Marcus (Chief Architect) | Critical Priority | Tomorrow 10 AM
- Observe decision register: *Automate zero-downtime certificate renewals via Let's Encrypt*.

### 4. 01:30 - 02:00 | Product Launch Retrospective & Diagnostics
- Inject `launch` preset scenario:
  > *"Global Product Launch Retrospective"* (12k signups, 99.98% uptime, gRPC migration).
- Observe updated Speaker Donut Chart visualizing conversational share across Sarah, David, Marcus, and Elena.
- Inspect the 5-Axis Radar Chart showing Engagement (91%), Clarity (88%), Task Density (80%), Consensus (92%), and Compression (75%).

### 5. 02:00 - 02:30 | Custom Incident Postmortem Ingestion
- Input freeform production postmortem dialogue:
  > *"P1 Redis Cluster Failover Postmortem"*
  > Sarah: Review Redis failover.
  > Marcus: Implement circuit breaker thresholds in gateway by Thursday.
  > Elena: Scale cluster nodes from 3 to 6 replicas.
- Trigger real-time summarization and observe instant entity extraction and priority assignment.

### 6. 02:30 - 03:00 | Processed Archives, Checkboxes & Minutes Export
- Toggle action item checkboxes directly on the interface.
- Scroll down to the Processed Meeting Archives list.
- Demonstrate historical session inspection and Markdown minutes generation via `GET /api/export/minutes/<id>`.
- Verification of transactional persistence in `meetings.db` and conclusion.
