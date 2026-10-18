# @Abhishek pp - Upgraded with Decision Visualization, Measurable Experiments & Linguistic Stylometry
import re
import math
import json
import os
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, template_folder='./templates', static_folder='./static')

# Load Pre-trained Artifacts
loaded_model = pickle.load(open("model.pkl", 'rb'))
vector = pickle.load(open("vector.pkl", 'rb'))
lemmatizer = WordNetLemmatizer()
stpwrds = set(stopwords.words('english'))

# Pre-cache vocabulary and model weights
vocab = vector.vocabulary_
coefs = loaded_model.coef_[0]
intercept = float(loaded_model.intercept_[0]) if hasattr(loaded_model, 'intercept_') else 0.0

# Load Measurable Experiments Benchmark Cache
EXPERIMENTS_FILE = "experiments_results.json"
experiments_data = {}
if os.path.exists(EXPERIMENTS_FILE):
    try:
        with open(EXPERIMENTS_FILE, "r") as f:
            experiments_data = json.load(f)
    except Exception as e:
        print(f"Warning: could not load experiments: {e}")

# Intuitive Lexicons
SENSATIONAL_WORDS = {
    'secret', 'shocking', 'bombshell', 'conspiracy', 'miracle', 'hidden', 'truth',
    'exposed', 'unbelievable', 'hoax', 'banned', 'urgent', 'proof', 'censored',
    'disaster', 'furious', 'panic', 'leaked', 'bizarre', 'nightmare', 'terrifying',
    'scandal', 'mindblowing', 'classified', 'rigged', 'illegal'
}

SPECULATIVE_WORDS = {
    'claims', 'claimed', 'allegedly', 'rumors', 'reportedly', 'sources', 'suggests',
    'might', 'could', 'unconfirmed', 'purported', 'speculation', 'supposedly'
}

OBJECTIVE_JOURNALISTIC_WORDS = {
    'announced', 'reported', 'statement', 'official', 'department', 'spokesperson',
    'confirmed', 'agency', 'council', 'court', 'ruled', 'published', 'reuters',
    'conference', 'signed', 'agreed', 'scheduled', 'federal', 'commission'
}

SOURCE_WATERMARK_REGEX = re.compile(
    r'(\s*[-–—|]\s*(the\s+)?(new york times|breitbart|reuters|associated press|ap|cnn|fox news|washington post|bbc|guardian|bloomberg|politico|wsj|nbc|abc news)[a-zA-Z\s]*$)|(^(reuters|associated press|ap|cnn|fox news)\s*[-:]\s*)',
    re.IGNORECASE
)

def strip_publisher_watermarks(text):
    """Strips publisher and outlet markers to enforce pure stylometric language analysis."""
    cleaned = SOURCE_WATERMARK_REGEX.sub('', text).strip()
    return cleaned if cleaned else text

