# Project TODO

Last updated: 2026-11-06. Current plan: [methodology.md](methodology.md).
Current context and session log: [SESSION_SUMMARY.md](SESSION_SUMMARY.md).

**Current direction:** authorized two-pass statement-fidelity experiment; see
`two-pass-experiment.md`. Manual Herald review is still deferred. First-pass LoRA
is complete; full Herald comparison and later stages are running sequentially.
Inspect `artifacts/two-pass/job.json` before launching any further GPU jobs.
For Monday, read `MONDAY_HANDOFF.md` and the newer generated aggregate snapshots
in `reports/two-pass/`; this static checklist may precede later job stages.

Unchecked tasks are outstanding, not evidence that work has begun. Human tasks
are judgment/coordination needs; agents should prepare concrete review material
and continue independent technical work rather than making the user do setup.

## HUMAN TODO

- [ ] Review an agent-prepared small pilot of side-by-side English/Lean pairs
  and provisional labels. Start with a few if useful; the suggested 30 is for
  rubric development, not the full evaluation set.
- [ ] Refine the argument-fidelity rubric: what routine elaboration, automation,
  reordering and proof compression count as the same essential argument?
- [ ] Review ambiguous or substantive labeling decisions and the sampled quality
  of weak training labels. Agree on a feasible, larger evaluation review budget.
- [ ] Identify subject areas the user or another qualified reviewer can assess;
  arrange independent second review of a subset if practical.
- [ ] Confirm course deliverables/deadline and prioritize optional experiments
  if available time cannot support all of them.
- [ ] For a large hosted AXLE job, obtain capacity guidance through its console
  or capacity form. No request to Axiom has been sent on the user's behalf.

Completed human actions:

- [x] Approved the required Windows C++ runtime installation.
- [x] Obtained an AXLE API key and saved it locally in ignored `.env`.

## AGENT TODO

### Active: first/second pass experiment

- [x] Prepare original/corrected ProofNet-V statement pairs and grouped split.
- [x] Train first-pass QLoRA and compare on 112 held-out pairs: 62.50% untuned,
  70.54% first pass, but mismatch recall falls from 21/39 to 13/39.
- [x] Implement agreement-only labels, fresh-base second-pass training and
  source-pinned external screening; three guard tests passed.
- [x] Start sequential background driver; full Herald comparison is in progress.
- [x] Add periodic long-training checkpoints, safe aggregate-report exporter and
  publishing watcher; nine guard tests passed. See Monday handoff.
- [x] Commit project source/docs locally; verify no credentials, data or weights
  staged (45 files, 586,625 bytes). Push is blocked by GitHub write authentication.
- [ ] On Monday, authenticate native Git or enable connected-app repository write
  access, then push local commits and latest aggregate reports. Watcher is local-only.
- [ ] Finish untuned/first-pass inference over all 44,553 Herald rows; report
  disagreement, class balance and missing/context-limit coverage.
- [ ] Train second pass from original Qwen on eligible agreement pseudo-labels.
- [ ] Compare all three models on frozen validation and external pilot; review
  flags before calling them errors. No second-pass/external results exist yet.
- [ ] Expand source-family overlap checks beyond contest-name/import heuristic.

### Next work: unlabeled exploration

- [x] Select Qwen3-8B as the first local model and start a revision-pinned download.
- [x] Complete/verify the download and run a local BF16 GPU inference smoke test.
  Published hashes passed; model replied `READY`; peak allocated VRAM 15.27 GiB.
- [x] Build a zero-shot binary-fidelity runner with reproducible prompts and
  source provenance. Its predictions are unvalidated, not ground-truth labels.
- [x] Run the 30-pair sample locally without editing review labels: 19 YES,
  11 NO, all 30 responses parseable; no correctness assessment performed.
- [ ] Explore corpus lengths/structure without requiring human annotation.
- [ ] Before any unsupervised adaptation, define the objective and reserve data
  families; no fine-tuning is started by the download task.

### Deferred: reviewed data pilot

- [x] Download ProofNet-V and FaithSieve pinned source snapshots, preserve labels,
  record checksums/schemas/counts and document usage in `dataset-guide.md`.
- [ ] Join archived ProofNet-V proof files to matching metadata; inspect taxonomy
  mappings and replay in an isolated compatible Lean environment before modeling.

- [x] Survey verified correspondence sources; see `verified-data-survey.md`.
- [ ] Inspect ProofNet-Verified archives/taxonomy with pinned revisions as a
  statement-level auxiliary benchmark; do not assume proof-argument labels.
