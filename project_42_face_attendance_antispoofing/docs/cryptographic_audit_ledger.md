# Cryptographic Audit Ledger & Chain of Custody

## 1. Merkle-Style Block Chaining Architecture
The institutional audit ledger provides mathematical immutability for all attendance and security operations.

```
+--------------------+       +--------------------+       +--------------------+
|     BLOCK #0       |       |     BLOCK #1       |       |     BLOCK #2       |
| (Genesis Seeding)  |       | (Roster Enrolled)  |       | (Live Access Grant)|
| Prev: 00000000...  | ----> | Prev: 4f82bc...    | ----> | Prev: e391a0...    |
| Hash: 4f82bc...    |       | Hash: e391a0...    |       | Hash: 78ab12...    |
+--------------------+       +--------------------+       +--------------------+
```

## 2. Hash Calculation Formula
For any block $B_k$:
$$	ext{Payload}_k = 	ext{ActionType} \parallel 	ext{Details} \parallel 	ext{Timestamp} \parallel 	ext{Hash}_{k-1}$$
$$	ext{Hash}_k = 	ext{SHA-256}(	ext{Payload}_k)$$

## 3. Tamper Detection Properties
- **Bit-Level Sensitivity**: A single altered character in a student's ID or score changes the resulting SHA-256 hash completely (Avalanche Effect).
- **Chain Breakage**: Because $B_{k+1}$ stores $	ext{Hash}_k$ as its previous hash, any modification to $B_k$ causes an immediate mismatch at block $k+1$.
- **Automated Verification**: Integrated test suites (`test_04_audit_ledger_hash_continuity` and `test_05_audit_tamper_detection`) mathematically prove ledger integrity on every CI/CD run.
