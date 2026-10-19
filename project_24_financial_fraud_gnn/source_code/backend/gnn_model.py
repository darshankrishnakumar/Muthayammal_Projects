import os
import json
import math
import numpy as np
import torch
import torch.nn as nn

COUNTRY_RISK_MAP = {
    'US': 0.05, 'CA': 0.04, 'UK': 0.06, 'DE': 0.05, 'FR': 0.05,
    'JP': 0.04, 'AU': 0.05, 'CH': 0.22, 'SG': 0.15, 'AE': 0.45,
    'VG': 0.92, 'PA': 0.88, 'CY': 0.82, 'KY': 0.94, 'SC': 0.86,
    'BZ': 0.89, 'MH': 0.91, 'BS': 0.85
}

class GraphConvolutionLayer(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super(GraphConvolutionLayer, self).__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)

    def forward(self, x, adj):
        support = torch.mm(x, self.weight)
        output = torch.mm(adj, support)
        if self.bias is not None:
            output = output + self.bias
        return output

class FinancialGCN(nn.Module):
    def __init__(self, nfeat=8, nhid=16, nclass=2, dropout=0.0):
        super(FinancialGCN, self).__init__()
        self.gc1 = GraphConvolutionLayer(nfeat, nhid)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.gc2 = GraphConvolutionLayer(nhid, nclass)

    def forward(self, x, adj):
        h1 = self.relu(self.gc1(x, adj))
        logits = self.gc2(h1, adj)
        return logits, h1

