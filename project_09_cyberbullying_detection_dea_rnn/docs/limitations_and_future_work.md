# Limitations and Future Work: PROJECT-009

## Current Limitations
1. **Unimodal Text Analysis**: Only analyzes plain text. Cannot inspect text embedded within images, memes, or attached video media.
2. **Monolingual English Scope**: Optimized primarily for English social discourse and transliterated slang.
3. **Fixed Context Window**: Max token sequence length of 40 tokens truncates long threads.

## Future Engineering Roadmap
1. **Multimodal OCR & Vision Transformers**: Integrate vision transformers (ViT) to detect toxicity in memes.
2. **Cross-Lingual Multilingual Transformers**: Incorporate Indic-BERT and XLM-RoBERTa for regional dialect coverage.
3. **Dynamic User Reputation Modeling**: Factor account creation date and past infractions into automated quarantine decisions.
