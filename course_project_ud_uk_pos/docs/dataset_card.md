# Dataset Card: UD Ukrainian-IU

## Source

- Dataset: Universal Dependencies `UD Ukrainian-IU`
- Official page: <https://universaldependencies.org/treebanks/uk_iu/index.html>
- Repository: <https://github.com/UniversalDependencies/UD_Ukrainian-IU>

## Task Fit

This corpus is appropriate for sequence labeling because each token has gold `UPOS`, `XPOS`, and morphological `FEATS`. It supports both a clean POS-tagging task and an extended joint morphology task.

## Language

- Ukrainian

## Format

- Original format: `CoNLL-U`
- Derived formats in this project:
  - sentence-level `JSONL`
  - token-level `CSV`

## Official Split

- Train: 5496 sentences
- Dev: 672 sentences
- Test: 892 sentences

## Approximate Size

- About 122K tokens
- About 7060 sentences

## Labels

- `UPOS`
- `XPOS`
- `FEATS`
- `LEMMA`

## Preprocessing Decisions

- Preserve the official split
- Skip comment lines in model inputs
- Skip multiword-token header rows and empty nodes when constructing token-level sequence labels
- Preserve `lemma`, `xpos`, and `feats` in processed exports for analysis
- Keep `text` and `sentence_id` for traceability

## Challenging Cases To Analyze

- Ambiguous function words
- Named entities and proper nouns
- Numerals
- Hyphenated forms
- Apostrophe variants
- Rare tag combinations
- Out-of-vocabulary tokens

## Privacy / Data Sensitivity

The treebank is a public linguistic resource. Still, demo materials should avoid copying long raw text fragments unnecessarily and should not foreground metadata fields like source or author when sharing examples.