def analyze_news(news_text, pure_language_mode=False):
    """
    Explainable AI (XAI) and Stylometric Language Pattern Engine:
    1. Beyond Blacklists: Pure language stylometry (source watermark stripping).
    2. Intuitive Indications: Sensationalism radar, speculative framing, formality.
    3. Mathematical Attribution: TF-IDF feature attribution with directional weights.
    4. Calibrated Probabilities: Dual-spectrum confidence estimation.
    """
    if not news_text or not news_text.strip():
        return None

    raw_input = news_text.strip()
    source_watermark_found = bool(SOURCE_WATERMARK_REGEX.search(raw_input))
    
    # Process text based on mode
    working_text = strip_publisher_watermarks(raw_input) if pure_language_mode else raw_input

    raw_tokens = working_text.split()
    review = re.sub(r'[^a-zA-Z\s]', ' ', working_text)
    review_lower = review.lower()
    tokenized = nltk.word_tokenize(review_lower)

    lemmatized_tokens = []
    filtered_pairs = []
    for word in tokenized:
        if word not in stpwrds and len(word) > 1:
            lemma = lemmatizer.lemmatize(word)
            lemmatized_tokens.append(lemma)
            filtered_pairs.append((word, lemma))

    cleaned_str = ' '.join(lemmatized_tokens)
    vectorized_input = vector.transform([cleaned_str])

    # Raw classification & hyperplane distance
    decision_score = float(loaded_model.decision_function(vectorized_input)[0])
    raw_pred = int(loaded_model.predict(vectorized_input)[0])
    is_fake = (raw_pred == 1)

    # Sigmoid calibration: P(Fake)
    clipped_score = max(min(decision_score, 12.0), -12.0)
    prob_fake = 1.0 / (1.0 + np.exp(-clipped_score))
    prob_real = 1.0 - prob_fake

    fake_pct = round(prob_fake * 100, 1)
    real_pct = round(prob_real * 100, 1)

    # Word-level attribution computation
    lemma_impact_map = {}
    contributions = []

    for word, lemma in filtered_pairs:
        if lemma in vocab:
            idx = vocab[lemma]
            tfidf_val = float(vectorized_input[0, idx])
            weight_val = float(coefs[idx])
            impact = tfidf_val * weight_val

            lemma_impact_map[lemma] = {
                'word': word,
                'lemma': lemma,
                'impact': impact,
                'weight': weight_val,
                'tfidf': tfidf_val
            }

            contributions.append({
                'word': word,
                'lemma': lemma,
                'impact': round(impact, 4),
                'direction': 'fake' if impact > 0 else 'real',
                'weight': round(weight_val, 4),
                'tfidf': round(tfidf_val, 4)
            })

    # Deduplicate for feature bar chart
    dedup = {}
    for c in contributions:
        l = c['lemma']
        if l not in dedup or abs(c['impact']) > abs(dedup[l]['impact']):
            dedup[l] = c

    sorted_words = sorted(dedup.values(), key=lambda x: abs(x['impact']), reverse=True)
    max_impact = max([abs(x['impact']) for x in sorted_words], default=1.0)
    if max_impact == 0:
        max_impact = 1.0

    for item in sorted_words:
        item['relative_pct'] = min(round((abs(item['impact']) / max_impact) * 100, 1), 100.0)

    top_influential_words = sorted_words[:8]

    # Annotate tokens for visual highlighting
    annotated_words = []
    for raw_token in raw_tokens:
        clean_word = re.sub(r'[^a-zA-Z]', '', raw_token).lower()
        lemma = lemmatizer.lemmatize(clean_word) if clean_word else ''

        if lemma and lemma in lemma_impact_map:
            imp = lemma_impact_map[lemma]['impact']
            direction = 'fake' if imp > 0.005 else ('real' if imp < -0.005 else 'neutral')
            annotated_words.append({
                'token': raw_token,
                'clean': clean_word,
                'direction': direction,
                'impact': round(imp, 4),
                'weight': round(lemma_impact_map[lemma]['weight'], 3)
            })
        else:
            annotated_words.append({
                'token': raw_token,
                'clean': clean_word,
                'direction': 'neutral',
                'impact': 0.0,
                'weight': 0.0
            })

    # --- INTUITIVE INDICATIONS OF REAL & FAKE NEWS ---
    letters = [c for c in working_text if c.isalpha()]
    caps_count = sum(1 for c in letters if c.isupper())
    caps_ratio = round((caps_count / len(letters) * 100), 1) if letters else 0.0

    exclamations = working_text.count('!')
    questions = working_text.count('?')

    # Sensationalism & Clickbait Lexicon Triggers Detected
    detected_sensational = [w for w in tokenized if w in SENSATIONAL_WORDS or lemmatizer.lemmatize(w) in SENSATIONAL_WORDS]
    detected_speculative = [w for w in tokenized if w in SPECULATIVE_WORDS or lemmatizer.lemmatize(w) in SPECULATIVE_WORDS]
    detected_objective = [w for w in tokenized if w in OBJECTIVE_JOURNALISTIC_WORDS or lemmatizer.lemmatize(w) in OBJECTIVE_JOURNALISTIC_WORDS]

    sensational_score = len(detected_sensational) * 25 + (20 if caps_ratio > 20 else 0) + (15 if exclamations > 0 else 0)
    sensational_score = min(sensational_score, 100)

    if sensational_score >= 50 or caps_ratio > 30:
        sensationalism_level = "High Sensationalism / Urgency"
        sensationalism_badge = "bg-rose-500/20 text-rose-300 border-rose-500/30"
    elif sensational_score >= 20 or caps_ratio > 12:
        sensationalism_level = "Moderate Subjectivity"
        sensationalism_badge = "bg-amber-500/20 text-amber-300 border-amber-500/30"
    else:
        sensationalism_level = "Formal / Measured Journalism"
        sensationalism_badge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"

    # Tone categorization
    if len(detected_sensational) > 0 and len(detected_objective) == 0:
        tone_description = "Emotionally Charged / Clickbait Rhetoric"
        tone_color = "text-rose-400"
    elif len(detected_objective) > 0 and len(detected_sensational) == 0:
        tone_description = "Neutral Institutional Reporting"
        tone_color = "text-emerald-400"
    elif len(detected_speculative) > 0:
        tone_description = "Speculative / Hearsay Framing"
        tone_color = "text-amber-400"
    else:
        tone_description = "Standard Discursive Style"
        tone_color = "text-slate-300"

    # Risk level assessment
    if is_fake:
        if fake_pct >= 75:
            risk_tier = "High Misinformation Risk"
            risk_color = "text-rose-400"
        else:
            risk_tier = "Moderate Suspicion"
            risk_color = "text-amber-400"
    else:
        if real_pct >= 75:
            risk_tier = "High Credibility"
            risk_color = "text-emerald-400"
        else:
            risk_tier = "Moderate Credibility"
            risk_color = "text-teal-400"

    return {
        'headline': raw_input,
        'working_text': working_text,
        'pure_language_mode': pure_language_mode,
        'source_watermark_found': source_watermark_found,
        'is_fake': is_fake,
        'verdict_title': 'Looking Fake News 📰' if is_fake else 'Looking Real News 📰',
        'verdict_subtitle': 'FLAGGED AS UNRELIABLE CONTENT' if is_fake else 'VERIFIED AS RELIABLE REPORTING',
        'verdict_badge': 'FAKE NEWS DETECTED' if is_fake else 'AUTHENTIC NEWS DETECTED',
        'verdict_color': 'rose' if is_fake else 'emerald',
        'decision_score': round(decision_score, 3),
        'fake_pct': fake_pct,
        'real_pct': real_pct,
        'confidence': fake_pct if is_fake else real_pct,
        'annotated_words': annotated_words,
        'top_words': top_influential_words,
        'caps_ratio': caps_ratio,
        'exclamations': exclamations,
        'questions': questions,
        'word_count': len(raw_tokens),
        'vocab_tokens': len(lemmatized_tokens),
        'sensational_score': sensational_score,
        'sensationalism_level': sensationalism_level,
        'sensationalism_badge': sensationalism_badge,
        'detected_sensational': list(set(detected_sensational)),
        'detected_speculative': list(set(detected_speculative)),
        'detected_objective': list(set(detected_objective)),
        'tone_description': tone_description,
        'tone_color': tone_color,
        'risk_tier': risk_tier,
        'risk_color': risk_color
    }

