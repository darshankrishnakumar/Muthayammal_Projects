import os
import json
import random
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import database
from rag_engine import get_rag_engine

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Initialize database
database.init_db()
database.seed_database()

# Load RAG Engine
engine = get_rag_engine()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    target = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({'error': 'Not found'}), 404

# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    stats = database.get_stats()
    return jsonify({
        'status': 'healthy',
        'service': 'Academic Retrieval-Augmented Generation (RAG) System API',
        'architecture': 'Dense Bi-Encoder (PyTorch) + Hybrid Lexical BM25 Ranking',
        'database_backend': 'SQLite ACID Relational DB (academic_rag.db)',
        'vector_db': 'FAISS / NPZ Dense Vector Index (L2 Cosine, 128D)',
        'port': 5027,
        'model_metadata': engine.metadata,
        'indexed_documents': stats['indexed_corpora'],
        'total_chunks': stats['total_indexed_chunks'],
        'embedding_dimension': 128
    })

@app.route('/api/model/metadata', methods=['GET'])
def model_metadata():
    return jsonify(engine.metadata)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = database.get_stats()
    return jsonify(stats)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    result = engine.retrieve(question, top_k=3)
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **result
    }
    query_id = database.insert_qa_query(entry)
    entry['id'] = query_id
    return jsonify(entry)

@app.route('/api/documents', methods=['GET'])
def get_documents():
    docs = database.get_documents_list()
    # If chunks info needed, attach topics
    for d in docs:
        d['doc_name'] = d.get('title')
        d['topics'] = [d.get('domain', 'Computer Science')]
        d['chunks'] = [1, 2] # presentation indicator
    return jsonify(docs)

@app.route('/api/history', methods=['GET'])
def get_history():
    history = database.get_recent_history(limit=30)
    return jsonify(history)

if __name__ == '__main__':
    print("=" * 65)
    print("🚀 Academic Question Answering RAG System (PROJECT-027)")
    print("🔒 Dedicated Port: Port 5027 (http://127.0.0.1:5027/)")
    print("🧠 Engine: PyTorch Dense Bi-Encoder + Hybrid BM25 Ranking")
    print("💾 Database: SQLite ACID Ledger (academic_rag.db)")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5027, debug=False)
