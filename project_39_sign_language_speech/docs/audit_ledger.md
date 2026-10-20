# Cryptographic Audit Ledger & Chain of Custody

## Mathematical Specification
Every translation and lifecycle event $k$ generates a block with current hash $H_k$:
$$H_k = \text{SHA-256}(\text{Action}_k \mathbin{\Vert} \text{Details}_k \mathbin{\Vert} \text{Timestamp}_k \mathbin{\Vert} H_{k-1})$$

The genesis block is deterministically seeded:
$$H_0 = \text{SHA-256}(\text{"SYSTEM_INIT"} \mathbin{\Vert} 0^{64})$$

## Digital Evidence Hash
Every translation entry generates an intrinsic digital evidence hash:
$$\text{Ev\_Hash} = \text{SHA-256}(\text{Gloss} \mathbin{\Vert} \text{Sentence} \mathbin{\Vert} \text{Conf} \mathbin{\Vert} F_0 \mathbin{\Vert} T_{dur})$$
