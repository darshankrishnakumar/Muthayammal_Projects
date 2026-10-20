# Cryptographic Security & Audit Specification (PROJECT-047)

## 1. Blockchain-Inspired Hash Chaining
Audit events are linked in an append-only cryptographic chain guaranteeing non-repudiation and immutable data integrity.

### Hash Chaining Formula
$$\text{Block Hash} = \text{SHA256}(\text{Action} \parallel \text{Details} \parallel \text{Timestamp} \parallel \text{Previous Hash})$$

- **Genesis Block (#0)**: Seeded at database bootstrap with `previous_hash = "0" * 64`.
- **Strict Continuity**: Block $N$ encapsulates the exact hash of Block $N-1$.
- **Tamper Invalidation**: Modifying even a single character in historical records alters that block's hash, instantly invalidating all downstream blocks.

## 2. Deterministic Evidence Hashes
Every snapshot receives an unforgeable SHA-256 digital fingerprint:
$$\text{Evidence Hash} = \text{SHA256}(\text{Course} : \text{Students} : \text{Score} : \text{Attentive} : \text{Bored} : \text{Distracted} : \text{Drowsy} : \text{Action} : \text{PredAtt} : \text{PredDrowsy})$$
