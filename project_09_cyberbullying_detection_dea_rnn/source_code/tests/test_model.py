import os
import sys
import pytest
import torch
import sqlite3
import json
import numpy as np

# Path setup
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(SRC_DIR, "backend")
MODELS_DIR = os.path.join(SRC_DIR, "models")
DATA_DIR = os.path.join(SRC_DIR, "data")
sys.path.insert(0, BACKEND_DIR)

from main import clean_text, TokenAttention, DEARNNClassifier, CATEGORIES, analyze_tweet, get_db

class TestDEARNNModelAndData:
    def test_clean_text_removes_urls_and_handles(self):
        raw = "Check out https://twitter.com/test @user #hate You are terrible!"
        cleaned = clean_text(raw)
        assert "http" not in cleaned
        assert "@user" not in cleaned
        assert "#hate" not in cleaned
        assert "you are terrible" in cleaned

    def test_clean_text_empty_and_special(self):
        raw = "!!! ??? 12345"
        cleaned = clean_text(raw)
        assert cleaned == ""

    def test_categories_count_and_content(self):
        assert len(CATEGORIES) == 6
        assert "not_cyberbullying" in CATEGORIES
        assert "gender" in CATEGORIES
        assert "religion" in CATEGORIES
        assert "age" in CATEGORIES
        assert "ethnicity" in CATEGORIES
        assert "other_cyberbullying" in CATEGORIES

    def test_token_attention_forward(self):
        batch_size = 4
        seq_len = 10
        hidden_dim = 32
        attn = TokenAttention(hidden_dim)
        x = torch.randn(batch_size, seq_len, hidden_dim)
        context, weights = attn(x)

        assert context.shape == (batch_size, hidden_dim)
        assert weights.shape == (batch_size, seq_len)
        # Weights should sum to 1 along sequence dimension
        sum_weights = weights.sum(dim=-1)
        assert torch.allclose(sum_weights, torch.ones(batch_size), atol=1e-5)

    def test_dea_rnn_classifier_forward(self):
        vocab_size = 100
        embed_dim = 16
        hidden_dim = 16
        num_classes = 6
        model = DEARNNClassifier(vocab_size, embed_dim, hidden_dim, num_classes)
        
        batch_size = 2
        seq_len = 20
        x = torch.randint(0, vocab_size, (batch_size, seq_len))
        logits, weights = model(x)

        assert logits.shape == (batch_size, num_classes)
        assert weights.shape == (batch_size, seq_len)

    def test_dea_rnn_gradient_flow(self):
        vocab_size = 50
        model = DEARNNClassifier(vocab_size, 16, 16, 6)
        x = torch.randint(0, vocab_size, (2, 10))
        target = torch.tensor([0, 3], dtype=torch.long)
        criterion = torch.nn.CrossEntropyLoss()
        
        logits, _ = model(x)
        loss = criterion(logits, target)
        loss.backward()

        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"Gradient missing for {name}"

    def test_model_checkpoint_file(self):
        ckpt_path = os.path.join(MODELS_DIR, "dea_rnn_model.pt")
        assert os.path.exists(ckpt_path), f"Checkpoint missing at {ckpt_path}"
        
        ckpt = torch.load(ckpt_path, map_location="cpu")
        assert "model_state_dict" in ckpt
        assert "vocab" in ckpt
        assert "hyperparameters" in ckpt
        assert len(ckpt["vocab"]) > 100

    def test_metrics_json_integrity(self):
        metrics_file = os.path.join(MODELS_DIR, "model_metrics.json")
        assert os.path.exists(metrics_file), "model_metrics.json missing"
        with open(metrics_file, "r") as f:
            data = json.load(f)
        assert "accuracy" in data
        assert "f1_score" in data
        assert "classes" in data
        assert data["accuracy"] > 0.85

    def test_sqlite_database_scans_table(self):
        db_path = os.path.join(DATA_DIR, "cyberbullying.db")
        assert os.path.exists(db_path), "cyberbullying.db missing"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(scans)")
        cols = {row[1] for row in cur.fetchall()}
        required = {"id", "timestamp", "tweet_text", "predicted_category", "confidence", "severity_score", "moderation_action", "latency_ms"}
        assert required.issubset(cols), f"Missing columns: {required - cols}"
        
        cur.execute("SELECT COUNT(*) FROM scans")
        count = cur.fetchone()[0]
        assert count > 0, "Scans table has no seed rows"
        conn.close()

    def test_analyze_tweet_function_execution(self):
        res = analyze_tweet("This is an inspiring research presentation on machine learning!")
        assert "predicted_category" in res
        assert "confidence" in res
        assert "severity_score" in res
        assert "token_attentions" in res
        assert "probabilities" in res
        assert len(res["probabilities"]) == 6
        assert isinstance(res["token_attentions"], list)
        assert res["latency_ms"] >= 0

    def test_analyze_tweet_severe_bullying(self):
        res = analyze_tweet("You dumb stupid idiot get off the internet you worthless retard")
        assert res["is_cyberbullying"] is True
        assert res["predicted_category"] != "not_cyberbullying"
        assert res["severity_score"] > 0.5
