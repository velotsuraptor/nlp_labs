# Dataset card

- Multi-agent use case tested: support extraction for admin/service messages.
- Test-case input types: simple, ambiguous, relative-date, noisy, hallucination-prone, fallback-required, manual-review cases.
- Expected error types: wrong route, missing field, hallucinated field, invalid JSON, unnecessary fallback, unresolved ambiguity.
- Fallback was needed mainly on noisy, hallucination-prone, and contradictory inputs.
- Multi-agent workflow improved controllability and logging over the single-agent baseline.
- It was excessive on trivial one-intent cases.
