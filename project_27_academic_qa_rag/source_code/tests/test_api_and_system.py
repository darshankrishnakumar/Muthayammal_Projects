import os
import sys
import unittest
import json
import torch
import numpy as np

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
from rag_engine import get_rag_engine
from app import app

class TestAcademicQARAGSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.seed_database(force=True)
        cls.engine = get_rag_engine()
        cls.client = app.test_client()

    # 1. Health Endpoint
    def test_01_health_endpoint(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['port'], 5027)
        self.assertIn('Dense Bi-Encoder', data['architecture'])
        self.assertIn('academic_rag.db', data['database_backend'])
        self.assertEqual(data['embedding_dimension'], 128)

    # 2. Model Metadata
    def test_02_model_metadata(self):
        res = self.client.get('/api/model/metadata')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['embedding_dimensions'], 128)
        self.assertGreaterEqual(data['total_indexed_chunks'], 5000)
        self.assertIn('Systems & Concurrency', data['domains'])

    # 3. Dense Retrieval: Transformer Attention
    def test_03_retrieve_transformer_attention(self):
        q = "Explain how Scaled Dot-Product Attention works in Transformers"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.85)
        top_src = res['top_sources'][0]
        self.assertIn('Attention Is All You Need', top_src['doc_name'])
        self.assertIn('DL-C03-004', top_src['chunk_id'])

    # 4. Dense Retrieval: Virtual Memory & TLB
    def test_04_retrieve_virtual_memory_tlb(self):
        q = "What is the difference between page tables and the TLB in virtual memory?"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.85)
        top_src = res['top_sources'][0]
        self.assertIn('Operating Systems', top_src['doc_name'])
        self.assertIn('OS-C18-142', top_src['chunk_id'])

    # 5. Dense Retrieval: Dijkstra Shortest Paths
    def test_05_retrieve_dijkstra_shortest_path(self):
        q = "How does Dijkstras shortest path algorithm achieve O(V log V + E) running time?"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.85)
        top_src = res['top_sources'][0]
        self.assertIn('Introduction to Algorithms', top_src['doc_name'])
        self.assertIn('ALGO-C24-658', top_src['chunk_id'])

    # 6. Dense Retrieval: Database ACID & WAL
    def test_06_retrieve_database_acid_wal(self):
        q = "What is Write-Ahead Logging (WAL) in relational database ACID transactions?"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.85)
        top_src = res['top_sources'][0]
        self.assertIn('Database System Concepts', top_src['doc_name'])
        self.assertIn('DB-C14-620', top_src['chunk_id'])

    # 7. Dense Retrieval: Raft Consensus
    def test_07_retrieve_raft_consensus(self):
        q = "How does Raft consensus elect leaders and maintain replicated logs?"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.80)
        doc_names = [s['doc_name'] for s in res['top_sources']]
        chunk_ids = [s['chunk_id'] for s in res['top_sources']]
        self.assertTrue(any('Designing Data-Intensive Applications' in d for d in doc_names))
        self.assertTrue(any('DIST-C09-352' in c for c in chunk_ids))

    # 8. Dense Retrieval: TCP Congestion Control
    def test_08_retrieve_tcp_congestion_control(self):
        q = "How does TCP Reno and Cubic congestion control adjust the cwnd?"
        res = self.engine.retrieve(q, top_k=3)
        self.assertGreater(res['confidence'], 0.80)
        top_src = res['top_sources'][0]
        self.assertIn('Computer Networks', top_src['doc_name'])
        self.assertIn('NET-C06-574', top_src['chunk_id'])

    # 9. Grounded Answer Synthesis
    def test_09_grounded_answer_synthesis(self):
        q = "Explain Scaled Dot-Product Attention"
        res = self.engine.retrieve(q, top_k=3)
        self.assertIn("Based on **Attention Is All You Need", res['answer'])
        self.assertIn("Theoretical Synthesis", res['answer'])

    # 10. Source Citations Structure
    def test_10_citations_structure(self):
        q = "Explain red-black trees complexity"
        res = self.engine.retrieve(q, top_k=3)
        self.assertEqual(len(res['top_sources']), 3)
        for s in res['top_sources']:
            self.assertIn('doc_name', s)
            self.assertIn('section', s)
            self.assertIn('page', s)
            self.assertIn('chunk_id', s)
            self.assertIn('relevance_score', s)

    # 11. Database Schema
    def test_11_database_schema(self):
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r['name'] for r in cur.fetchall()]
        conn.close()
        for expected in ['documents', 'academic_chunks', 'qa_query_history', 'citation_records', 'audit_log']:
            self.assertIn(expected, tables)

    # 12. Insert QA Query Transaction
    def test_12_insert_qa_query(self):
        record = {
            'question': 'How does CFS scheduling work?',
            'answer': 'Based on Operating Systems Three Easy Pieces...',
            'confidence': 0.965,
            'retrieval_latency_ms': 25,
            'generation_latency_ms': 190,
            'tokens_generated': 140,
            'top_sources': [
                {
                    'doc_name': 'Operating Systems: Three Easy Pieces (Arpaci-Dusseau)',
                    'section': 'Chapter 9: Completely Fair Scheduler (CFS)',
                    'page': 84,
                    'relevance_score': 0.965,
                    'chunk_id': 'OS-C09-084',
                    'excerpt': 'The Linux Completely Fair Scheduler...'
                }
            ]
        }
        qid = database.insert_qa_query(record)
        self.assertIsInstance(qid, int)
        self.assertGreater(qid, 0)

    # 13. Recent History Retrieval
    def test_13_get_recent_history(self):
        history = database.get_recent_history(limit=5)
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)
        self.assertIn('top_sources', history[0])

    # 14. Documents List Retrieval
    def test_14_get_documents_list(self):
        docs = database.get_documents_list()
        self.assertGreaterEqual(len(docs), 6)
        self.assertEqual(docs[0]['id'], 1)

    # 15. System Statistics Rollup
    def test_15_system_stats(self):
        stats = database.get_stats()
        self.assertIn('total_queries', stats)
        self.assertIn('avg_confidence_pct', stats)
        self.assertIn('indexed_corpora', stats)
        self.assertGreaterEqual(stats['total_queries'], 1)

    # 16. API Endpoint: POST /api/ask
    def test_16_api_ask_endpoint(self):
        res = self.client.post('/api/ask', json={'question': 'Explain dynamic programming memoization'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('answer', data)
        self.assertIn('confidence_pct', data)
        self.assertIn('top_sources', data)

    # 17. API Endpoint: POST /api/ask with Empty Question
    def test_17_api_ask_empty_question(self):
        res = self.client.post('/api/ask', json={'question': ''})
        self.assertEqual(res.status_code, 400)

    # 18. API Endpoint: GET /api/documents
    def test_18_api_documents(self):
        res = self.client.get('/api/documents')
        self.assertEqual(res.status_code, 200)
        docs = res.get_json()
        self.assertGreaterEqual(len(docs), 6)
        self.assertIn('doc_name', docs[0])

    # 19. API Endpoint: GET /api/history
    def test_19_api_history(self):
        res = self.client.get('/api/history')
        self.assertEqual(res.status_code, 200)
        history = res.get_json()
        self.assertIsInstance(history, list)

    # 20. API Endpoint: GET /api/stats
    def test_20_api_stats(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('avg_confidence_pct', data)

    # 21. Static Frontend Serving
    def test_21_serve_index(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Academic QA with Retrieval-Augmented Generation', res.data)

    # 22. Unit L2 Normalization of Embeddings
    def test_22_embedding_unit_norm(self):
        tensor = self.engine.text_to_tensor("test academic query").unsqueeze(0)
        with torch.no_grad():
            emb = self.engine.model(tensor).numpy()[0]
        norm = np.linalg.norm(emb)
        self.assertAlmostEqual(norm, 1.0, places=4)

    # 23. Top Sources Sorting
    def test_23_top_sources_sorting(self):
        res = self.engine.retrieve("virtual memory paging TLB", top_k=3)
        scores = [s['relevance_score'] for s in res['top_sources']]
        self.assertEqual(scores, sorted(scores, reverse=True))

    # 24. Query with Special Characters
    def test_24_query_special_chars(self):
        res = self.engine.retrieve("What is O(V log V + E) in Dijkstra's algorithm??? #graph @path", top_k=2)
        self.assertIn('answer', res)
        self.assertGreater(len(res['top_sources']), 0)

    # 25. Out-of-Vocabulary Robustness
    def test_25_out_of_vocab_query(self):
        res = self.engine.retrieve("xyzzy quantum teleportation superluminal chronosync", top_k=2)
        self.assertIn('answer', res)
        self.assertIsInstance(res['confidence'], float)

    # 26. Relevance Score Range Bounds
    def test_26_relevance_score_bounds(self):
        res = self.engine.retrieve("Explain B+ tree disk I/O in databases", top_k=3)
        for s in res['top_sources']:
            self.assertGreaterEqual(s['relevance_score'], 0.0)
            self.assertLessEqual(s['relevance_score'], 1.0)

    # 27. Audit Log Presence
    def test_27_audit_log_entries(self):
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM audit_log")
        cnt = cur.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(cnt, 1)

if __name__ == '__main__':
    unittest.main()
