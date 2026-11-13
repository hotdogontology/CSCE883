# OpenAI correspondence case shortlist

Selected 2026-11-13. User authorized the trained informalization pipeline only;
the direct untuned baseline is removed from this run. Execution artifacts:
`artifacts/openai-informalization-20261113`; runner:
`scripts/openai_informalization_cases.py`.

## Pinned sources

- Critique: [Bastounis, Circelli and Hansen, arXiv:2610.08144](https://arxiv.org/html/2610.08144), examples 3.1 and 3.3.
- English: [Finite time blowup for Navier–Stokes](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), 166 pages. Download SHA256: `0e779481c4da40bd28d1e642e1d8ca57447d129610df28dfa5a11e9af8ae228f`.
- Lean: `openai/NavierStokesAndEuler`, revision `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, the revision examined by the critique.
- Local ignored sources: `data/openai-correspondence-cases/`: manuscript, two Lean files and extracted English pages. Extracted PDF mathematics needs visual checking before becoming model input.

## Candidate 1: inverse estimate

English: Lemma 8.6, equation (8.19), page 95; corresponding Fourier-estimate argument begins on page 96. Select that subargument, not every claim in the lemma.

Lean: [`norm_derivativeWord_inverse_le`, lines 1059–1080](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L1059-L1080).

The downloaded English estimate requires m+4 derivatives; the inspected Lean declaration uses `w.length + 5`. Its proof invokes a coefficient estimate and a summability bound. This provides a compact first test of whether informalization preserves derivative requirements and explains the estimate actually proved.

Before inference, resolve the definitions of `derivativeWord`, `xJet`, `slice`, `inverse`, and the coefficient-bound helper. Do not present a detached theorem as the entire formal argument.

## Candidate 2: pressure-flux estimate (priority proof-body case)

English: the pressure portion of Lemma 10.5, pages 121–123, ending in equation (10.19) on page 123.

Lean: [`exists_uniform_actual_pressure_flux_bound`, lines 576–598](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L576-L598).

The inspected Lean bound includes `dissipationRoot`, whereas the displayed English pressure-flux bound is expressed in terms of B_R and R. The critique also identifies a different analytic route: the English Riesz estimate and the formal Sobolev/Riesz route use different spaces. This tests argument correspondence as well as the resulting bound.

Expand the wrapper's helpers, especially `exists_uniform_canonicalCutoffFlux_bound`, the pressure decomposition and relevant results in `R3/RieszTestOperators.lean`. Define cutoff norms and dissipation before comparison. A focused Riesz-estimate subcase may help localize failures, but belongs to this same case family, not an independent observation.

## Proposed evaluation

1. Freeze source excerpts, definitions, dependency context and token counts; do not silently truncate. Preserve original sources separately from normalized equation transcription.
2. Run trained Lean-to-English plus the existing untuned English judge. Keep the original English and critique out of the translator input; keep critique and expected labels out of the judge.
3. Inspect whether the generated English retains the relevant assumptions, quantities and proof steps before interpreting the judge decision. Record original-pair discrepancies, translator errors and judge errors separately.
4. Treat expected mismatches as literature-supported case annotations, not newly independently verified gold labels. Report caught/missed discrepancies and quotations from generated explanations; two selected mismatch families do not support general accuracy or specificity.
5. Add independently assessed faithful cases before claiming balanced performance. Nearby uncriticized lemmas are candidates, not automatically positive controls. Sign conventions and equivalent presentations must not be counted as semantic errors.

Prepared scoped English transcriptions with equations visually checked against
pages 95, 96, 122 and 123. Downloaded the pinned repository archive and selected
41 Lean declarations (definitions/helper bodies plus targets); this is not a
complete transitive dependency closure. Translation prompts: 2,563 and 8,396
tokens. No truncation. The translation output cap is 2,048 tokens, versus 1,024
in the Herald evaluation; both external inputs exceed the training total-token
cap of 2,048. Judge retains the original constrained YES/NO score; a separate,
unconditioned explanation request is recorded as diagnostic output and may
disagree with that score. No new Lean compilation or independent mathematical
verification has been performed.
