# 02. System Requirements & Domain Scope

## Functional Requirements
1. **Attributed Graph Ingestion & Modeling:**
   - Ingests accounts across diverse entity types (Personal, Corporate, Merchant, Shell LLC, Money Mule Proxy, Crypto Mixing Pool).
   - Ingests directed transactions with financial attributes (amount, transfer channel, note, timestamp).
   - Dynamically tracks in-degree, out-degree, total cash inflow, and total cash outflow.

2. **Graph Machine Learning Inference:**
   - Real-time extraction of 8-dimensional topological node feature vectors $X \in \mathbb{R}^{N \times 8}$.
   - Construction of symmetrized augmented adjacency $\tilde{A} = A_{sym} + I_N$ and symmetric normalized Laplacian $\hat{A} = \tilde{D}^{-1/2} \tilde{A} \tilde{D}^{-1/2}$.
   - 2-layer GCN forward pass outputting 16-dimensional continuous embeddings $H^{(1)}$ and calibrated softmax probabilities $P(\text{Fraud})$.

3. **Syndicate Pattern Extraction & Ring Traversal:**
   - Automated detection of closed circular carousels ($A \to B \to C \to D \to A$).
   - Extraction of structured smurfing fan-out trees (single mixing pool dispersing sub-$10,000 tranches).
   - Identification of aggregation funnels (multiple domestic feeder accounts funneling to offshore entities).

4. **Forensic Inspection & Explainability:**
   - Detailed dossier inspection per account displaying counterparty ledgers, country risk tier, and structural GNN explanations.

5. **Operational Interdiction & FinCEN Regulatory Compliance:**
   - Proactive freeze and unfreeze controls updating database state and diffusing counterparty risk.
   - Export of FinCEN Suspicious Activity Report (SAR) regulatory JSON dossiers with complete audit logs.

6. **Dynamic Graph Stress Testing:**
   - Zero-downtime dynamic injection of synthetic multi-hop laundering rings directly into the running graph.

## Non-Functional Requirements
- **Inference Latency:** $< 15$ ms end-to-end for 520 nodes and 1,650 edges on CPU.
- **Reliability:** 100% automated test pass rate with zero flaky assertions.
- **Port Allocation:** Exclusively bound to assigned Port 5024.\n