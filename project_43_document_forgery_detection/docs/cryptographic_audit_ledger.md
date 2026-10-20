# Cryptographic Audit Ledger & Chain of Custody

## 1. Merkle-Style Block Chaining Architecture
The institutional audit ledger provides mathematical immutability for all document examination events.

```
+--------------------+       +--------------------+       +--------------------+
|     BLOCK #0       |       |     BLOCK #1       |       |     BLOCK #2       |
| (Genesis Seeding)  |       | (Templates Init)   |       | (Forgery Intercept)|
| Prev: 00000000...  | ----> | Prev: 4f82bc...    | ----> | Prev: e391a0...    |
| Hash: 4f82bc...    |       | Hash: e391a0...    |       | Hash: 78ab12...    |
+--------------------+       +--------------------+       +--------------------+
```

## 2. Hash Calculation Formula
For any block $B_k$:
$$\text{Payload}_k = \text{ActionType} \parallel \text{Details} \parallel \text{Timestamp} \parallel \text{Hash}_{k-1}$$
$$\text{Hash}_k = \text{SHA-256}(\text{Payload}_k)$$

## 3. Tamper Detection Properties
- **Bit-Level Sensitivity**: A single altered character in a document title or verdict changes the SHA-256 hash completely.
- **Chain Breakage**: Because $B_{k+1}$ stores $\text{Hash}_k$ as its previous hash, any modification to $B_k$ causes an immediate mismatch at block $k+1$.
- **Automated Verification**: Integrated test suites (`test_04_audit_ledger_hash_continuity` and `test_05_audit_tamper_detection`) mathematically prove ledger integrity on every CI/CD run.
