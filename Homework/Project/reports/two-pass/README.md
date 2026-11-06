# Two-pass experiment: latest observed results

Observed UTC: 2026-11-06T21:45:37.062842+00:00

Job: **running**; stage: `untuned-herald`.

Scope: statement correspondence, not proof-argument fidelity.

| Run | State | Records written | Labeled accuracy |
| --- | --- | ---: | ---: |
| first-pass-validation | complete | 112 | 70.54% |
| untuned-herald | running | 4784 | not available |
| untuned-validation | complete | 112 | 62.50% |

First-pass validation: 79/112 correct versus 70/112 untuned; mismatch detection
fell from 21/39 to 13/39. A higher YES rate alone is not improvement.

Herald labels are predictions, including agreement-only pseudo-labels. External NO
outputs are review leads; context, theorem scope and PDF formatting need review.

Full local outputs: `artifacts/two-pass/`. Data, logs, weights and credentials
are excluded from this published snapshot. See `../../two-pass-experiment.md`.
