import os
import json
import math
import random
import csv
from datetime import datetime, timedelta, timezone
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Set fixed seeds for deterministic reproducibility
np.random.seed(42)
random.seed(42)
torch.manual_seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(DATA_DIR, "..", "backend"))
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DIR, exist_ok=True)

# ─── 1. SYNTHETIC FINANCIAL GRAPH GENERATION (520 NODES, 1,650 TRANSACTIONS) ───

COUNTRY_RISK_MAP = {
    'US': 0.05, 'CA': 0.04, 'UK': 0.06, 'DE': 0.05, 'FR': 0.05,
    'JP': 0.04, 'AU': 0.05, 'CH': 0.22, 'SG': 0.15, 'AE': 0.45,
    'VG': 0.92, 'PA': 0.88, 'CY': 0.82, 'KY': 0.94, 'SC': 0.86,
    'BZ': 0.89, 'MH': 0.91, 'BS': 0.85
}

def generate_graph_dataset():
    print("Generating comprehensive financial graph dataset...")
    nodes = []
    edges = []

    # A. Circular Laundering Carousel Rings (3 Rings, ~15 nodes)
    ring_specs = [
        {"ring_id": 1, "size": 4, "prefix": "RING-20", "country_pool": ["VG", "CY", "PA", "SC"], "base_amt": 185000.0},
        {"ring_id": 2, "size": 5, "prefix": "RING-40", "country_pool": ["KY", "BZ", "MH", "CH", "PA"], "base_amt": 340000.0},
        {"ring_id": 3, "size": 4, "prefix": "RING-60", "country_pool": ["BS", "VG", "CY", "AE"], "base_amt": 125000.0}
    ]
    for spec in ring_specs:
        ring_nodes = []
        for i in range(1, spec["size"] + 1):
            nid = f"{spec['prefix']}{i}"
            country = spec["country_pool"][(i - 1) % len(spec["country_pool"])]
            node = {
                "id": nid,
                "name": f"Syndicate Entity {nid} ({country})",
                "type": "Shell LLC" if i % 2 == 0 else "Money Mule Proxy",
                "balance": round(spec["base_amt"] * random.uniform(0.9, 1.2), 2),
                "country": country,
                "is_fraud": 1,
                "cluster": f"CIRCULAR_RING_{spec['ring_id']}",
                "status": "ACTIVE"
            }
            nodes.append(node)
            ring_nodes.append(node)

        # Connect circular edges (1 -> 2 -> ... -> N -> 1)
        for i in range(len(ring_nodes)):
            src = ring_nodes[i]["id"]
            dst = ring_nodes[(i + 1) % len(ring_nodes)]["id"]
            amt = round(spec["base_amt"] * random.uniform(0.96, 0.99), 2)
            edges.append({
                "id": f"TX-RING-{spec['ring_id']}-{i+1}",
                "source": src,
                "target": dst,
                "amount": amt,
                "note": f"Structured Tranche Layering {i+1}",
                "channel": "SWIFT WIRE",
                "is_suspicious": 1,
                "pattern": "CIRCULAR_LOOP",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))).isoformat()
            })

    # B. Smurfing Fan-Out Operations (3 Kingpins, each dispersing to 8-12 mules)
    for k in range(1, 4):
        kingpin_id = f"MULE-KING-0{k}"
        kingpin = {
            "id": kingpin_id,
            "name": f"Shadow Vault Nexus {k}",
            "type": "Crypto Mixing Pool",
            "balance": round(random.uniform(500000, 1200000), 2),
            "country": random.choice(["CH", "VG", "PA", "CY"]),
            "is_fraud": 1,
            "cluster": f"SMURFING_TREE_{k}",
            "status": "ACTIVE"
        }
        nodes.append(kingpin)

        mule_count = random.randint(8, 12)
        for m in range(1, mule_count + 1):
            mule_id = f"MULE-SMURF-{k}{m:02d}"
            mule = {
                "id": mule_id,
                "name": f"Placement Mule #{k}-{m}",
                "type": "Money Mule Proxy",
                "balance": round(random.uniform(9200, 11500), 2),
                "country": random.choice(["US", "UK", "CA", "DE"]),
                "is_fraud": 1,
                "cluster": f"SMURFING_TREE_{k}",
                "status": "ACTIVE"
            }
            nodes.append(mule)

            # Sub-threshold transaction just below $10,000 to evade CTR
            edges.append({
                "id": f"TX-SMURF-{k}-{m}",
                "source": kingpin_id,
                "target": mule_id,
                "amount": round(random.uniform(8900.0, 9850.0), 2),
                "note": "Sub-threshold Structured P2P Disbursement",
                "channel": "P2P CRYPTO OFFRAMP",
                "is_suspicious": 1,
                "pattern": "SMURFING_FANOUT",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(2, 72))).isoformat()
            })

    # C. Aggregation Funnels (2 Offshore Exit Hubs, fed by multiple domestic feeders)
    for f_idx in range(1, 3):
        exit_id = f"OFFSHORE-EXIT-0{f_idx}"
        exit_node = {
            "id": exit_id,
            "name": f"Haven Asset Holding #{f_idx}",
            "type": "Shell LLC",
            "balance": round(random.uniform(450000, 850000), 2),
            "country": random.choice(["KY", "VG", "BS"]),
            "is_fraud": 1,
            "cluster": f"AGGREGATION_FUNNEL_{f_idx}",
            "status": "ACTIVE"
        }
        nodes.append(exit_node)

        feeder_count = random.randint(6, 10)
        for fd in range(1, feeder_count + 1):
            feeder_id = f"FEEDER-{f_idx}{fd:02d}"
            feeder = {
                "id": feeder_id,
                "name": f"Sleeper Domestic Feeder #{f_idx}-{fd}",
                "type": "Personal",
                "balance": round(random.uniform(1200, 4800), 2),
                "country": "US",
                "is_fraud": 1,
                "cluster": f"AGGREGATION_FUNNEL_{f_idx}",
                "status": "ACTIVE"
            }
            nodes.append(feeder)

            edges.append({
                "id": f"TX-FUNNEL-{f_idx}-{fd}",
                "source": feeder_id,
                "target": exit_id,
                "amount": round(random.uniform(25000.0, 48000.0), 2),
                "note": "Liquidation Funnel Consolidation",
                "channel": "SWIFT WIRE",
                "is_suspicious": 1,
                "pattern": "AGGREGATION_FUNNEL",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=random.randint(4, 96))).isoformat()
            })

    # D. Legitimate Retail, Merchants, Corporate, and Personal Nodes (~450 nodes)
    current_count = len(nodes)
    target_total = 520
    needed_normal = target_total - current_count

    merchant_names = [
        "Amazon Corp", "Target Stores", "Chevron Gas", "Starbucks Retail", "Apple Store Direct",
        "Walmart Supercenter", "Home Depot Supply", "Costco Wholesale", "Kroger Groceries",
        "Best Buy Electronics", "Trader Joes", "Shell Petroleum", "Delta Air Lines", "Uber Mobility"
    ]

    normal_nodes = []
    # Seed top merchants
    for idx, mname in enumerate(merchant_names, 1):
        mid = f"MERCHANT-{idx:03d}"
        node = {
            "id": mid,
            "name": mname,
            "type": "Merchant",
            "balance": round(random.uniform(85000, 950000), 2),
            "country": "US",
            "is_fraud": 0,
            "cluster": "COMMUNITY_RETAIL_COMMERCE",
            "status": "ACTIVE"
        }
        nodes.append(node)
        normal_nodes.append(node)

    # Seed personal and payroll accounts
    p_needed = target_total - len(nodes)
    first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Oliver", "Isabella", "Benjamin", "Mia", "Lucas", "Charlotte"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]

    for p in range(1, p_needed + 1):
        pid = f"ACC-{p+100:04d}"
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        acc_type = random.choice(["Personal", "Corporate", "Personal", "Personal"])
        node = {
            "id": pid,
            "name": f"{full_name} ({acc_type})",
            "type": acc_type,
            "balance": round(random.uniform(1500, 45000), 2),
            "country": random.choice(["US", "US", "US", "CA", "UK", "DE", "FR"]),
            "is_fraud": 0,
            "cluster": "COMMUNITY_NORMAL",
            "status": "ACTIVE"
        }
        nodes.append(node)
        normal_nodes.append(node)

    # Normal Transactions to bring total edges to ~1,650
    target_edges = 1650
    merchants_list = [n for n in normal_nodes if n["type"] == "Merchant"]
    personals_list = [n for n in normal_nodes if n["type"] != "Merchant"]

    tx_counter = len(edges) + 1
    while len(edges) < target_edges:
        tx_type = random.choice(["retail_purchase", "p2p_transfer", "payroll_deposit", "merchant_settlement"])
        if tx_type == "retail_purchase" and merchants_list and personals_list:
            src = random.choice(personals_list)["id"]
            dst = random.choice(merchants_list)["id"]
            amt = round(random.uniform(12.50, 480.00), 2)
            note = random.choice(["Retail Purchase", "Online Checkout", "POS Debit", "Grocery Shopping", "Utility Bill"])
            channel = random.choice(["ACH/CARD", "VISA/DEBIT", "MASTERCARD", "APPLE PAY"])
        elif tx_type == "p2p_transfer" and len(personals_list) >= 2:
            src, dst = random.sample(personals_list, 2)
            src_id = src["id"]
            dst_id = dst["id"]
            amt = round(random.uniform(20.00, 850.00), 2)
            note = random.choice(["Dinner Reimbursement", "Rent Split", "Freelance Gig", "Family Support", "Used Furniture"])
            channel = "P2P ZELLE"
        elif tx_type == "payroll_deposit" and merchants_list and personals_list:
            src = random.choice(merchants_list)["id"]
            dst = random.choice(personals_list)["id"]
            amt = round(random.uniform(2200.00, 6800.00), 2)
            note = "Bi-Weekly Salary Direct Deposit"
            channel = "DIRECT DEPOSIT ACH"
        else:
            if len(personals_list) >= 2:
                src, dst = random.sample(personals_list, 2)
                src_id = src["id"]
                dst_id = dst["id"]
                amt = round(random.uniform(45.0, 1200.0), 2)
                note = "Commercial Payment"
                channel = "FEDWIRE"
            else:
                continue

        edges.append({
            "id": f"TX-NORM-{tx_counter:05d}",
            "source": src_id if 'src_id' in locals() else src,
            "target": dst_id if 'dst_id' in locals() else dst,
            "amount": amt,
            "note": note,
            "channel": channel,
            "is_suspicious": 0,
            "pattern": "NORMAL_COMMERCE",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))).isoformat()
        })
        tx_counter += 1

    print(f"Generated {len(nodes)} accounts and {len(edges)} transactions.")
    return nodes, edges

