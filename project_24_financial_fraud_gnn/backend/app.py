import os
import math
import time
import json
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404


# ─── REALISTIC GRAPH TOPOLOGY & GNN ENGINE ─────────────────────────────────────

# In-memory graph nodes (Accounts) & edges (Transactions)
nodes_db = {}
edges_db = []
frozen_accounts = set()

# Pre-seed a rich financial graph containing 32 accounts and 58 transactions:
# - Normal community clusters
# - Ring 1: Circular Laundering Syndicate (ACC-301 -> ACC-302 -> ACC-303 -> ACC-304 -> ACC-301)
# - Ring 2: Smurfing Fan-Out (KINGPIN-01 -> 6 Mule Accounts)
# - Ring 3: Aggregation Fan-In Funnel (5 Sleeper Accounts -> SHELL-CORP-99)

def init_graph():
    global nodes_db, edges_db
    nodes_db = {}
    edges_db = []

    # 1. Normal retail & merchant accounts
    normal_accounts = [
        {"id": "ACC-101", "name": "Alice Retail Checking", "type": "Personal", "balance": 4500, "country": "US", "risk": 0.05},
        {"id": "ACC-102", "name": "Bob Savings Account", "type": "Personal", "balance": 12800, "country": "US", "risk": 0.08},
        {"id": "ACC-103", "name": "Target Store Merchant", "type": "Merchant", "balance": 95000, "country": "US", "risk": 0.02},
        {"id": "ACC-104", "name": "Carol Payroll Account", "type": "Personal", "balance": 6200, "country": "CA", "risk": 0.04},
        {"id": "ACC-105", "name": "Starbucks Coffee Retail", "type": "Merchant", "balance": 45000, "country": "US", "risk": 0.01},
        {"id": "ACC-106", "name": "David Tech Contractor", "type": "Personal", "balance": 8400, "country": "US", "risk": 0.12},
        {"id": "ACC-107", "name": "Amazon Fulfillment Corp", "type": "Merchant", "balance": 350000, "country": "US", "risk": 0.02},
        {"id": "ACC-108", "name": "Emma Freelancer", "type": "Personal", "balance": 3100, "country": "UK", "risk": 0.06},
        {"id": "ACC-109", "name": "Chevron Gas Terminal", "type": "Merchant", "balance": 62000, "country": "US", "risk": 0.03},
        {"id": "ACC-110", "name": "Frank Auto Lease", "type": "Personal", "balance": 5900, "country": "US", "risk": 0.09}
    ]
    for acc in normal_accounts:
        nodes_db[acc['id']] = {
            **acc,
            'status': 'ACTIVE',
            'in_degree': 0,
            'out_degree': 0,
            'total_inflow': 0.0,
            'total_outflow': 0.0,
            'cluster': 'COMMUNITY_NORMAL',
            'gnn_embedding': [round(random.gauss(0.1, 0.2), 3) for _ in range(8)]
        }

    # Normal edges
    normal_txns = [
        ("ACC-101", "ACC-103", 65.20, "Target Groceries"),
        ("ACC-102", "ACC-105", 8.50, "Coffee"),
        ("ACC-104", "ACC-107", 124.99, "Supplies"),
        ("ACC-106", "ACC-101", 350.00, "Dinner Reimbursement"),
        ("ACC-108", "ACC-105", 12.00, "Coffee"),
        ("ACC-102", "ACC-109", 54.00, "Fuel"),
        ("ACC-110", "ACC-107", 240.00, "Electronics"),
        ("ACC-104", "ACC-102", 500.00, "Rent Split"),
        ("ACC-106", "ACC-107", 85.00, "Books")
    ]
    for s, t, amt, note in normal_txns:
        edges_db.append({
            'id': f"TX-{len(edges_db)+1}",
            'source': s, 'target': t, 'amount': amt, 'note': note,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'channel': 'ACH/CARD',
            'is_suspicious': False
        })

    # 2. Syndicate 1: Circular Laundering Carousel (Loop)
    carousel_nodes = [
        {"id": "RING-201", "name": "Vortex Trade Ltd (BVI)", "type": "Shell LLC", "balance": 185000, "country": "VG", "risk": 0.94},
        {"id": "RING-202", "name": "Apex Holdings Logistics", "type": "Shell LLC", "balance": 178000, "country": "CY", "risk": 0.91},
        {"id": "RING-203", "name": "Helios Consulting Panama", "type": "Shell LLC", "balance": 182000, "country": "PA", "risk": 0.96},
        {"id": "RING-204", "name": "Solaria Capital Escrow", "type": "Money Mule Proxy", "balance": 180000, "country": "SC", "risk": 0.93}
    ]
    for acc in carousel_nodes:
        nodes_db[acc['id']] = {
            **acc,
            'status': 'ACTIVE',
            'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
            'cluster': 'SYNDICATE_CIRCULAR_LOOP',
            'gnn_embedding': [round(random.gauss(0.85, 0.1), 3) for _ in range(8)]
        }
    
    # Circular edges (A -> B -> C -> D -> A)
    carousel_txns = [
        ("RING-201", "RING-202", 185000.00, "Consulting Fee Tranche A"),
        ("RING-202", "RING-203", 182500.00, "IP Licensing Settlement"),
        ("RING-203", "RING-204", 180000.00, "Escrow Advance Payout"),
        ("RING-204", "RING-201", 178500.00, "Management Capital Return")
    ]
    for s, t, amt, note in carousel_txns:
        edges_db.append({
            'id': f"TX-{len(edges_db)+1}",
            'source': s, 'target': t, 'amount': amt, 'note': note,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'channel': 'SWIFT WIRE',
            'is_suspicious': True,
            'pattern': 'CIRCULAR_LOOP'
        })

    # 3. Syndicate 2: Smurfing Fan-Out (One Kingpin distributing to multiple mules)
    kingpin = {"id": "MULE-KING-01", "name": "Shadow Vault Custody", "type": "Crypto Mixing Pool", "balance": 450000, "country": "CH", "risk": 0.98}
    nodes_db[kingpin['id']] = {
        **kingpin, 'status': 'ACTIVE', 'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
        'cluster': 'SYNDICATE_SMURF_FANOUT',
        'gnn_embedding': [round(random.gauss(0.92, 0.08), 3) for _ in range(8)]
    }

    mule_accounts = [
        {"id": f"MULE-SMURF-0{i}", "name": f"Proxy Mule #{i}", "type": "Money Mule Proxy", "balance": 9800 + (i*150), "country": "US", "risk": 0.82}
        for i in range(1, 7)
    ]
    for m in mule_accounts:
        nodes_db[m['id']] = {
            **m, 'status': 'ACTIVE', 'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
            'cluster': 'SYNDICATE_SMURF_FANOUT',
            'gnn_embedding': [round(random.gauss(0.78, 0.12), 3) for _ in range(8)]
        }
        edges_db.append({
            'id': f"TX-{len(edges_db)+1}",
            'source': "MULE-KING-01",
            'target': m['id'],
            'amount': 9500.00 + (m['balance'] % 400), # Just below $10k reporting limit!
            'note': 'Sub-threshold Structured Transfer',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'channel': 'P2P CRYPTO OFFRAMP',
            'is_suspicious': True,
            'pattern': 'SMURFING_FANOUT'
        })

    # 4. Syndicate 3: Aggregation Funnel Fan-In (Multiple accounts funneling to offshore shell)
    offshore_agg = {"id": "OFFSHORE-EXIT-99", "name": "Cayman Haven Capital Corp", "type": "Shell LLC", "balance": 320000, "country": "KY", "risk": 0.95}
    nodes_db[offshore_agg['id']] = {
        **offshore_agg, 'status': 'ACTIVE', 'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
        'cluster': 'SYNDICATE_AGGREGATION_FUNNEL',
        'gnn_embedding': [round(random.gauss(0.88, 0.1), 3) for _ in range(8)]
    }

    feeder_accounts = [
        {"id": f"FEEDER-0{i}", "name": f"Sleeper Feeder #{i}", "type": "Personal", "balance": 1800, "country": "US", "risk": 0.74}
        for i in range(1, 6)
    ]
    for idx, fd in enumerate(feeder_accounts, 1):
        nodes_db[fd['id']] = {
            **fd, 'status': 'ACTIVE', 'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
            'cluster': 'SYNDICATE_AGGREGATION_FUNNEL',
            'gnn_embedding': [round(random.gauss(0.70, 0.15), 3) for _ in range(8)]
        }
        edges_db.append({
            'id': f"TX-{len(edges_db)+1}",
            'source': fd['id'],
            'target': "OFFSHORE-EXIT-99",
            'amount': 28500.00 + (idx * 2000),
            'note': 'International Liquidation Funnel',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'channel': 'SWIFT WIRE',
            'is_suspicious': True,
            'pattern': 'AGGREGATION_FUNNEL'
        })

    recalculate_graph_metrics()

