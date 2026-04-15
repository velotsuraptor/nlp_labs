# Dataset card — Lab8

## Corpus snapshot
- Source corpus: cleaned `processed_v2` from Lab2.
- Documents before filtering: 1000.
- Documents after topic-model filtering: 988.
- Filtering rule: keep documents with at least 4 cleaned tokens after stop-word and template-noise removal.

## Topic modeling findings
- Strong recurring themes: `єВідновлення / Дія`, `освітні заклади / викладачі`, `ратуша / вид на місто`.
- The corpus is mixed rather than homogeneous: it blends service reviews, university/academy reviews, tourism/location comments, and civic / war-support posts.
- Some noisy or template-style documents remain, especially short recommendation posts and generic service complaints.
- Topic modeling is useful for exploratory analysis here, but not strong enough on its own for stable domain segmentation.

## Remaining risks
- Mixed domains in one corpus create blended topics.
- Short texts still produce generic themes.
- Template phrases and service vocabulary can dominate weaker topics.
- A lemma-based representation may shift topic boundaries.
