# Cryptographic Audit Ledger & Chain of Custody

## Mathematical Specification
Every inspection event $k$ generates a block with current hash $H_k$:
$$H_k = \text{SHA-256}(\text{Action}_k \mathbin{\Vert} \text{Details}_k \mathbin{\Vert} \text{Timestamp}_k \mathbin{\Vert} H_{k-1})$$

The genesis block is deterministically seeded:
$$H_0 = \text{SHA-256}(\text{"GENESIS|SYSTEM_INIT|"} \mathbin{\Vert} \text{Timestamp} \mathbin{\Vert} 0^{64})$$

## Tamper Evident Verification
Modifying any historical record $j < k$ breaks the mathematical hash chain for all subsequent blocks $m \ge j$. The integrity check endpoint validates that $\forall i, H_i == \text{SHA-256}(\dots, H_{i-1})$.