# ─── 2. COMPUTE GRAPH TOPOLOGICAL FEATURES ───

def build_feature_matrix(nodes, edges):
    node_id_to_idx = {n["id"]: idx for idx, n in enumerate(nodes)}
    N = len(nodes)
    
    in_degrees = np.zeros(N)
    out_degrees = np.zeros(N)
    inflows = np.zeros(N)
    outflows = np.zeros(N)
    adj_matrix = np.zeros((N, N), dtype=np.float32)

    for edge in edges:
        s_idx = node_id_to_idx.get(edge["source"])
        t_idx = node_id_to_idx.get(edge["target"])
        if s_idx is not None and t_idx is not None:
            adj_matrix[s_idx, t_idx] = 1.0
            out_degrees[s_idx] += 1
            in_degrees[t_idx] += 1
            outflows[s_idx] += float(edge["amount"])
            inflows[t_idx] += float(edge["amount"])

    # Feature vector X per node:
    # 0: log10(balance + 1)
    # 1: in_degree normalized
    # 2: out_degree normalized
    # 3: log10(total_inflow + 1)
    # 4: log10(total_outflow + 1)
    # 5: country_risk
    # 6: fan_out_ratio (out_degree / (in_degree + out_degree + 1e-5))
    # 7: flow_asymmetry ((inflow - outflow) / (inflow + outflow + 1e-5))
    X = np.zeros((N, 8), dtype=np.float32)
    labels = np.zeros(N, dtype=np.int64)

    for idx, n in enumerate(nodes):
        bal = max(0.0, float(n["balance"]))
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
        labels[idx] = int(n["is_fraud"])

    # Compute symmetric normalized adjacency matrix: A_hat = D_tilde^(-1/2) * A_tilde * D_tilde^(-1/2)
    A_sym = np.maximum(adj_matrix, adj_matrix.T)
    A_tilde = A_sym + np.eye(N, dtype=np.float32)
    d_tilde = np.sum(A_tilde, axis=1)
    d_inv_sqrt = np.power(d_tilde, -0.5)
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0
    D_tilde_mat = np.diag(d_inv_sqrt)
    A_hat = D_tilde_mat @ A_tilde @ D_tilde_mat

    return X, A_hat, labels, in_degrees, out_degrees, inflows, outflows

