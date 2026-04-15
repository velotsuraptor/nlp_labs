# Audit summary — Lab8

1. Corpus size after filtering: 988 documents (from 1000 original rows).
2. Models tested: LSA (TF-IDF + TruncatedSVD) and LDA (CountVectorizer + LatentDirichletAllocation).
3. Topic counts tested: k=5 and k=8 for both models.
4. Best themes: єВідновлення / документи / цифрові сервіси; Ратуша / вид на місто / туристична рекомендація; Освітні заклади / навчання / викладачі.
5. Worst themes: duplicate sightseeing/style topic; generic opinion/place topic; mixed war/service topic.
6. What damaged the weak topics: template-style recommendation phrases, generic service vocabulary, and a mixed multi-domain corpus with many short documents.
7. Better model for this corpus: LDA, because its strongest topics stay more coherent at the document level.
8. Next steps: stronger stop-word filtering, domain-specific subcorpora, and optional lemma-based topic modeling.
