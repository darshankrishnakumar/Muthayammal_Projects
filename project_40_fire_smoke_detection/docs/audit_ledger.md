# Cryptographic Audit Ledger & Chain of Custody

## Mathematical Specification
Every industrial alarm, suppression dispatch, and operator acknowledgment generates an immutable ledger block with current hash $H_k$:
$$H_k = \text{SHA-256}(\text{Action}_k \mathbin{\Vert} \text{Details}_k \mathbin{\Vert} \text{Timestamp}_k \mathbin{\Vert} H_{k-1})$$

The genesis block is deterministically seeded at system initialization:
$$H_0 = \text{SHA-256}(\text{"SYSTEM_INIT"} \mathbin{\Vert} 0^{64})$$

## Digital Evidence Hash
Every incident record generates an intrinsic evidentiary verification hash:
$$\text{Ev\_Hash} = \text{SHA-256}(\text{Hazard} \mathbin{\Vert} \text{Tier} \mathbin{\Vert} \text{Conf} \mathbin{\Vert} T_{flame} \mathbin{\Vert} U_{urgency})$$