class GNNFraudEngine:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        self.weights_path = os.path.join(model_dir, "gnn_weights.pt")
        self.metadata_path = os.path.join(model_dir, "gnn_model_metadata.json")
        self.model = None
        self.metadata = None
        self.feat_mean = None
        self.feat_std = None
        self.load_model()

    def load_model(self):
        if os.path.isfile(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.feat_mean = np.array(self.metadata["feature_mean"], dtype=np.float32)
            self.feat_std = np.array(self.metadata["feature_std"], dtype=np.float32)
        else:
            self.feat_mean = np.zeros(8, dtype=np.float32)
            self.feat_std = np.ones(8, dtype=np.float32)

        self.model = FinancialGCN(nfeat=8, nhid=16, nclass=2, dropout=0.0)
        if os.path.isfile(self.weights_path):
            state_dict = torch.load(self.weights_path, map_location=torch.device('cpu'))
            self.model.load_state_dict(state_dict)
        self.model.eval()

    def extract_graph_features(self, nodes, edges):
        """Build feature matrix X and symmetric normalized adjacency matrix A_hat."""
        N = len(nodes)
        node_id_to_idx = {n["id"]: idx for idx, n in enumerate(nodes)}

        in_degrees = np.zeros(N, dtype=np.float32)
        out_degrees = np.zeros(N, dtype=np.float32)
        inflows = np.zeros(N, dtype=np.float32)
        outflows = np.zeros(N, dtype=np.float32)
        adj_matrix = np.zeros((N, N), dtype=np.float32)

        for edge in edges:
            s_idx = node_id_to_idx.get(edge["source"])
            t_idx = node_id_to_idx.get(edge["target"])
            amt = float(edge.get("amount", 0.0))
            if s_idx is not None and t_idx is not None:
                adj_matrix[s_idx, t_idx] = 1.0
                out_degrees[s_idx] += 1.0
                in_degrees[t_idx] += 1.0
                outflows[s_idx] += amt
                inflows[t_idx] += amt

        X = np.zeros((N, 8), dtype=np.float32)
        for idx, n in enumerate(nodes):
            bal = max(0.0, float(n.get("balance", 0.0)))
            c_risk = COUNTRY_RISK_MAP.get(n.get("country", "US"), 0.1)
            tot_deg = in_degrees[idx] + out_degrees[idx]
            tot_vol = inflows[idx] + outflows[idx]

            X[idx, 0] = math.log10(bal + 1.0)
            X[idx, 1] = float(in_degrees[idx])
            X[idx, 2] = float(out_degrees[idx])
            X[idx, 3] = math.log10(inflows[idx] + 1.0)
            X[idx, 4] = math.log10(outflows[idx] + 1.0)
            X[idx, 5] = float(c_risk)
            X[idx, 6] = float(out_degrees[idx] / max(1.0, tot_deg))
            X[idx, 7] = float((inflows[idx] - outflows[idx]) / max(1.0, tot_vol))

        # Normalize features with learned scalers
        if self.feat_mean is not None and self.feat_std is not None:
            X_norm = (X - self.feat_mean) / self.feat_std
        else:
            X_norm = X

        # Symmetrize adjacency for undirected GCN message passing
        A_sym = np.maximum(adj_matrix, adj_matrix.T)
        # Symmetric normalized adjacency: D^(-1/2) * (A + I) * D^(-1/2)
        A_tilde = A_sym + np.eye(N, dtype=np.float32)
        d_tilde = np.sum(A_tilde, axis=1)
        d_inv_sqrt = np.power(d_tilde, -0.5)
        d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0
        D_mat = np.diag(d_inv_sqrt)
        A_hat = D_mat @ A_tilde @ D_mat

        return X_norm, A_hat, in_degrees, out_degrees, inflows, outflows

    def predict_graph(self, nodes, edges, frozen_accounts=None):
        """Run 2-layer GCN forward pass over the entire graph."""
        if not nodes:
            return []

        if frozen_accounts is None:
            frozen_accounts = set()

        X_norm, A_hat, in_degrees, out_degrees, inflows, outflows = self.extract_graph_features(nodes, edges)

        with torch.no_grad():
            x_t = torch.FloatTensor(X_norm)
            adj_t = torch.FloatTensor(A_hat)
            logits, embeddings = self.model(x_t, adj_t)
            probs = torch.softmax(logits, dim=1)[:, 1].numpy()
            emb_np = embeddings.numpy()

        results = []
        for i, n in enumerate(nodes):
            nid = n["id"]
            is_frozen = nid in frozen_accounts
            raw_risk = float(probs[i])
            if is_frozen:
                risk = 0.999
                status = "FROZEN"
            else:
                risk = round(raw_risk, 4)
                status = n.get("status", "ACTIVE")

            tier = "CRITICAL" if risk >= 0.80 else "HIGH" if risk >= 0.60 else "MEDIUM" if risk >= 0.35 else "CLEAN"

            results.append({
                "id": nid,
                "name": n.get("name", nid),
                "type": n.get("type", "Personal"),
                "balance": float(n.get("balance", 0.0)),
                "country": n.get("country", "US"),
                "risk": risk,
                "risk_tier": tier,
                "status": status,
                "is_frozen": is_frozen,
                "in_degree": int(in_degrees[i]),
                "out_degree": int(out_degrees[i]),
                "total_inflow": round(float(inflows[i]), 2),
                "total_outflow": round(float(outflows[i]), 2),
                "cluster": n.get("cluster", "COMMUNITY_NORMAL"),
                "gnn_embedding": [round(float(v), 4) for v in emb_np[i][:8]]
            })

        return results

    def explain_node(self, node_info, inbound_edges, outbound_edges):
        """Provide detailed forensic explanation based on GCN topology."""
        risk = node_info.get("risk", 0.0)
        in_deg = len(inbound_edges)
        out_deg = len(outbound_edges)
        c_risk = COUNTRY_RISK_MAP.get(node_info.get("country", "US"), 0.05)
        
        signatures = []
        if out_deg >= 4 and in_deg <= 1:
            signatures.append("High-Fanout Smurfing Dispersal Signature (Dispersing funds to multiple mules)")
        if in_deg >= 4 and out_deg <= 1:
            signatures.append("Funnel Aggregation Signature (Consolidating capital from distributed sleeper feeders)")
        if in_deg >= 1 and out_deg >= 1 and abs(in_deg - out_deg) <= 1 and c_risk > 0.5:
            signatures.append("Circular Carousel Layering Node (Matched multi-hop transit in high-risk offshore jurisdiction)")
        if c_risk > 0.7:
            signatures.append(f"High-Risk Jurisdictional Nexus ({node_info.get('country')}) with strict secrecy laws")

        if not signatures:
            if risk > 0.7:
                signatures.append("High neighborhood risk diffusion via 2-hop GCN message passing")
            else:
                signatures.append("Standard bilateral commercial/retail transaction pattern")

        return {
            "classification_verdict": "FLAGGED MONEY MULE" if risk >= 0.75 else "ELEVATED SUSPICION" if risk >= 0.40 else "CLEAN RETAIL",
            "layer1_aggregate": f"Aggregated 1-hop embeddings across {in_deg + out_deg} adjacent counterparties",
            "layer2_neighborhood_pool": f"Symmetric normalized GCN propagation over 2-hop topological ego network",
            "detected_signatures": signatures
        }

# Global Singleton Engine Instance
gnn_engine = GNNFraudEngine()
