# Overnight BF16 Qwen3-14B argument experiment

Observed UTC: 2026-11-10T12:01:38.469453+00:00
Job: complete; stage: tuned-herald

Both English and Lean proof bodies are inputs. No quantization or second-pass training.
ProofNet positives are user-assumed; training swaps are a coarse proof-consistency pilot.
The separate core crosses two valid routes for each theorem, with a formal-proof-masked control.
Core material is constructed and is not independently human reviewed.

| Model / corpus | Status | Rows | Accuracy |
| --- | --- | ---: | ---: |
| untuned-validation | complete | 118 | 81.36% |
| tuned-validation | complete | 118 | 100.00% |
| untuned-core | complete | 16 | 93.75% |
| tuned-core | complete | 16 | 50.00% |
| untuned-core-masked | complete | 16 | 50.00% |
| tuned-core-masked | complete | 16 | 50.00% |
| untuned-herald | complete | 44553 | unlabeled |
| tuned-herald | complete | 44553 | unlabeled |

No Herald accuracy claim is possible without independent labels.
Cross-problem pilot accuracy alone does not demonstrate proof-route matching.
Compilation is distinct from independent semantic argument validation.
