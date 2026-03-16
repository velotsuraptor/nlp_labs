# Dataset Card — Lab2 update

## Source & task
- Base dataset: UAReviews subset from Lab1 (N=1000, 5 balanced classes).
- Task: Track A text classification.

## Preprocessing (Lab2)
- whitespace/NBSP normalization; apostrophes/quotes/dashes canonicalization
- masking: <URL>, <EMAIL>, <PHONE>
- robust sentence split with UA abbreviation and decimal protection

## Before vs After snapshot
- char_mean: 152.615 -> 151.803
- word_mean: 22.509 -> 22.503
- short_lt5_pct: 0.200% -> 0.200%
- dup_pct: 0.400% -> 0.400%

## Masking totals
- URL replacements: 12
- EMAIL replacements: 1
- PHONE replacements: 11

## Risks
- semantic noise and slang remain in text (by design)
- near-duplicates and domain shift are still possible
