# Linguistic Stylometry & Explainable AI (XAI) Attribution

## 1. Linear Feature Attribution ($w_i \cdot x_i$)
Because the decision boundary is strictly linear in the TF-IDF space:
$$d = \sum_{i=1}^V w_i x_i + b$$
Each individual word $i$ present in the document possesses an exact directional contribution:
$$\phi_i = w_i \cdot x_i$$

- **Positive Impact ($\phi_i > 0$)**: Pushes headline toward FAKE.
- **Negative Impact ($\phi_i < 0$)**: Anchors headline toward REAL.
- **Zero Impact ($\phi_i = 0$)**: Neutral filler or stopword.

## 2. Stylometric Signal Radars
1. **Sensationalism Index (0-100)**: Evaluates urgent clickbait vocabulary (`shocking`, `miracle`, `hoax`, `banned`, `conspiracy`, `scandal`).
2. **Speculative Framing**: Detects hearsay markers (`claims`, `allegedly`, `rumors`, `reportedly`, `sources suggest`).
3. **Formatting Hysteria**: Calculates percentage of uppercase characters (`% CAPS`), exclamation counts (`!`), and question marks (`?`).
4. **Information Density**: Compares word count to lemmatized vocabulary tokens.
