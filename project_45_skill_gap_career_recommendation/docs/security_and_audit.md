# Security & Cryptographic Audit: SHA-256 Chained Ledger

## Immutable Chain-of-Custody Architecture
To prevent post-hoc score modification, training credential fraud, and recruiter tampering, all career diagnostic evaluations and upskilling roadmaps are committed to a cryptographically linked blockchain-style audit ledger (`audit_ledger`).

```
[Genesis Block #0]
  Hash: SHA-256("SYSTEM_INIT" | Details | Timestamp | 0000...0000)
       |
       v
[Block #1: Roles Initialized]
  Prev: Genesis Hash
  Hash: SHA-256("CAREER_ROLES_INITIALIZED" | Details | Timestamp | PrevHash)
       |
       v
[Block #N: Roadmap Generated]
  Prev: Block #(N-1) Hash
  Hash: SHA-256("CAREER_ROADMAP_GENERATED" | RoadmapDetails | Timestamp | PrevHash)
```

## Anti-Tamper Verification
Any modification to historical records alters the block hash and invalidates the entire downstream cryptographic chain. Programmatic verification endpoints `/api/career/audit-logs` allow compliance auditing.