- [ ] Locate released Pistis human ratings/proof pairs and FaithSieve's 135
  semantic-gate audit pairs; availability remains unconfirmed. No outreach sent.

- [ ] Prepare accessible review examples with English and Lean side by side,
  full relevant assumptions, provisional binary fidelity labels, source spans,
  and short explanations. Do not silently treat agent labels as human review.
- [ ] Select human-documented Mathlib examples and compare with the prepared
  Herald sample; record whether each English item describes a statement or proof.
- [ ] Create a trackable annotation schema and provenance/source manifest outside
  ignored download directories. Preserve uncertain/missing labels explicitly.
- [ ] Construct reviewed candidates for hard negatives and meaning-preserving
  positives, including changes to English that keep the Lean proof valid.
- [ ] Define and implement theorem-family grouping, deduplication and source
  overlap checks before generating variants or chunks; provisionally reserve
  external IMO problems/research families.

### Extraction and verification

- [ ] Build a local `.env` loader/AXLE client helper that never logs credentials;
  include low concurrency, bounded backoff, cache keys and source/environment pins.
- [ ] Investigate local Jixia/LeanDojo or Lean metaprogramming compatible with
  Lean 4.11. Compare against AXLE on a compatible synthetic or ported subset.
- [ ] Prototype chunk extraction on roughly 10 multi-step development proofs:
  source spans, context, local claims, witnesses, cases and dependencies.
- [ ] Implement a reusable verification policy beyond the smoke tests: target
  declarations, transitive axioms, admissions, pinned imports, timeouts, and
  separate environment-failure/invalid-proof outcomes.
- [ ] Check corpus replay coverage; document failures without treating all
  environment/version failures as mathematical invalidity.

### First model and baselines

- [ ] Assess Jev as an optional hosted typed-decision baseline and Clef-Flash
  as an open-weight candidate. Verify local custom-head training compatibility
  before changing the first-model recommendation. Neither has been tested here.
- [x] Select/pin the first checkpoint: Qwen3-8B. Download completion is tracked
  above and in `model-manifest.json`; Goedel remains an optional later comparison.
- [ ] Measure token lengths and real-checkpoint GPU memory/runtime; select input
  limits, batching, LoRA/QLoRA settings and treatment of long examples accordingly.
- [ ] Implement text-feature and unfine-tuned LLM baselines.
- [ ] Implement supervised LoRA training with one binary argument-fidelity head.
  Exclude uncertain/unassessable pairs from supervised labels; retain optional
  mismatch categories and verification status as independent metadata.
- [ ] Record seeds, exact checkpoint revisions, prompts, training settings and
  data manifests. Keep checkpoints and bulk results ignored.
- [ ] Evaluate false acceptance, mismatch precision/recall/F1, PR-AUC,
  calibration, abstention/coverage and theorem-clustered uncertainty.

### Separate experiments

- [ ] Compare whole-proof judging with chunk scores and with chunk alignment
  plus dependency/scope checks and global assessment.
- [ ] Pilot a restricted ForTheL fragment: pin grammar/tool version, establish
  vocabulary/foundation mappings, and test actual parser acceptance.
- [ ] Compare direct judging, ordinary-English normalization, controlled-language
  views, and original-plus-controlled inputs under comparable budgets.
- [ ] Curate and independently label frozen IMO and research-level test subsets;
  check overlap, source versions, available English arguments and build environments.
- [ ] Only after judge validation, evaluate compiler-only versus combined
  compiler/judge ranking of a fixed candidate set. Consider generator RL later.

### Project maintenance

- [ ] Review and commit the project source/docs when ready; no commit or push has
  been performed in this chat. Verify `.env`, data, weights and caches stay ignored.
- [ ] Keep the summary, TODO and methodology synchronized as decisions change.

Completed agent work:

- [x] Clone repository and inspect the proposal and workstation.
- [x] Install Git, Python, GPU PyTorch/fine-tuning/evaluation tools, VS Code
  extensions and the Jupyter kernel.
- [x] Install/pin Lean 4.11 and Mathlib; pass local smoke proof and one Herald replay.
- [x] Pass CUDA BF16, NF4 and tiny random-model LoRA integration checks.
- [x] Download/pin/audit Herald; prepare 30 unlabeled review examples.
- [x] Document main methodology and controlled-language, structured-proof and
  external-test experiments.
- [x] Verify AXLE's three extraction tools anonymously and a request using the
  locally saved API key; identify missing hosted Lean 4.11 support.
- [x] Update/verify ignore rules and create persistent session summary/TODO docs.
