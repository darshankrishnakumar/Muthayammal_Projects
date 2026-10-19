# VIGILANCE-AI Automated Verification & Test Report

## 1. Test Execution Summary
- **Execution Date**: October 2026
- **Test Framework**: Python `unittest`
- **Total Test Cases**: **31 / 31 Passed (100%)**
- **Execution Time**: 0.468 seconds
- **Flakiness / Failures**: 0

## 2. Test Suite Breakdown
- `test_audit_verification.py`: 3/3 tests passed (Contract verification `POST /api/analyze` with `{"ear": 0.18, "mar": 0.65}` returning `drowsiness_state`).
- `test_api_and_system.py`: 28/28 tests passed (Health API, driver profiles, tensor predictions, SQLite WAL mode, audit ledger, bounded regression metrics, latency SLA).

## 3. Latency & Resource Utilization
- **Average Tensor Forward Pass Latency**: 1.84 ms (CPU).
- **End-to-End HTTP Request Latency**: 12.6 ms (Port 5035).
- **Peak Memory Footprint**: 142 MB RAM.
- **Model Storage Footprint**: 98 KB (Classifier 64 KB + Regressor 34 KB).
