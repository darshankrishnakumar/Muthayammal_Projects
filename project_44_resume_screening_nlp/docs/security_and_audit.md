# Security & Cryptographic Audit: SHA-256 Chained Ledger

## Immutable Chain-of-Custody Architecture
To prevent post-hoc score modification, recruiter tampering, and algorithmic bias, all candidate screening evaluations are committed to a cryptographically linked blockchain-style audit ledger (`audit_ledger`).

```
[Genesis Block #0]
  Hash: SHA-256("SYSTEM_INIT" | Details | Timestamp | 0000...0000)
       |
       v
[Block #1: Requisitions Initialized]
  Prev: Genesis Hash
  Hash: SHA-256("OPENINGS_INITIALIZED" | Details | Timestamp | PrevHash)
       |
       v
[Block #N: Candidate Evaluation]
  Prev: Block #(N-1) Hash
  Hash: SHA-256("CANDIDATE_MATCH_EVALUATED" | MatchDetails | Timestamp | PrevHash)
```

## Anti-Bias Mitigation: Demographic Token Anonymization
When `anonymize_bias` is enabled:
1. Candidate legal names and demographic proxies are stripped.
2. A cryptographic pseudonym (`Candidate #ANON-XXXX`) is assigned.
3. Neural scoring operates strictly over validated skill tokens, verified experience duration, and educational credentials.
