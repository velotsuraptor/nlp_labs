# Dataset card update for Lab 12

- Tested agent use case: single-agent support extraction.
- Input types in test cases: simple requests, missing data, noisy text, ambiguous service mentions, relative dates, and amount-heavy payment cases.
- Tools used on these inputs: issue classification, structured field extraction, required-field validation.
- Noisy / ambiguous cases: yes, explicitly included in the evaluation set.
- Did tool grounding help: yes, especially for structure, ambiguity control, and final answers that cite extracted fields.
