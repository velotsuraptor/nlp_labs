# Lab 13 audit summary

- Use case: support extraction crew for Ukrainian admin/service messages.
- Agents: Triager, Extractor, Reviewer, RepairFallback.
- Test cases: 12
- Valid final output rate: 0.833
- Reviewer catch rate: 1.000
- Fallback activation rate: 0.500
- Fallback success rate: 0.667
- Manual review rate: 0.167
- Baseline schema-valid rate: 0.833
- Crew schema-valid rate: 1.000
- Best examples: case_001_simple_compensation, case_007_passport_queue, case_012_location_specific.
- Problem cases: case_003_ambiguous_service, case_005_hallucination_prone, case_010_manual_review_conflict.
- Next fix: better ambiguity handling for multi-service inputs and less aggressive service guessing.
