# LPNU NLP — Lab 08 (Topic Modeling: LSA vs LDA)

1. Corpus analyzed: cleaned Ukrainian review/comment corpus from `processed_v2`.
2. Models run: `LSA = TF-IDF + TruncatedSVD`, `LDA = CountVectorizer + LatentDirichletAllocation`.
3. Topic counts tested: `k=5` and `k=8` for both models.
4. Best themes: `єВідновлення / Дія`, `освітні заклади / навчання / викладачі`, `ратуша / вид на місто`.
5. Bad themes: duplicate LSA sightseeing/style topics and mixed LDA service-war topics.
6. LSA vs LDA: LDA produced more readable topics for this corpus because its top documents stayed more coherent.
7. Usefulness: topic modeling is helpful for corpus exploration, but the corpus should be split into narrower domains for cleaner topics.