@app.route('/')
def home():
    return render_template('index.html', experiments=experiments_data)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    news = ""
    pure_language_mode = False

    if request.method == 'POST':
        news = request.form.get('news', '').strip()
        pure_language_mode = request.form.get('pure_language_mode') == '1'
    elif request.method == 'GET':
        news = request.args.get('news', '').strip()
        pure_language_mode = request.args.get('pure_language_mode') == '1'

    if news:
        analysis = analyze_news(news, pure_language_mode=pure_language_mode)
        prediction_text = f"Prediction of the News : {analysis['verdict_title']}"
        return render_template(
            'prediction.html',
            news=news,
            analysis=analysis,
            pure_language_mode=pure_language_mode,
            prediction_text=prediction_text,
            experiments=experiments_data
        )
    return render_template(
        'prediction.html',
        news="",
        analysis=None,
        pure_language_mode=pure_language_mode,
        prediction_text="",
        experiments=experiments_data
    )

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('Images', filename)

@app.route('/api/experiments', methods=['GET'])
def api_experiments():
    return jsonify(experiments_data)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json(silent=True) or request.form
    news = data.get('news', '').strip()
    pure_mode = bool(data.get('pure_language_mode', False))
    if not news:
        return jsonify({'error': 'News text is required'}), 400
    analysis = analyze_news(news, pure_language_mode=pure_mode)
    return jsonify(analysis)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(debug=True, port=port)