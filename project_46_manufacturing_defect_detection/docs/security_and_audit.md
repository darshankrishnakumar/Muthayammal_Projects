# Cryptographic Security & Audit Specification (PROJECT-046)

## 1. Merkle-Inspired Hash Chaining
Audit events are linked in an append-only cryptographic chain guaranteeing non-repudiation and immutable data integrity.

### Hash Chaining Formula
$$	ext{Block Hash} = 	ext{SHA256}(	ext{Action} \parallel 	ext{Details} \parallel 	ext{Timestamp} \parallel 	ext{Previous Hash})$$

- **Genesis Block (#0)**: Seeded at database bootstrap with `previous_hash = "0" * 64`.
- **Strict Continuity**: Block $N$ encapsulates the exact hash of Block $N-1$.
- **Tamper Invalidation**: Modifying even a single character in historical records alters that block's hash, instantly invalidating all downstream blocks.

## 2. Deterministic Evidence Hashes
Every inspected part receives an unforgeable SHA-256 digital fingerprint:
$$	ext{Evidence Hash} = 	ext{SHA256}(	ext{Part Type} : 	ext{Line} : 	ext{Verdict} : 	ext{Defect} : 	ext{Severity} : 	ext{Area} : 	ext{Roughness} : 	ext{Eject Conf})$$