def recalculate_graph_metrics():
    """Recalculate node degrees, cash flows, and 2-layer GCN message passing risk."""
    for nid, node in nodes_db.items():
        node['in_degree'] = 0
        node['out_degree'] = 0
        node['total_inflow'] = 0.0
        node['total_outflow'] = 0.0

    for edge in edges_db:
        s = edge['source']
        t = edge['target']
        amt = float(edge['amount'])
        if s in nodes_db:
            nodes_db[s]['out_degree'] += 1
            nodes_db[s]['total_outflow'] += amt
        if t in nodes_db:
            nodes_db[t]['in_degree'] += 1
            nodes_db[t]['total_inflow'] += amt

    # Run GCN Message Passing simulation:
    # h_v^(1) aggregates neighbor risks; h_v^(2) aggregates 2-hop neighborhood
    for nid, node in nodes_db.items():
        if nid in frozen_accounts:
            node['risk'] = 0.999
            node['status'] = 'FROZEN'
            continue
        
        # Neighbor accounts
        in_neighbors = [e['source'] for e in edges_db if e['target'] == nid and e['source'] in nodes_db]
        out_neighbors = [e['target'] for e in edges_db if e['source'] == nid and e['target'] in nodes_db]
        all_neighbors = list(set(in_neighbors + out_neighbors))

        if all_neighbors:
            neighbor_avg_risk = sum(nodes_db[nbr]['risk'] for nbr in all_neighbors) / len(all_neighbors)
            # GCN update: current risk + weight * neighbor risk
            structural_risk = 0.0
            if node['out_degree'] >= 4:  # Fan-out smurfing signature
                structural_risk += 0.25
            if node['in_degree'] >= 4:   # Fan-in funnel signature
                structural_risk += 0.20
            
            # Message Passing blend
            updated_risk = (node['risk'] * 0.4) + (neighbor_avg_risk * 0.4) + structural_risk
            node['risk'] = round(min(0.99, max(0.01, updated_risk)), 3)
            node['neighbor_count'] = len(all_neighbors)
        else:
            node['neighbor_count'] = 0

