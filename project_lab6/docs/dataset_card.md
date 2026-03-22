# Dataset Card — Lab6 update

## Classification baseline
- Model: TF-IDF + Logistic Regression (2 baseline variants).
- Features: processed_v2 text, word n-grams (1,1) and (1,2).

## Main risks
- overlap класів та змішані наміри в одному тексті
- noisy labels / неоднозначність gold
- translit/slang та рідкісна лексика
- domain drift на нових джерелах
