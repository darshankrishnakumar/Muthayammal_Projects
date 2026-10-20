# Cryptographic Audit Ledger & Chain of Custody

## Mathematical Specification
Every optical fruit grading inspection, lane configuration, and operator chute override generates an immutable block with hash $H_k$:
$$H_k = \text{SHA-256}(\text{Action}_k \mathbin{\Vert} \text{Details}_k \mathbin{\Vert} \text{Timestamp}_k \mathbin{\Vert} H_{k-1})$$

The genesis block is deterministically seeded at system boot:
$$H_0 = \text{SHA-256}(\text{"SYSTEM_INIT"} \mathbin{\Vert} 0^{64})$$

## Digital Evidence Hash
Every individual fruit item record carries a cryptographic evidence hash:
$$\text{Ev\_Hash} = \text{SHA-256}(\text{Variety} \mathbin{\Vert} \text{Grade} \mathbin{\Vert} \text{Defect} \mathbin{\Vert} F_{firm} \mathbin{\Vert} \text{Brix} \mathbin{\Vert} T_{shelf} \mathbin{\Vert} E_{index})$$
