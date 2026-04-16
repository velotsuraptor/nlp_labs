# Embedding notes — Lab9

## 1. Corpus

- Source: processed `text` field from `processed_v2`
- Documents: 1000
- Approx tokens after tokenization: 22030

## 2. Models

- Word2Vec
- FastText

## 3. Parameters

- vector_size=100, window=5, min_count=3, sg=1, epochs=20, seed=42, workers=1

## 4. Ten nearest-neighbor probe words

- університет [frequent/domain]
  W2V: університету (0.933), імені (0.923), площі (0.920), ринок (0.918), національний (0.918), архітектура (0.913), ратуша (0.913), чернівецький (0.909)
  FT: університету (0.998), університетів (0.994), університеті (0.993), чернівецький (0.948), міста (0.944), будівлі (0.940), міська (0.935), площі (0.934)
  Useful: useful; Comment: FastText groups morphology better; Word2Vec is also coherent on frequent forms.
- євідновлення [domain]
  W2V: майно (0.973), заяву (0.972), подати (0.972), пошкоджене (0.971), застосунку (0.969), дія (0.960), заяви (0.959), виплату (0.957)
  FT: відновлення (0.997), оновлення (0.993), пошкоджене (0.992), дія (0.992), заяви (0.991), пошкодження (0.990), пошкодженого (0.989), заявку (0.989)
  Useful: useful; Comment: Both models catch the program context; FastText adds cleaner morphological neighbors.
- паспорт [domain]
  W2V: прийняли (0.943), документи (0.939), без (0.937), тижні (0.933), слів (0.928), роблять (0.924), закордонний (0.923), сьогодні (0.923)
  FT: паспорта (0.987), паспорти (0.985), документ (0.984), документи (0.979), документів (0.979), зрозуміла (0.975), працівників (0.974), прийшов (0.973)
  Useful: partly; Comment: Domain signal is present, but Word2Vec pulls some noisy context words.
- дія [domain/morph-sensitive]
  W2V: пошкоджене (0.977), застосунку (0.977), майно (0.977), заяви (0.971), подати (0.967), радимо (0.966), подання (0.963), виплату (0.961)
  FT: заяви (0.996), пошкоджене (0.994), заяву (0.993), пошкодження (0.992), євідновлення (0.992), заявку (0.991), оновлення (0.989), компенсація (0.989)
  Useful: useful; Comment: Both models stay in the e-service / damaged-property context, with cleaner FastText neighborhoods.
- ремонт [domain]
  W2V: пошкодженого (0.947), отримати (0.937), окрім (0.934), програмою (0.931), квартири (0.925), витяг (0.921), програми (0.916), карти (0.916)
  FT: ремонту (0.990), податків (0.984), подавав (0.971), пошту (0.971), квартири (0.969), квартир (0.968), податкова (0.967), пост (0.962)
  Useful: partly; Comment: Neighbors are only partly useful; the term drifts toward adjacent administrative or housing context.
- ратуша [rare/domain]
  W2V: ринок (0.978), площі (0.977), зали (0.974), самому (0.974), університету (0.972), відвідування (0.969), архітектура (0.969), територія (0.968)
  FT: верх (0.996), ратуші (0.996), вершини (0.994), вершину (0.993), вежа (0.992), львів (0.992), вежі (0.991), ратушу (0.990)
  Useful: useful; Comment: FastText is clearly better on morphology and landmark-specific neighbors.
- черга [morph-variant]
  W2V: черзі (0.964), очікування (0.954), години (0.952), прийшов (0.950), сидять (0.949), близько (0.948), взагалі (0.947), чергу (0.947)
  FT: чергу (0.995), черзі (0.991), черги (0.980), чекав (0.979), взагалі (0.978), чекаю (0.966), норм (0.959), терміни (0.959)
  Useful: partly; Comment: Both models see the queue/waiting concept, while FastText captures inflected variants better.
- реєстрація [rare]
  W2V: пенсійного (0.994), знайти (0.992), додати (0.992), проводяться (0.992), приходити (0.992), шанс (0.992), жахливий (0.992), мої (0.992)
  FT: нотаріуса (0.992), нотаріуси (0.990), запис (0.989), реєстрації (0.989), заздалегідь (0.989), службу (0.988), результати (0.988), поліції (0.987)
  Useful: weak; Comment: Word2Vec is unstable for this rare word; FastText is better but still not reliably semantic.
- phone [noisy/latin]
  W2V: рр (0.875), резиденція (0.842), зв'язку (0.823), україні (0.823), програма (0.821), чернівців (0.817), митрополитів (0.808), університетів (0.800)
  FT: рр (0.919), будинку (0.907), резиденція (0.907), митрополитів (0.905), м (0.897), програмування (0.896), захисту (0.895), захист (0.893)
  Useful: weak; Comment: Latin/noisy token gives weak or accidental neighbors in both models.
- oкyпації [noisy/mixed-script]
  W2V: [oov]
  FT: щодо (0.988), завдання (0.978), спілкування (0.977), результат (0.976), рішення (0.976), надані (0.974), дякуємо (0.974), далмації (0.972)
  Useful: weak; Comment: Word2Vec is OOV; FastText can compose a vector but the neighbors are not practically useful.

## 5. Five domain terms

