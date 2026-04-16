# LPNU NLP — Lab 09 (Word Embeddings: Word2Vec vs FastText)

1. Corpus: cleaned Ukrainian `processed_v2` comments/reviews using original word forms.
2. Models: Word2Vec and FastText with the same training parameters.
3. Parameters: `vector_size=100`, `window=5`, `min_count=3`, `sg=1`, `epochs=20`, `seed=42`.
4. Word types analyzed: frequent, rare, domain, morph-variant, noisy / Latin / mixed-script.
5. Most informative cases: `євідновлення`, `ратуша`, `черга`, `реєстрація`, `oкyпації`.
6. Where FastText was better: morphology, inflection, and OOV-like noisy variants.
7. Usefulness: embeddings are useful for vocabulary and domain-term analysis, with FastText as the better default on this corpus.
