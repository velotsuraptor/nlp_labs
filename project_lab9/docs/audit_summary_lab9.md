# Audit summary — Lab9

1. Corpus: cleaned `processed_v2` from Lab2; 1000 documents and about 22030 tokens after light tokenization.
2. Models trained: Word2Vec and FastText with shared parameters (`vector_size=100`, `window=5`, `min_count=3`, `sg=1`, `epochs=20`, `seed=42`).
3. Strongest nearest-neighbor examples: євідновлення, ратуша, університет.
4. Weakest nearest-neighbor examples: реєстрація, phone, oкyпації.
5. Domain terms with meaningful neighborhoods: євідновлення, дія, ратуша, and partially паспорт.
6. Where FastText won: morphology, inflected forms, and OOV-like noisy words.
7. Where the gain was small: frequent stable words and mixed-context terms such as ремонт.
8. Final judgement: embeddings are useful here for vocabulary exploration and domain-term inspection; FastText is the better fit for this noisy mixed corpus.
