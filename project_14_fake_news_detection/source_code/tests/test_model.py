import os
import sys
import pickle
import pytest
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import (
    loaded_model, vector, lemmatizer, stpwrds,
    analyze_news, strip_publisher_watermarks, SENSATIONAL_WORDS,
    SPECULATIVE_WORDS, OBJECTIVE_JOURNALISTIC_WORDS
)

def test_model_and_vectorizer_loaded():
    assert loaded_model is not None
    assert vector is not None
    assert hasattr(loaded_model, "predict")
    assert hasattr(loaded_model, "decision_function")
    assert hasattr(vector, "transform")

def test_vectorizer_vocabulary():
    vocab = vector.vocabulary_
    assert len(vocab) > 1000
    assert "trump" in vocab or "president" in vocab or "state" in vocab

def test_stopword_removal_and_lemmatizer():
    assert "the" in stpwrds
    assert "and" in stpwrds
    lemma = lemmatizer.lemmatize("running", pos="v")
    assert lemma == "run"

def test_source_watermark_stripping():
    text_with_source = "Senate passes bipartisan budget bill - Reuters"
    cleaned = strip_publisher_watermarks(text_with_source)
    assert "Reuters" not in cleaned
    assert "Senate passes bipartisan budget bill" in cleaned

    text_with_cnn = "CNN - Major wildfire contained in northern California"
    cleaned_cnn = strip_publisher_watermarks(text_with_cnn)
    assert "CNN" not in cleaned_cnn
    assert "Major wildfire contained" in cleaned_cnn

def test_sensationalism_radar():
    sensational_text = "SHOCKING BOMBSHELL: Secret classified documents EXPOSE massive conspiracy hoax!"
    res = analyze_news(sensational_text)
    assert res["sensational_score"] >= 50
    assert "Sensationalism" in res["sensationalism_level"]
    assert len(res["detected_sensational"]) >= 2

def test_speculative_framing():
    speculative_text = "Sources allegedly claim unconfirmed rumors suggest impending executive resignation"
    res = analyze_news(speculative_text)
    assert len(res["detected_speculative"]) >= 2

def test_objective_journalism():
    objective_text = "The Department of Transportation announced official scheduled hearings agreed upon by the council"
    res = analyze_news(objective_text)
    assert len(res["detected_objective"]) >= 2
    assert "Formal" in res["sensationalism_level"] or "Neutral" in res["tone_description"]

def test_fake_news_classification():
    fake_headline = "SHOCKING PROOF: Hillary Clinton secretly runs underground cannibal ring exposed by leaked emails!"
    res = analyze_news(fake_headline)
    assert res is not None
    assert res["is_fake"] is True
    assert "Fake" in res["verdict_title"]
    assert res["fake_pct"] > 50.0

def test_real_news_classification():
    real_headline = "United States Supreme Court justices issued an official written opinion concerning environmental regulation authority"
    res = analyze_news(real_headline)
    assert res is not None
    assert res["is_fake"] is False
    assert "Real" in res["verdict_title"]
    assert res["real_pct"] > 50.0

def test_pure_language_mode():
    headline = "Shocking truth about economic inflation numbers - The New York Times"
    res_normal = analyze_news(headline, pure_language_mode=False)
    res_pure = analyze_news(headline, pure_language_mode=True)
    assert res_pure["pure_language_mode"] is True
    assert res_pure["working_text"] != headline
