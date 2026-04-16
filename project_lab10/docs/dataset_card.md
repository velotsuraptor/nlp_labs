# Dataset card — Lab10

## NER relevance
- Important entity types in this corpus: PERSON, ORG, LOC, DATE, MONEY, and domain entities such as `єВідновлення` and `Дія`.
- Standard Ukrainian NER baseline is not sufficient on its own: it catches some classic entities, but misses many domain and regular-pattern entities.
- The most problematic entities were domain-specific names plus DATE and MONEY mentions in noisy user text.
- Hybrid rules gave a clear gain in coverage and practical usefulness, especially for DATE, MONEY, and corpus-specific domain entities.
- Remaining issues: vocative person names, hotline-like numbers, and some baseline false positives from MISC / LOC spans.
