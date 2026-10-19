# Regulatory Compliance & Civil Aviation Standards (FAA / EASA)

## 1. Regulatory Context
AERO-RUL is designed in strict conformance with the following civil aviation regulations:
- **FAA Title 14 CFR Part 121**: Air Carrier Certification and Continuing Airworthiness.
- **FAA Advisory Circular AC 120-16G**: Continuous Airworthiness Maintenance Programs (CAMP).
- **EASA Part-M (Regulation EU 1321/2014)**: Continuing Airworthiness Management Organisation (CAMO).

## 2. Three-Tier Airworthiness Alignment
The classification boundaries are mathematically mapped to certified maintenance action windows:
1. `AIRWORTHY / OPTIMAL` (Health >= 60%): Meets standard flight envelope without dispatch limitations.
2. `MAINTENANCE DUE SOON` (30% <= Health < 60%): Mandates accelerated inspection intervals under FAA FAR 121.367.
3. `GROUNDED / MANDATORY SHOP VISIT` (Health < 30%): Enforces mandatory engine removal under FAA Airworthiness Directives (AD).

## 3. Immutable Audit Trail
The system maintains non-repudiable audit logging in SQLite table `audit_log` with ISO-8601 UTC timestamps, recording every inference prediction, operational parameter change, and maintenance shop order dispatch.
