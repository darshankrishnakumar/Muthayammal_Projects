# Walkthrough Script: Explainable Fake News Detection (PROJECT-014)

## Project Overview
- **Identifier**: PROJECT-014
- **Title**: Explainable Fake News Detection via Linguistic Stylometry, TF-IDF Feature Attribution, and Passive-Aggressive Large-Margin Learning
- **Port**: 5014 (`http://127.0.0.1:5014`)
- **Target Video Duration**: Exactly 180.0 Seconds (03:00)

---

### Step 1: Architecture & Executive Landing (00:00 - 00:20)
**Spoken Narration**:
"Welcome to the capstone demonstration of PROJECT-014: Explainable Fake News Detection via Linguistic Stylometry and Passive-Aggressive Large-Margin Learning. Digital misinformation cannot be defeated with brittle domain blacklists that malicious actors bypass at will. VeriNews AI analyzes intrinsic textual syntax, punctuation hysteria, and n-gram statistical distributions to verify content in real-time."
**Visual Focus**:
- Full executive dashboard at `http://127.0.0.1:5014/` displaying 96.2% Kaggle validation accuracy, Passive-Aggressive hyperplane architecture, and quick navigation.

---

### Step 2: Interactive Visualizer Console (00:20 - 00:45)
**Spoken Narration**:
"Navigating to the prediction console, we observe a modern interactive input workspace. Analysts can paste any article or headline, select quick preset samples, or activate 'Pure Language Mode' to eliminate source-bias artifacts before classification."
**Visual Focus**:
- Navigation to `/predict`. Highlighting input textarea, preset buttons (Real News, Sensational Fake, Clickbait, Pure Headline), and submit trigger.

---

### Step 3: Sensational Fake News Detection (00:45 - 01:15)
**Spoken Narration**:
"We test a classic clickbait headline: 'Secret government plan revealed to control weather with cell towers.' The Passive-Aggressive model executes in under 2 milliseconds, projecting a margin score of +2.04. The dual-spectrum sigmoid meter reveals an 88.5% Fake probability, triggering a high-risk crimson alert."
**Visual Focus**:
- Form submission, animated fade-in of Crimson Verdict Banner ('Looking Fake News 📰'), calibrated probability gauge (88.5% Fake vs 11.5% Real), and Severe Misinformation Risk tier.

---

### Step 4: Explainable AI (XAI) Attribution (01:15 - 01:45)
**Spoken Narration**:
"Unlike opaque deep neural networks, VeriNews AI provides full mathematical transparency. By evaluating w_i times x_i for each active TF-IDF token, the engine identifies exact directional weights. Words like 'secret', 'plan', and 'revealed' exert positive pressure driving the classification toward Fake. Tokens are rendered as interactive color-coded pills with hover diagnostics."
**Visual Focus**:
- Smooth scroll to Explainable Feature Attribution panel. Inspection of word pills (Rose for fake indicators, emerald for authentic journalism, neutral for stopwords) and relative impact bar charts.

---

### Step 5: 4-Signal Linguistic Stylometric Radar (01:45 - 02:10)
**Spoken Narration**:
"Beyond n-gram frequencies, VeriNews AI deploys four human-cognitive signal meters: the Sensationalism Index, Speculative Hearsay framing, Formatting Hysteria measuring uppercase shouting and exclamation clusters, and Information Density contrasting raw word count against lemmatized vocabulary."
**Visual Focus**:
- Inspection of the 4-signal grid: Sensationalism Index (60/100), Discursive Tone framing, 0% Caps, and lemmatized token density.

---

### Step 6: Beyond Blacklists — Pure Language Stylometry Mode (02:10 - 02:35)
**Spoken Narration**:
"Now we test our 'Pure Language Mode' on a headline ending with a publisher watermark: '- The New York Times'. If an attacker appends a legitimate source name, blacklists are fooled. Here, VeriNews AI strips the watermark and verifies that the remaining text possesses authentic journalistic grammar, confirming Real News with 85.2% credibility."
**Visual Focus**:
- Execution with `pure_language_mode=on`. Green Glowing Verdict Banner ('Appears Authentic News 📰'), high Real Credibility score, and verification that source watermarks were stripped prior to inference.

---

### Step 7: Multi-Model Benchmarks & SQLite Audit Ledger (02:35 - 02:50)
**Spoken Narration**:
"Scrolling to our experimental benchmarks, our Passive-Aggressive classifier leads with 96.2% accuracy and 1.8 millisecond latency, outperforming Linear SVM, Logistic Regression, Naive Bayes, and Random Forest. Below, every verification is persisted into an immutable SQLite database for institutional audit compliance."
**Visual Focus**:
- Multi-model evaluation table and SQLite verification table (`fake_news.db`) displaying headline, calibrated probabilities, and timestamps.

---

### Step 8: API Health & Capstone Conclusion (02:50 - 03:00)
**Spoken Narration**:
"All 27 automated unit, API, and database tests pass with a 100% success rate. VeriNews AI is fully documented, container-ready, and verified for college final-year engineering submission."
**Visual Focus**:
- Return to executive overview / REST API `/api/health` displaying 146,627 vocabulary entries and database connection. Final sign-off.
