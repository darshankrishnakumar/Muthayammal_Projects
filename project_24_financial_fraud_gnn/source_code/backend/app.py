import os
import math
import time
import json
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np

import database
from gnn_model import gnn_engine

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Initialize SQLite database on startup
database.init_db()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404


# ─── REAL GNN ENGINE & GRAPH METRICS ──────────────────────────────────────────

def get_evaluated_graph():
    """Retrieve nodes and edges from SQLite, and run GCN forward pass."""
    nodes = database.get_all_nodes()
    edges = database.get_all_edges()
    frozen_set = database.get_frozen_account_ids()

    evaluated_nodes = gnn_engine.predict_graph(nodes, edges, frozen_set)
    # Persist updated degree and flow metrics back to DB asynchronously or periodically
    return evaluated_nodes, edges, frozen_set


# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    nodes = database.get_all_nodes()
    edges = database.get_all_edges()
    frozen_set = database.get_frozen_account_ids()
    syndicates = database.get_all_syndicates()

    return jsonify({
        'status': 'healthy',
        'service': 'Financial Fraud Graph Neural Network (GNN) Engine',
        'model': '2-Layer Graph Convolutional Network (GCN + GraphSAGE Pool)',
        'nodes_tracked': len(nodes),
        'edges_tracked': len(edges),
        'frozen_accounts': len(frozen_set),
        'detected_syndicates': [s['name'] for s in syndicates],
        'database_backend': 'SQLite ACID Relational Graph DB (fraud_graph.db)',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Return complete graph nodes and edges for force-directed canvas layout."""
    evaluated_nodes, edges, frozen_set = get_evaluated_graph()

    return jsonify({
        'nodes': evaluated_nodes,
        'edges': edges,
        'metadata': {
            'total_nodes': len(evaluated_nodes),
            'total_edges': len(edges),
            'graph_density': round((2 * len(edges)) / max(1, len(evaluated_nodes) * (len(evaluated_nodes) - 1)), 4),
            'frozen_count': len(frozen_set),
            'gnn_layers': 2,
            'embedding_dim': 16
        }
    })

@app.route('/api/graph/syndicates', methods=['GET'])
def get_syndicates():
    """Extract detected fraud patterns, circular rings, and smurfing operations from DB."""
    syndicates = database.get_all_syndicates()
    return jsonify(syndicates)

@app.route('/api/node/<nid>', methods=['GET'])
def get_node_details(nid):
    """Retrieve full forensic dossier for a specific node account with GNN explanation."""
    node = database.get_node_by_id(nid)
    if not node:
        return jsonify({'error': 'Node not found'}), 404

    inbound_txns = database.get_inbound_edges(nid)
    outbound_txns = database.get_outbound_edges(nid)
    frozen_set = database.get_frozen_account_ids()
    is_frozen = nid in frozen_set

    # Explain node with GNN topology
    gnn_expl = gnn_engine.explain_node(node, inbound_txns, outbound_txns)

    return jsonify({
        'account': {
            **node,
            'is_frozen': is_frozen
        },
        'inbound_transactions': inbound_txns,
        'outbound_transactions': outbound_txns,
        'total_volume': round(float(node.get('total_inflow', 0.0)) + float(node.get('total_outflow', 0.0)), 2),
        'is_frozen': is_frozen,
        'gnn_message_passing': gnn_expl
    })

@app.route('/api/account/freeze', methods=['POST'])
def freeze_account():
    data = request.json or {}
    nid = data.get('account_id')
    node = database.get_node_by_id(nid)
    if node:
        reason = data.get('reason', 'Autonomous GNN FinCEN Interdiction')
        frozen_by = data.get('frozen_by', 'FinCEN Autonomous Interdiction Agent')
        database.freeze_account(nid, reason=reason, frozen_by=frozen_by)
        return jsonify({'success': True, 'account_id': nid, 'status': 'FROZEN'})
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/account/unfreeze', methods=['POST'])
def unfreeze_account():
    data = request.json or {}
    nid = data.get('account_id')
    node = database.get_node_by_id(nid)
    if node:
        unfrozen_by = data.get('unfrozen_by', 'AML Compliance Officer')
        database.unfreeze_account(nid, unfrozen_by=unfrozen_by)
        return jsonify({'success': True, 'account_id': nid, 'status': 'UNFROZEN'})
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/simulate/ring', methods=['POST'])
def simulate_new_ring():
    """Inject a dynamic new synthetic laundering ring into the database and graph."""
    ring_id = random.randint(100, 999)
    now_str = datetime.now(timezone.utc).isoformat()
    
    new_nodes = [
        {"id": f"DYN-{ring_id}A", "name": f"Offshore Mixer #{ring_id}", "type": "Crypto Mixing Pool", "balance": 145000.0, "country": "PA", "risk": 0.96, "cluster": f"DYNAMIC_RING_{ring_id}"},
        {"id": f"DYN-{ring_id}B", "name": f"Proxy Agent #{ring_id}", "type": "Money Mule Proxy", "balance": 142000.0, "country": "VG", "risk": 0.94, "cluster": f"DYNAMIC_RING_{ring_id}"},
        {"id": f"DYN-{ring_id}C", "name": f"Real Estate Holding #{ring_id}", "type": "Shell LLC", "balance": 140000.0, "country": "CY", "risk": 0.91, "cluster": f"DYNAMIC_RING_{ring_id}"}
    ]

    new_edges = [
        {'id': f"TX-DYN-{ring_id}-1", 'source': f"DYN-{ring_id}A", 'target': f"DYN-{ring_id}B", 'amount': 145000.00, 'note': 'Rapid Layering Injection', 'timestamp': now_str, 'channel': 'CRYPTO MIX', 'is_suspicious': 1, 'pattern': 'DYNAMIC_CYCLE'},
        {'id': f"TX-DYN-{ring_id}-2", 'source': f"DYN-{ring_id}B", 'target': f"DYN-{ring_id}C", 'amount': 142000.00, 'note': 'Asset Purchase Escrow', 'timestamp': now_str, 'channel': 'SWIFT WIRE', 'is_suspicious': 1, 'pattern': 'DYNAMIC_CYCLE'},
        {'id': f"TX-DYN-{ring_id}-3", 'source': f"DYN-{ring_id}C", 'target': f"DYN-{ring_id}A", 'amount': 140000.00, 'note': 'Synthetic Dividend Reimbursement', 'timestamp': now_str, 'channel': 'WIRE', 'is_suspicious': 1, 'pattern': 'DYNAMIC_CYCLE'}
    ]

    syndicate_info = {
        'syndicate_id': f"SYN-DYN-{ring_id}",
        'name': f"Dynamic Multi-Hop Laundering Ring #{ring_id}",
        'pattern': "Dynamic Circular Carousel (A → B → C → A)",
        'threat_level': "CRITICAL",
        'risk_score': 0.95,
        'involved_volume_usd': 427000.00,
        'nodes': [n['id'] for n in new_nodes],
        'edges': [e['id'] for e in new_edges],
        'description': f"Dynamically injected carousel ring cycling funds across Panama, BVI, and Cyprus to evade heuristic velocity filters."
    }

    database.insert_dynamic_ring(new_nodes, new_edges, syndicate_info)

    return jsonify({
        'success': True,
        'ring_id': ring_id,
        'nodes_added': [n['id'] for n in new_nodes],
        'edges_added': [e['id'] for e in new_edges]
    })

@app.route('/api/export/sar', methods=['GET'])
def export_sar():
    """Export regulatory FinCEN Suspicious Activity Report (SAR) dossier."""
    evaluated_nodes, edges, frozen_set = get_evaluated_graph()
    high_risk_nodes = [n for n in evaluated_nodes if n['risk'] >= 0.75 or n['id'] in frozen_set]
    suspicious_edges = [e for e in edges if e.get('is_suspicious')]
    total_laundering_usd = sum(float(e['amount']) for e in suspicious_edges)

    return jsonify({
        'sar_filing_id': f"SAR-FINCEN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        'filing_institution': 'Orbyte Global AML Intelligence Unit',
        'generated_timestamp': datetime.now(timezone.utc).isoformat(),
        'case_classification': 'Organized Layered Money Mule & Circular Carousel Laundering',
        'gnn_detection_engine': '2-Layer GCN + Symmetric Normalized Adjacency',
        'summary': {
            'target_entities_flagged': len(high_risk_nodes),
            'suspicious_transactions_count': len(suspicious_edges),
            'total_illicit_volume_identified_usd': round(total_laundering_usd, 2),
            'frozen_accounts_count': len(frozen_set),
            'frozen_accounts_list': list(frozen_set)
        },
        'primary_suspect_entities': high_risk_nodes[:50],
        'transaction_audit_trail': suspicious_edges[:100]
    })

@app.route('/api/gnn/layers', methods=['GET'])
def get_gnn_layers():
    """Return model architecture inspection metrics."""
    return jsonify({
        'architecture': '2-Layer Graph Convolutional Network',
        'feature_dimension': 8,
        'hidden_dimension': 16,
        'output_classes': 2,
        'classes': ['CLEAN', 'FRAUD_MULE_RING'],
        'layer1_weights_shape': [8, 16],
        'layer2_weights_shape': [16, 2],
        'activation': 'ReLU (Layer 1) -> Softmax (Layer 2)',
        'normalization': 'D^(-1/2) * (A + I) * D^(-1/2)',
        'metadata': gnn_engine.metadata
    })

@app.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    logs = database.get_audit_logs(limit=30)
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True, port=5024)
