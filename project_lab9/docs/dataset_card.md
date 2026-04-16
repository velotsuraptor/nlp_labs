# Dataset card — Lab9

## Embeddings readiness
- Corpus used: `processed_v2` original word forms.
- Size for embeddings: 1000 documents and about 22030 tokens after light tokenization.
- Domain vocabulary is present (`євідновлення`, `дія`, `паспорт`, `ремонт`, `ратуша`), but the corpus is still mixed across several subdomains.
- Noisy text exists: mixed-script tokens, Latin tokens, spelling variation, and short low-context texts.
- FastText looks more appropriate than Word2Vec for this corpus because morphology and subword composition matter in Ukrainian and in noisy user text.
- Embeddings provide a useful exploratory signal, especially for domain terms, but are not uniformly strong on rare or noisy words.