- євідновлення
  W2V: майно (0.973), заяву (0.972), подати (0.972), пошкоджене (0.971), застосунку (0.969), дія (0.960), заяви (0.959), виплату (0.957)
  FT: відновлення (0.997), оновлення (0.993), пошкоджене (0.992), дія (0.992), заяви (0.991), пошкодження (0.990), пошкодженого (0.989), заявку (0.989)
  Judgement: FastText is slightly better: both are useful, but FastText keeps more morphological/domain variants together.
- дія
  W2V: пошкоджене (0.977), застосунку (0.977), майно (0.977), заяви (0.971), подати (0.967), радимо (0.966), подання (0.963), виплату (0.961)
  FT: заяви (0.996), пошкоджене (0.994), заяву (0.993), пошкодження (0.992), євідновлення (0.992), заявку (0.991), оновлення (0.989), компенсація (0.989)
  Judgement: FastText is better because it stays closer to applications, claims, and damaged-property processing vocabulary.
- паспорт
  W2V: прийняли (0.943), документи (0.939), без (0.937), тижні (0.933), слів (0.928), роблять (0.924), закордонний (0.923), сьогодні (0.923)
  FT: паспорта (0.987), паспорти (0.985), документ (0.984), документи (0.979), документів (0.979), зрозуміла (0.975), працівників (0.974), прийшов (0.973)
  Judgement: FastText is better on morphology; Word2Vec is noisier but still domain-related.
- ремонт
  W2V: пошкодженого (0.947), отримати (0.937), окрім (0.934), програмою (0.931), квартири (0.925), витяг (0.921), програми (0.916), карти (0.916)
  FT: ремонту (0.990), податків (0.984), подавав (0.971), пошту (0.971), квартири (0.969), квартир (0.968), податкова (0.967), пост (0.962)
  Judgement: Both are only partly useful; the corpus is too mixed for a stable repair-specific neighborhood.
- ратуша
  W2V: ринок (0.978), площі (0.977), зали (0.974), самому (0.974), університету (0.972), відвідування (0.969), архітектура (0.969), територія (0.968)
  FT: верх (0.996), ратуші (0.996), вершини (0.994), вершину (0.993), вежа (0.992), львів (0.992), вежі (0.991), ратушу (0.990)
  Judgement: FastText is clearly better because subword information helps align ратуша / ратуші / ратушу / вежа.

## 6. Five useful / not useful cases

- євідновлення: useful
  W2V: майно (0.973), заяву (0.972), подати (0.972), пошкоджене (0.971), застосунку (0.969), дія (0.960), заяви (0.959), виплату (0.957)
  FT: відновлення (0.997), оновлення (0.993), пошкоджене (0.992), дія (0.992), заяви (0.991), пошкодження (0.990), пошкодженого (0.989), заявку (0.989)
  Rationale: Useful: both models recover domain neighbors; FastText is cleaner on morphology and related administrative forms.
- ратуша: useful
  W2V: ринок (0.978), площі (0.977), зали (0.974), самому (0.974), університету (0.972), відвідування (0.969), архітектура (0.969), територія (0.968)
  FT: верх (0.996), ратуші (0.996), вершини (0.994), вершину (0.993), вежа (0.992), львів (0.992), вежі (0.991), ратушу (0.990)
  Rationale: Useful: the landmark neighborhood is concrete, and FastText strongly benefits from inflected forms and subwords.
- черга: partly
  W2V: черзі (0.964), очікування (0.954), години (0.952), прийшов (0.950), сидять (0.949), близько (0.948), взагалі (0.947), чергу (0.947)
  FT: чергу (0.995), черзі (0.991), черги (0.980), чекав (0.979), взагалі (0.978), чекаю (0.966), норм (0.959), терміни (0.959)
  Rationale: Partly useful: the queue/waiting concept is visible, but some neighbors remain generic rather than task-specific.
- реєстрація: weak
  W2V: пенсійного (0.994), знайти (0.992), додати (0.992), проводяться (0.992), приходити (0.992), шанс (0.992), жахливий (0.992), мої (0.992)
  FT: нотаріуса (0.992), нотаріуси (0.990), запис (0.989), реєстрації (0.989), заздалегідь (0.989), службу (0.988), результати (0.988), поліції (0.987)
  Rationale: Weak: the word is rare, so Word2Vec is unstable and FastText only partly rescues it.
- oкyпації: weak
  W2V: [oov]
  FT: щодо (0.988), завдання (0.978), спілкування (0.977), результат (0.976), рішення (0.976), надані (0.974), дякуємо (0.974), далмації (0.972)
  Rationale: Weak: this noisy mixed-script form is OOV for Word2Vec and only weakly recoverable in FastText.

## 7. Word2Vec vs FastText

For this corpus, FastText is the better default embedding model. On frequent stable words like університет, both models are already useful, but FastText groups inflected forms more consistently. On domain terms such as євідновлення, дія, and ратуша, FastText keeps a cleaner neighborhood and handles morphology more naturally. The biggest difference appears on rare or noisy forms: Word2Vec fails on OOV-like words such as oкyпації, while FastText can still build a subword-based vector. That said, FastText does not magically solve corpus noise: for phone and реєстрація the neighbors are still weak or mixed. So embeddings are useful here mainly for vocabulary exploration and domain-term inspection, not as a guaranteed strong semantic resource on every rare token.

## 8. Main conclusion

FastText is the more useful embedding model for this corpus because it handles morphology and noisy tokens better, although both models remain limited by corpus size and domain heterogeneity.