# ─── 3. 2-LAYER GRAPH CONVOLUTIONAL NETWORK (GCN) ARCHITECTURE ───

class GraphConvolutionLayer(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super(GraphConvolutionLayer, self).__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, x, adj):
        # Support = X * W
        support = torch.mm(x, self.weight)
        # Output = Adj * Support
        output = torch.mm(adj, support)
        if self.bias is not None:
            output = output + self.bias
        return output

class FinancialGCN(nn.Module):
    def __init__(self, nfeat=8, nhid=16, nclass=2, dropout=0.2):
        super(FinancialGCN, self).__init__()
        self.gc1 = GraphConvolutionLayer(nfeat, nhid)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.gc2 = GraphConvolutionLayer(nhid, nclass)

    def forward(self, x, adj):
        # Layer 1 message passing -> 16-dim latent node embedding H1
        h1 = self.relu(self.gc1(x, adj))
        h1_drop = self.dropout(h1)
        # Layer 2 message passing -> Class logits
        logits = self.gc2(h1_drop, adj)
        return logits, h1

# ─── 4. TRAIN AND EVALUATE MODEL ───

def train_and_evaluate():
    nodes, edges = generate_graph_dataset()
    X, A_hat, labels, in_deg, out_deg, inflows, outflows = build_feature_matrix(nodes, edges)

    # Standardize continuous features
    feat_mean = np.mean(X, axis=0)
    feat_std = np.std(X, axis=0) + 1e-6
    X_norm = (X - feat_mean) / feat_std

    # Convert to PyTorch tensors
    x_tensor = torch.FloatTensor(X_norm)
    adj_tensor = torch.FloatTensor(A_hat)
    labels_tensor = torch.LongTensor(labels)

    # Train / Val / Test split mask (60% train, 20% val, 20% test)
    N = len(nodes)
    indices = np.arange(N)
    np.random.shuffle(indices)

    train_idx = indices[: int(0.6 * N)]
    val_idx = indices[int(0.6 * N): int(0.8 * N)]
    test_idx = indices[int(0.8 * N):]

    train_mask = torch.zeros(N, dtype=torch.bool)
    val_mask = torch.zeros(N, dtype=torch.bool)
    test_mask = torch.zeros(N, dtype=torch.bool)
    train_mask[train_idx] = True
    val_mask[val_idx] = True
    test_mask[test_idx] = True

    model = FinancialGCN(nfeat=8, nhid=16, nclass=2, dropout=0.2)
    # Handle class imbalance: clean accounts vs fraud accounts
    fraud_weight = float(np.sum(labels == 0)) / float(max(1, np.sum(labels == 1)))
    weight_tensor = torch.FloatTensor([1.0, fraud_weight * 0.75])
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    optimizer = optim.Adam(model.parameters(), lr=0.015, weight_decay=5e-4)

    print("Training 2-Layer Financial GCN for 200 epochs...")
    model.train()
    for epoch in range(1, 201):
        optimizer.zero_grad()
        logits, _ = model(x_tensor, adj_tensor)
        loss = criterion(logits[train_mask], labels_tensor[train_mask])
        loss.backward()
        optimizer.step()

        if epoch % 50 == 0 or epoch == 200:
            model.eval()
            with torch.no_grad():
                val_logits, _ = model(x_tensor, adj_tensor)
                val_preds = torch.argmax(val_logits[val_mask], dim=1)
                val_acc = (val_preds == labels_tensor[val_mask]).float().mean().item()
                print(f"Epoch {epoch:03d} | Train Loss: {loss.item():.4f} | Val Accuracy: {val_acc*100:.2f}%")
            model.train()

    # Final Evaluation on Test Set
    model.eval()
    with torch.no_grad():
        test_logits, embeddings = model(x_tensor, adj_tensor)
        probs = torch.softmax(test_logits, dim=1)[:, 1].numpy()
        preds = torch.argmax(test_logits, dim=1).numpy()
        test_labels = labels[test_idx]
        test_preds = preds[test_idx]

        tp = np.sum((test_preds == 1) & (test_labels == 1))
        fp = np.sum((test_preds == 1) & (test_labels == 0))
        fn = np.sum((test_preds == 0) & (test_labels == 1))
        tn = np.sum((test_preds == 0) & (test_labels == 0))

        accuracy = (tp + tn) / max(1, len(test_idx))
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * (precision * recall) / max(1e-6, precision + recall)

        print("\n--- TEST SET EVALUATION ---")
        print(f"Accuracy:  {accuracy*100:.2f}%")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall:    {recall*100:.2f}%")
        print(f"F1-Score:  {f1:.4f}")

    # Attach computed metrics & embeddings back to nodes
    all_probs = torch.softmax(test_logits, dim=1)[:, 1].numpy()
    emb_numpy = embeddings.numpy()

    for i, n in enumerate(nodes):
        n["in_degree"] = int(in_deg[i])
        n["out_degree"] = int(out_deg[i])
        n["total_inflow"] = round(float(inflows[i]), 2)
        n["total_outflow"] = round(float(outflows[i]), 2)
        n["risk"] = round(float(all_probs[i]), 4)
        n["gnn_embedding"] = [round(float(v), 4) for v in emb_numpy[i][:8]]  # First 8 dimensions

    # Save accounts.csv and transactions.csv
    accounts_csv_path = os.path.join(DATA_DIR, "accounts.csv")
    with open(accounts_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "name", "type", "balance", "country", "is_fraud", "cluster", "status", "in_degree", "out_degree", "total_inflow", "total_outflow", "risk"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for n in nodes:
            writer.writerow({k: n[k] for k in fieldnames})
    print(f"Saved {len(nodes)} accounts to {accounts_csv_path}")

    transactions_csv_path = os.path.join(DATA_DIR, "transactions.csv")
    with open(transactions_csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "source", "target", "amount", "note", "channel", "is_suspicious", "pattern", "timestamp"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in edges:
            writer.writerow(e)
    print(f"Saved {len(edges)} transactions to {transactions_csv_path}")

    # Save PyTorch model weights
    weights_path = os.path.join(BACKEND_DIR, "gnn_weights.pt")
    torch.save(model.state_dict(), weights_path)
    print(f"Saved model weights to {weights_path}")

    # Save model metadata and feature scalers
    metadata = {
        "model_architecture": "2-Layer Graph Convolutional Network (GCN)",
        "input_features": 8,
        "hidden_embedding_dim": 16,
        "output_classes": 2,
        "classes": ["CLEAN", "FRAUD_MULE_RING"],
        "feature_names": [
            "log10_balance", "in_degree", "out_degree", "log10_inflow",
            "log10_outflow", "country_risk", "fan_out_ratio", "flow_asymmetry"
        ],
        "feature_mean": [float(m) for m in feat_mean],
        "feature_std": [float(s) for s in feat_std],
        "metrics": {
            "test_accuracy": round(float(accuracy), 4),
            "test_precision": round(float(precision), 4),
            "test_recall": round(float(recall), 4),
            "test_f1": round(float(f1), 4),
            "training_samples": len(train_idx),
            "validation_samples": len(val_idx),
            "test_samples": len(test_idx),
            "total_nodes": N,
            "total_edges": len(edges)
        },
        "trained_timestamp": datetime.now(timezone.utc).isoformat()
    }
    metadata_path = os.path.join(BACKEND_DIR, "gnn_model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to {metadata_path}")

if __name__ == "__main__":
    train_and_evaluate()
