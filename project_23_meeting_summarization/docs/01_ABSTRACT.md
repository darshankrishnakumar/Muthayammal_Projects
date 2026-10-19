# 01. Executive Abstract

## Project Overview
**PROJECT-023: AI Meeting Summarization & Action-Item Extraction Using Natural Language Processing (NLP)**  
**System Designation:** SYNAPSE-MEET  
**Assigned Dedicated Port:** Port 5023 (`http://127.0.0.1:5023`)  
**College Capstone Submission:** College Final Year Engineering Project (Conversational AI & Enterprise NLP)

---

## Executive Summary
In modern hyper-scale enterprise organizations, synchronous meetings represent both the primary vehicle for high-level decision-making and one of the largest sources of operational friction. Modern professionals routinely spend between 18 and 26 hours per week attending virtual conferences, design reviews, and agile stand-ups. Despite this immense expenditure of human capital, critical institutional knowledge is systematically lost due to inadequate note-taking, dropped action items, and undocumented verbal consensus.

This engineering capstone report introduces **SYNAPSE-MEET**, an autonomous, high-throughput meeting intelligence platform engineered for enterprise production deployment on Port 5023. The platform addresses meeting information decay through a tightly integrated dual-engine architecture: a graph-based TextRank extractive summarization pipeline coupled with a calibrated multi-class dialogue act classification engine operating across a 917-feature sublinear TF-IDF vector space.

The system processes multi-speaker conversational transcripts, extracts speaker turns, and establishes pairwise sentence cosine similarities to compute power-iteration PageRank centrality. Concurrently, the dialogue act classifier categorizes individual conversational utterances across four standardized discourse acts:
1. **ACTION_ITEM**: Explicit commitments with priority estimation (Critical, High, Medium, Low), task ownership, and deadlines.
2. **DECISION**: Consensus agreements and architectural sign-offs.
3. **DISCUSSION**: Technical debates and metrics review feeding TextRank centrality.
4. **GENERAL_STATEMENT**: Protocol checks and conversational chitchat.

The production deployment features a zero-GPU multithreaded Python backend, an ACID-compliant transactional SQLite 3 database (`meetings.db`), and a glassmorphic command center utilizing Chart.js for speaker talk-time distribution and multi-axis quality radar profiling. Verified through 30 automated QA test cases achieving a 100.0% pass rate, the platform fulfills all technical and academic requirements for final-year engineering capstone defense.
