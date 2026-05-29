# Classical POS Tagging And Morphology For UD Ukrainian-IU

This project builds a classical NLP pipeline for Ukrainian POS tagging and optional joint morphology tagging on the Universal Dependencies `UD Ukrainian-IU` treebank.

## Scope

- Main task: `UPOS` sequence labeling
- Extension: joint `UPOS + FEATS` sequence labeling
- Input: raw Ukrainian sentence
- Output: token-level JSON with predicted tags

## Project Layout

- `data/raw/` - original `.conllu` files
- `data/processed/` - converted `JSONL` and `CSV`
- `docs/` - dataset card, project plan, error-analysis template
- `models/` - serialized baseline and CRF models
- `notebooks/` - EDA notebook
- `outputs/` - metrics, confusion matrix, error cases
- `src/` - pipeline code

## Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## End-To-End Run

1. Download the official data:

```powershell
python -m src.load_data
```

2. Convert `CoNLL-U` to `JSONL/CSV`:

```powershell
python -m src.preprocess
```

3. Train baselines:

```powershell
python -m src.train_baselines --label-field upos
```

4. Train CRF:

```powershell
python -m src.train_crf --label-field upos
```

5. Run inference:

```powershell
python -m src.predict --model-path models/crf_upos.pkl --text "Ми читаємо українські тексти."
```

6. Validate JSON output:

```powershell
python -m src.predict --model-path models/crf_upos.pkl --text "Ми читаємо українські тексти." > outputs/prediction.json
python -m src.validate_output --input-json outputs/prediction.json
```

7. Run regression pack (20 deterministic cases):

```powershell
python tests/run_regression.py --model-path models/crf_upos.pkl
```

8. Run full pipeline with tracing:

```powershell
python -m src.run_pipeline --label-field upos
```

## Notes

- The project uses the official train/dev/test split from the treebank.
- `lemma` is stored in processed data but is **not** used as a training feature. Using gold lemmas as CRF features would leak annotation unavailable at inference time.
- For the extension task, pass `--label-field joint` to train a joint label of `UPOS||FEATS`.
- `src.predict` supports fallback to a baseline model if CRF inference fails:
  - `python -m src.predict --model-path models/crf_upos.pkl --fallback-model-path models/baseline_lexicon_upos.pkl --text "..."`