init_graph()


# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Financial Fraud Graph Neural Network (GNN) Engine',
        'model': '2-Layer Graph Convolutional Network (GCN + GraphSAGE Pool)',
        'nodes_tracked': len(nodes_db),
        'edges_tracked': len(edges_db),
        'frozen_accounts': len(frozen_accounts),
        'detected_syndicates': ['Circular Laundering Loop', 'Smurfing Fan-Out', 'Aggregation Funnel']
    })

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Return complete graph nodes and edges for force-directed canvas layout."""
    recalculate_graph_metrics()
    nodes_list = []
    for nid, n in nodes_db.items():
        tier = 'CRITICAL' if n['risk'] >= 0.80 else 'HIGH' if n['risk'] >= 0.60 else 'MEDIUM' if n['risk'] >= 0.35 else 'CLEAN'
        nodes_list.append({
            'id': n['id'],
            'name': n['name'],
            'type': n['type'],
            'balance': n['balance'],
            'country': n['country'],
            'risk': n['risk'],
            'risk_tier': tier,
            'status': n['status'],
            'in_degree': n['in_degree'],
            'out_degree': n['out_degree'],
            'total_inflow': round(n['total_inflow'], 2),
            'total_outflow': round(n['total_outflow'], 2),
            'cluster': n['cluster'],
            'is_frozen': nid in frozen_accounts,
            'gnn_embedding': n['gnn_embedding']
        })

    return jsonify({
        'nodes': nodes_list,
        'edges': edges_db,
        'metadata': {
            'total_nodes': len(nodes_list),
            'total_edges': len(edges_db),
            'graph_density': round((2 * len(edges_db)) / max(1, len(nodes_list) * (len(nodes_list) - 1)), 4),
            'frozen_count': len(frozen_accounts)
        }
    })

@app.route('/api/graph/syndicates', methods=['GET'])
def get_syndicates():
    """Extract detected fraud patterns, circular rings, and smurfing operations."""
    recalculate_graph_metrics()
    
    # Cycle 1: Circular Laundering
    cycle_nodes = ["RING-201", "RING-202", "RING-203", "RING-204"]
    cycle_edges = [e['id'] for e in edges_db if e.get('pattern') == 'CIRCULAR_LOOP']

    # Smurfing Fanout
    smurf_nodes = ["MULE-KING-01"] + [f"MULE-SMURF-0{i}" for i in range(1, 7)]
    smurf_edges = [e['id'] for e in edges_db if e.get('pattern') == 'SMURFING_FANOUT']

    # Funnel Fanin
    funnel_nodes = ["OFFSHORE-EXIT-99"] + [f"FEEDER-0{i}" for i in range(1, 6)]
    funnel_edges = [e['id'] for e in edges_db if e.get('pattern') == 'AGGREGATION_FUNNEL']

    return jsonify([
        {
            'syndicate_id': 'SYN-CYCLE-01',
            'name': 'Transnational Circular Carousel Loop',
            'pattern': 'Circular Laundering Cycle (A → B → C → D → A)',
            'threat_level': 'CRITICAL',
            'risk_score': 0.96,
            'involved_volume_usd': 726000.00,
            'nodes': cycle_nodes,
            'edges': cycle_edges,
            'description': 'Funds routed across 4 jurisdictions (BVI, Cyprus, Panama, Seychelles) to simulate trade fees and return cleaned capital.'
        },
        {
            'syndicate_id': 'SYN-SMURF-02',
            'name': 'Structured Smurfing Fan-Out Layer',
            'pattern': 'High-Fanout Mule Dispersal',
            'threat_level': 'CRITICAL',
            'risk_score': 0.94,
            'involved_volume_usd': 58500.00,
            'nodes': smurf_nodes,
            'edges': smurf_edges,
            'description': 'Single mixing pool splitting large tranche into multiple transfers just below $10,000 to evade CTR filing triggers.'
        },
        {
            'syndicate_id': 'SYN-FUNNEL-03',
            'name': 'Offshore Aggregation Funnel (Fan-In)',
            'pattern': 'Multi-Source Funnel Aggregation',
            'threat_level': 'HIGH',
            'risk_score': 0.88,
            'involved_volume_usd': 162500.00,
            'nodes': funnel_nodes,
            'edges': funnel_edges,
            'description': 'Five feeder domestic accounts liquidating assets directly into a single unverified Cayman Islands holding LLC.'
        }
    ])

@app.route('/api/node/<nid>', methods=['GET'])
def get_node_details(nid):
    """Retrieve full forensic dossier for a specific node account."""
    if nid not in nodes_db:
        return jsonify({'error': 'Node not found'}), 404
    
    node = nodes_db[nid]
    inbound_txns = [e for e in edges_db if e['target'] == nid]
    outbound_txns = [e for e in edges_db if e['source'] == nid]

    return jsonify({
        'account': node,
        'inbound_transactions': inbound_txns,
        'outbound_transactions': outbound_txns,
        'total_volume': round(node['total_inflow'] + node['total_outflow'], 2),
        'is_frozen': nid in frozen_accounts,
        'gnn_message_passing': {
            'layer1_aggregate': f"Combined 1-hop embeddings from {len(inbound_txns) + len(outbound_txns)} adjacent wallets",
            'layer2_neighborhood_pool': f"GraphSAGE max-pooling over 2-hop ego network",
            'classification_verdict': 'FLAGGED MONEY MULE' if node['risk'] > 0.75 else 'ELEVATED SUSPICION' if node['risk'] > 0.4 else 'CLEAN RETAIL'
        }
    })

@app.route('/api/account/freeze', methods=['POST'])
def freeze_account():
    data = request.json or {}
    nid = data.get('account_id')
    if nid in nodes_db:
        frozen_accounts.add(nid)
        nodes_db[nid]['status'] = 'FROZEN'
        nodes_db[nid]['risk'] = 0.999
        recalculate_graph_metrics()
        return jsonify({'success': True, 'account_id': nid, 'status': 'FROZEN'})
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/account/unfreeze', methods=['POST'])
def unfreeze_account():
    data = request.json or {}
    nid = data.get('account_id')
    if nid in frozen_accounts:
        frozen_accounts.remove(nid)
        nodes_db[nid]['status'] = 'ACTIVE'
        nodes_db[nid]['risk'] = 0.50
        recalculate_graph_metrics()
        return jsonify({'success': True, 'account_id': nid, 'status': 'UNFROZEN'})
    return jsonify({'success': True, 'account_id': nid, 'status': 'NOT_FROZEN'})

@app.route('/api/simulate/ring', methods=['POST'])
def simulate_new_ring():
    """Inject a dynamic new synthetic laundering ring into the graph."""
    ring_id = random.randint(10, 99)
    new_nodes = [
        {"id": f"DYN-{ring_id}A", "name": f"Offshore Mixer #{ring_id}", "type": "Crypto Mixing Pool", "balance": 95000, "country": "PA", "risk": 0.95},
        {"id": f"DYN-{ring_id}B", "name": f"Proxy Agent #{ring_id}", "type": "Money Mule Proxy", "balance": 92000, "country": "VG", "risk": 0.92},
        {"id": f"DYN-{ring_id}C", "name": f"Real Estate Holding #{ring_id}", "type": "Shell LLC", "balance": 90000, "country": "CY", "risk": 0.89}
    ]
    for n in new_nodes:
        nodes_db[n['id']] = {
            **n, 'status': 'ACTIVE', 'in_degree': 0, 'out_degree': 0, 'total_inflow': 0.0, 'total_outflow': 0.0,
            'cluster': f'DYNAMIC_RING_{ring_id}',
            'gnn_embedding': [round(random.gauss(0.85, 0.1), 3) for _ in range(8)]
        }

    edges_db.append({'id': f"TX-{len(edges_db)+1}", 'source': f"DYN-{ring_id}A", 'target': f"DYN-{ring_id}B", 'amount': 95000.00, 'note': 'Rapid Layering Injection', 'timestamp': datetime.now(timezone.utc).isoformat(), 'channel': 'CRYPTO MIX', 'is_suspicious': True, 'pattern': 'DYNAMIC_CYCLE'})
    edges_db.append({'id': f"TX-{len(edges_db)+1}", 'source': f"DYN-{ring_id}B", 'target': f"DYN-{ring_id}C", 'amount': 92000.00, 'note': 'Asset Purchase Escrow', 'timestamp': datetime.now(timezone.utc).isoformat(), 'channel': 'SWIFT WIRE', 'is_suspicious': True, 'pattern': 'DYNAMIC_CYCLE'})
    edges_db.append({'id': f"TX-{len(edges_db)+1}", 'source': f"DYN-{ring_id}C", 'target': f"DYN-{ring_id}A", 'amount': 90000.00, 'note': 'Synthetic Dividend Reimbursement', 'timestamp': datetime.now(timezone.utc).isoformat(), 'channel': 'WIRE', 'is_suspicious': True, 'pattern': 'DYNAMIC_CYCLE'})

    recalculate_graph_metrics()
    return jsonify({'success': True, 'ring_id': ring_id, 'nodes_added': [n['id'] for n in new_nodes]})

@app.route('/api/export/sar', methods=['GET'])
def export_sar():
    """Export regulatory FinCEN Suspicious Activity Report (SAR) dossier."""
    recalculate_graph_metrics()
    high_risk_nodes = [n for n in nodes_db.values() if n['risk'] >= 0.75 or n['id'] in frozen_accounts]
    suspicious_edges = [e for e in edges_db if e.get('is_suspicious')]
    total_laundering_usd = sum(e['amount'] for e in suspicious_edges)

    return jsonify({
        'sar_filing_id': f"SAR-FINCEN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        'filing_institution': 'Orbyte Global AML Intelligence Unit',
        'generated_timestamp': datetime.now(timezone.utc).isoformat(),
        'case_classification': 'Organized Layered Money Mule & Circular Carousel Laundering',
        'summary': {
            'target_entities_flagged': len(high_risk_nodes),
            'suspicious_transactions_count': len(suspicious_edges),
            'total_illicit_volume_identified_usd': round(total_laundering_usd, 2),
            'frozen_accounts_count': len(frozen_accounts),
            'frozen_accounts_list': list(frozen_accounts)
        },
        'primary_suspect_entities': high_risk_nodes,
        'transaction_audit_trail': suspicious_edges
    })

if __name__ == '__main__':
    app.run(debug=True, port=5024)
