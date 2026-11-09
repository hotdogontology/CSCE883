# Project session summary

Last updated: 2026-11-09 (America/New_York).

## Start here in a new session

Project: `Public/CSCE883/Homework/Project` in the `hotdogontology/CSCE883`
repository. On this workstation the full path is
`C:\Users\tbelcher\GitHub Repos\Public\CSCE883\Homework\Project`.

Read this document, [TODO.md](TODO.md), and [methodology.md](methodology.md).
For the unattended Friday run, first read [MONDAY_HANDOFF.md](MONDAY_HANDOFF.md)
and [automatically published results](reports/two-pass/README.md). Those snapshots
may be newer than the static session notes below.
The methodology is the current experimental plan; TODO tracks execution. The
submitted proposal is historical context, not a record of everything implemented.

A useful new-session request is: "Read Homework/Project/SESSION_SUMMARY.md and
TODO.md, check the current files, and continue the project."

This summary covers the project discussion and work available in this chat,
including references to earlier work preserved in the repository. It is not an
exhaustive transcript of sessions outside the available history. Verify current
files and tool availability before relying on older operational details.

## Objective

New data research (2026-11-06): see [verified-data-survey.md](verified-data-survey.md).
ProofNet-Verified supplies audited statement alignment, not certified argument
alignment. Pistis evaluates proof fidelity with human ratings; individual data
release not located. FaithSieve reports 135 human-audited local statement pairs;
its public ProofLoc files instead label correctness/first errors. No new verified
argument labels were imported and no change to the chosen target was made.

Build and evaluate a learned judge of correspondence between natural-language
mathematics and Lean formalizations. The motivating concern is that a formally
valid Lean proof can establish a statement or follow an argument different from
the intended English mathematics. Agda is a possible later extension.

Keep three outcomes separate:

**Confirmed user decision:** the first model predicts one binary label for
faithful translation of the argument. Yes requires the same claim/assumptions
and essential reasoning; a different valid proof of the same theorem is No.
The following three concepts remain distinct for annotation and diagnostics,
not three model outputs. Earlier multi-head suggestions are optional extensions.

1. Formal validity under a pinned Lean environment and an explicit axiom policy.
2. Statement correspondence: objects, domains, assumptions, quantifiers, conclusion.
3. Argument correspondence: essential intermediate claims and reasoning structure.

Different valid proofs of one theorem can match statements but differ in argument.
Allow uncertain labels; missing English proof material is not a negative label.

## Current state

Future-work proposal saved (2026-11-09): user supplied PatrickMassot/verbose-lean4
and medovina/natural_lean. See `references.md` and `verbose-lean-experiment.md`.
Generate verbose Lean independently from English and from original Lean, compare
the resulting argument structures, and explore a custom generator/judge design
guided by actual compilation plus correspondence. Not implemented or installed;
does not change the running direct 14B proof-body experiment.

**New active experiment (2026-11-09):** user explicitly requested preserving
statement-only results, downloading the largest practical unquantized Qwen,
training/evaluating proof BODY correspondence, and applying untuned/tuned models
to Herald; no second pass. Selected fully GPU-resident Qwen3-14B in BF16,
~27.52 GiB original weights; 32B BF16 exceeds the 48 GiB GPU. Download is in progress
at this note; no real 14B training/probe result yet. Full details in
`argument-experiment.md`. Driver state: `artifacts/argument-14b/job.json`, waiting
for verified download, then memory probe / untuned validation / LoRA / tuned
validation / both Herald runs. Check job state before launching GPU work.

Using the user's explicit assumption that corrected ProofNet proof pairs are
argument positives. Extracted 361 pairs; excluded six with unsafe/unclear target
or dependency context. Active data `artifacts/argument-14b/data-v3`: 578 train /
144 validation examples, balanced with constructed unrelated-English-proof swaps.
Statements and Lean body/context unchanged across each positive/negative pair.
Donors are within split and used once; pairwise context filtering preserves class
balance. Both proof bodies are actual input fields and formal English comments
are removed. Hard same-theorem alternative-argument discrimination remains an
unmeasured extension. Fifteen guard tests passed. Prior 8B artifacts are intact.

Scope clarification (2026-11-09): user emphasized argument matching and questioned
our dismissal of ProofNet-V. Rechecked primary documentation and actual archived
proofs. ProofNet-V DOES supply paired English/formal proof material; examples 11
and 13 visibly use the same Eisenstein strategy. The claim we cannot establish
is a released dataset-wide argument-alignment guarantee/label, not the existence
of useful proof pairs. Example 1 uses closure induction versus English power
normal forms; acceptable granularity needs resolution. See updated
`verified-data-survey.md`. Some archive files mix old admitted statements,
refutations and completed corrections; isolate the intended target. No new
training, argument labels or local replay performed. Do not silently narrow the
argument target for future experiments; the statement-only run remains an auxiliary
experiment and does not answer the user's principal research question.

Classification reporting update (2026-11-09): original runs recorded accuracy
and confusion counts, but did not report precision/recall/F1. Added reproducible
`scripts/classification_metrics.py` to compute both match and mismatch class
metrics, macro/weighted F1, balanced accuracy and coverage from saved frozen
validation predictions. Outputs: `reports/two-pass/classification-metrics.csv`
and `.json`. No retraining or new labels; positive-class convention explicit.

**Monday verified status (2026-11-09): the full queued pipeline completed** at
2026-11-07 05:55 UTC (Saturday 00:55 Eastern). Verified saved adapters for both
passes and 44,553 unique source IDs in each Herald prediction file. No rerun
started. The Friday running/pending descriptions below are historical.

- Untuned/first-pass each predicted 44,499 Herald rows; 54 exceeded input budget.
  They disagreed on 17,422, agreed on 27,077. Untuned YES: 23,798; first-pass YES:
  41,218. Agreement is not accuracy; Herald has no independent match labels.
- After reserving 115 contest-family agreements, retained 26,962 pseudo-labels
  (23,688 YES, 3,274 NO). Second-pass training used 26,961; one exceeded the
  training token budget including its answer. Fresh original base, one epoch,
  3,371 optimizer steps, 18,079.37 seconds (~5.02 hours), 12.86 GiB peak VRAM.
- Frozen 112-pair validation: untuned 70/112 (62.50%), first pass 79/112 (70.54%),
  second pass 74/112 (66.07%). Mismatch rejection: 21/39, 13/39, 14/39 respectively.
  Second pass did not beat first pass on this validation; neither tuned model
  improved mismatch detection over untuned. Single-run, within-source results.
- External pilot: five of six cases scored; bin-packing case exceeded context.
  All models said NO on the three IMO cases and matching-entropy case. Binary
  counting: untuned NO / first pass YES / second pass NO. No human labels or
  confirmed errors: question/answer scope, theorem versions and PDF formatting
  remain confounds. Do not describe this as external accuracy.
- No successful push established; local commits remain `3ebcd52`, `0b4e149`.
  New aggregate report files are modified locally. No new publishing attempt
  was made during this Monday status review.

Next: inspect representative disagreements and external source alignment, fix
input/scope problems, and evaluate with independent correspondence labels before
more self-training. Compilation, proof-argument judging, ForTheL and chunk
alignment remain separate outstanding work. See `reports/two-pass/README.md`.

Friday continuation: user authorized running as much of the experiment as possible
and pushing the work to GitHub before their Monday return. Code was committed
locally, but native Git requires interactive sign-in and the connected GitHub app
returned HTTP 403 `Resource not accessible by integration` on a write request.
No successful push is confirmed. Per the user's instruction, stop setup work at
this permission blocker. The existing GPU pipeline continues. A separate watcher
exports aggregate reports in local-only mode and holds a temporary Windows
execution request. Optional automatic report pushing is implemented but NOT active.
It records failure
as well as completion; no permanent power-plan change. Long second-pass training
now saves adapter/optimizer/RNG/progress every 512 examples (manual recovery).
Nine meaningful guard tests passed. See Monday handoff and live process/log state.

**Latest authorization:** the user requested ProofNet-V first-pass LoRA, full
Herald comparison against untuned Qwen, a second pass trained from original Qwen
on teacher labels, then IMO/OpenAI screening. User explicitly chose agreement-only
pseudo-labels. See [two-pass-experiment.md](two-pass-experiment.md). Implemented
scope is statement fidelity because the available trusted labels are statements.
First pass completed (448 training pairs, 56 steps, 230.61 seconds, 10.56 GiB peak).
Held-out 112 pairs: untuned 62.50%, first pass 70.54%, but mismatch rejection falls
21/39 to 13/39. Do not claim a reliable issue detector. Driver is running with
PID in `artifacts/two-pass/job.pid` and state in `artifacts/two-pass/job.json`;
check live state before launching GPU work. Full Herald and later results remain
pending at this update. Second pass is fresh-base self-training, not unsupervised.

Downloaded reference datasets: see [dataset-guide.md](dataset-guide.md) and
`verified-data-manifest.json`. Pinned ProofNet-V snapshot includes 367 corrected
examples and an archive with 367 Lean 4.28 proof files. Pinned FaithSieve snapshot
includes ProofLoc 350 Olympiad + 200 university NL proofs with first-error labels,
no Lean counterparts or semantic-gate audit pairs. Raw files remain ignored.
Schemas/counts checked; no local Lean replay or argument labels imported.
Statement-only first-pass fine-tuning has since completed as described above.

**Earlier steering (superseded for task training):** the user deferred checking the 30 sampled pairs and wants
to proceed without manual labels. Qwen3-8B is selected as the first model; its
pinned download is complete and local BF16 inference passed. Start with unlabeled exploration.
Zero-shot inference is not fine-tuning; no self-supervised training objective has
been selected and no classification performance can be established without labels.

| Area | Completed | Outstanding |
| --- | --- | --- |
| Workstation | GPU stack and Lean installed; full-checkpoint inference smoke test passed | Representative long-input/training memory and runtime measurements |
| Data | Herald downloaded and structurally audited; Mathlib source available | Reviewed labels, hard negatives, leakage-aware splits |
| Model | Qwen3-8B downloaded; 30 argument judgments; first-pass statement QLoRA trained | Full Herald comparison, second pass and external screening running/queued |
| Extraction | Three AXLE endpoints tested anonymously; saved-key request succeeded | Compatible extraction pipeline for Lean 4.11 corpus |
| Experiments | Direct, structured, controlled-language and external-test plans written | Implement baselines and evaluate |
| Repository | Ignore rules verified; user authorized commit/push and aggregate-report publishing | Check Git history/push state and newer automatic reports |

## Workstation and verified software

- CPU: Intel Core i9-14900KF, 24 cores / 32 threads.
- GPU: NVIDIA RTX A6000, 48 GB VRAM. PyTorch reports 47.99 GiB and compute
  capability 8.6. Driver observed: 595.71.
- RAM: approximately 128 GB. At initial inspection C: had about 3.45 TiB free
  and D: about 3.64 TiB free; those free-space values are historical.
- Native Windows Python 3.12.10; project environment: `.venv`.
- PyTorch 2.11.0+cu128, Transformers 5.22.2, PEFT 0.21.2, bitsandbytes 0.50.2,
  TRL 1.17.1, dataset/evaluation packages, Jupyter and pypdf installed.
- Exact package versions: [requirements-lock-windows.txt](requirements-lock-windows.txt).
- Verified CUDA BF16 forward/backward, NF4 layer forward/backward, and one
  LoRA classification optimizer step on a tiny random Qwen3 model. This did not
  download pretrained weights or demonstrate research performance.
- Lean 4.11.0 managed through elan; Mathlib revision
  `20c73142afa995ac9c8fb80a9bb585a55ca38308`, with Lake manifest pinned.
- `lean/Correspondence.lean` builds. A renamed replay of Herald row 0 builds
  with printed axioms `propext` and `Quot.sound`.
- VS Code Lean/Python/Jupyter extensions installed. Notebook kernel:
  `CSCE883 correspondence`.
- WSL2, vLLM, FlashAttention and a standalone CUDA Toolkit were not installed.
  The tested native stack works; future backends may have other requirements.

Commands and limitations: [SETUP.md](SETUP.md), [verification.md](verification.md).

## Model discussion

The user also proposed Jev. Official TypeSafe docs describe hosted typed decisions
and no customer-specific fine-tuning; it is an optional external baseline rather
than a local LoRA backbone. The supplied `jevai.net` link is unofficial. Cloudflare
Clef-Flash (9B, Apache 2.0) was identified as an open decision-model candidate,
subject to checking its custom head/training support. No Jev API calls were made.
These remain optional comparisons. Measure domain calibration rather than assuming it.

The original proposal named Qwen2.5-Coder-1.5B. Hardware allows larger adapter
experiments. The selected starting model is Qwen3-8B, with
Goedel-Prover-V2-8B as a similarly sized Lean-specialized comparison. Newer Qwen
models and a 27B quantized model were discussed as additional comparisons, not
selected. Qwen3-8B is downloaded at revision
`b968826d9c46dd6066d109eabc6255188de91218`; see `model-manifest.json` for status.
It is the first experimental model, not a benchmark-selected winner.

Local path: `data/models/Qwen3-8B/` (ignored). `scripts/download_model.py` resumes
the pinned download and verifies published hashes. `scripts/run_model.py` loads
local-only safetensors in BF16 with remote code and thinking disabled. The smoke
test replied `READY`: 10.28 s load, 0.46 s generation of 2 tokens, 15.27 GiB peak
allocated VRAM. These tiny-prompt timings do not predict long-proof throughput.
The ignored report is `artifacts/last-model-run.json`. No task training occurred.

The later supervised design uses LoRA and one binary argument-fidelity output.
For now, manual review is deferred and unlabeled/zero-shot work comes first.
The rubric guides future labeling; uncertainty is a review status, not a third model class.
Lean checking is an independent deterministic gate.
Do not mistake adding a constant compilation bonus to a fixed-pair classifier
for learning correspondence. For a later generator, gate reward on proof
integrity and then score correspondence with a separately evaluated frozen judge.
GAN-like joint training was discussed, but is not the initial plan.

## Data and human review

The first zero-shot run is saved in ignored
`artifacts/zero-shot/20261106T210906480486Z/`. All 30 sampled pairs produced
parseable binary responses: 19 YES, 11 NO. This is a prediction distribution,
not measured accuracy; no human labels or Lean checks were added. Exact prompts,
source row/input hashes and model/generation settings are recorded. The runner
uses one loaded BF16 model, greedy decoding and non-thinking mode. It sends only
English statement/proof plus Lean header/completed proof, excluding comment-based
English annotations and review fields. Oversized inputs and malformed responses
are recorded separately rather than silently truncated/coerced. Source review
records remain unchanged. Entry points: `scripts/judge_pairs.py`,
`prompts/fidelity-v1.txt`; usage is in SETUP.md.

- **Mathlib:** primary formal source with human-written docstrings, exposition
  and some proof comments. Docstrings often describe statements rather than
  full proof arguments. Review the correspondence actually supported by each item.
- **Herald Proofs:** `FrenzyMath/Herald_proofs`, revision
  `2d31b459df74d730bff85682de237d894b4eecfa`; 44,553 rows.
  Download and reports are under ignored `data/herald/`.
- Required text fields have no null/empty values in the structural audit;
  no duplicate theorem names or identical full formal proofs were found.
  Statement templates contain admission tokens; the completed-proof field had
  none of the scanned tokens. This is not a transitive-axiom or semantic audit.
- Use `header` + `formal_proof`, not the admitted `formal_theorem` template,
  for complete-proof replay. Exclude `commented_proof` from judge inputs to
  avoid English annotation leakage.
- `scripts/audit_herald.py` prepares 30 **unlabeled** review pairs at
  `data/herald/review-unlabeled.jsonl`. They have not been manually labeled.
- The 30 pairs are a rubric-development suggestion, not a sufficient training
  or test set and not an obligation for the user to label every item unaided.
  Agent prepares comparisons/provisional labels; human review supplies stronger
  judgments. Large training data can have documented weak supervision, sampled
  quality checks, and a substantially larger independently reviewed evaluation set.
- Construct subtle negatives, particularly altered English paired with unchanged
  valid Lean. Verify edits actually change meaning. Include hard positives.
- Herald is derived from Mathlib. Split source theorem families before variants,
  comments, generated English, chunks or controlled-language translations. Many
  chunks/mutations of one theorem are not independent mathematical examples.
- Replaying with Mathlib imports can expose the original target theorem; renaming
  a declaration alone does not prevent circular shortcuts for generator evaluation.

## Additional experiments

**Controlled language:** the user proposed ForTheL and a commuting diagram.
The linked 2007 paper was downloaded/read locally. Test direct judging against
independent controlled-language views, with ordinary-English normalization as a
control. No ForTheL bridge or Naproche installation exists yet. First-order
ForTheL and dependent-type Lean need explicit vocabulary/foundation mappings.
See [controlled-language-experiment.md](controlled-language-experiment.md).

**Commuting diagrams:** NL -> FL -> NL is a cycle. A useful second axis is
proof -> theorem statement, but that loses argument details. Proof -> structured
argument graph retains intermediate claims and dependencies. Agreement and
round-trip consistency are evidence, not semantic guarantees; shared errors can
survive cycles. Lean proof irrelevance makes proof-term equality unsuitable for
distinguishing arguments.

**Chunking:** independently extract claims, assumptions, witnesses, cases and
dependencies from English and Lean. Align with one-to-many/many-to-one matches;
check coverage, scope and dependency consistency, then assess the whole proof.
Matching isolated pieces does not establish a matching whole. A shared model
can score chunk pairs initially; no graph neural network is committed.
See [structured-proof-experiment.md](structured-proof-experiment.md).

**External tests:** reserve IMO/Compfiles problems and selected OpenAI October
2026 research manuscript sections as separate tiers. The latter source is
`openai/math`, with `lean/formalization.yaml` connecting papers and declarations.
Neither source supplies automatic proof-fidelity ground truth. Some IMO
formalizations originate in Mathlib Archive; reserve these across all sources.
Public-data exposure in pretrained models remains a limitation. No final test
set was built. See [external-test-plan.md](external-test-plan.md).

## AXLE access and credentials

- AXLE is Axiom's hosted Lean utility service. Public standard access and API
  keys were advertised as free when checked; bulk capacity should be confirmed.
- Anonymous synthetic tests passed for `have2lemma`, `extract_decls` and
  `extract_proof_states` using `lean-4.28.0`.
- The user obtained a key and saved it in project `.env`. An authenticated
  lemma-extraction request returned one lemma and no Lean/tool errors.
  This verifies a successful request using the saved key, not billing/capacity
  guarantees. No key value belongs in this document, logs, chat or Git.
- `.env` is ignored. Load `AXLE_API_KEY` locally without printing it; there is
  no persistent environment loader or AXLE SDK integration implemented yet.
- Tested tool URL: `https://axle.axiommath.ai/api/v1/<tool>`.
  Environment list: `https://api.axle.axiommath.ai/v1/environments`.
- No AXLE MCP connection or `axiom-axle` Python package was installed here.
- Advertised standard environments ranged from Lean 4.21 to 4.35; 4.11 was absent.
  Preserve the local corpus pin and investigate compatible local tooling or an
  explicitly ported subset. Do not silently upgrade the corpus to use the API.
- `have2lemma` defaults to `sorry` bodies; request `include_have_body=true`.
  Preserve imports/context and elaborate proof dependencies. Service defaults
  can replace import headers; record processed content and version.
- Documented concurrency was 10 anonymous / 20 keyed requests. Start with low
  concurrency, cache results, back off and cap retries. No bulk run was made.

## Repository hygiene and continuity

Root/project ignore rules exclude environments, downloads, data, model weights,
checkpoints, outputs, Lean caches/replay files, and `.env`. Keep source,
requirements locks, Lean toolchain/manifests, curated annotations and small
dataset manifests trackable. Put curated labels outside ignored `data/`.
Fifteen older homework model weight files were already tracked; ignore rules
do not remove them or rewrite history, and they were left in place.

After meaningful work, update this summary's current state, the task checkboxes,
and the dated log below. Distinguish user decisions, agent recommendations,
implemented features and untested proposals. Never infer a completed experiment
from a planning document.

## Session log

### 2026-11-09 — authorized BF16 proof-argument experiment

- User confirmed argument target and explicitly authorized assuming corrected
  ProofNet pairs match; requested larger unquantized model and no self-training
  second pass. Started revision-pinned Qwen3-14B download in its own directory.
- Implemented corrected-proof extraction, comment/admission guards, within-split
  deranged proof swaps and paired length filtering. Prepared active v3 dataset.
- Implemented BF16 LoRA training and constrained argument inference plus sequential
  driver waiting for verified weights. Preserve prior statement-only results.

### 2026-11-09 — Monday results review

- Read AGENTS, handoff, methodology, TODO and actual job/training/prediction
  artifacts. Confirmed full completion, both saved adapters, complete unique-ID
  Herald coverage and final watcher completion record. Updated stale TODOs and
  documented validation, pseudo-label balance and external coverage limitations.
- No new training, push, external error verification or independent labeling
  performed. Full training second pass did not outperform first pass on validation.

### 2026-11-06 — unattended run and GitHub handoff

- Confirmed active untuned Herald inference; retained the existing sequential GPU
  job rather than launching a duplicate. User authorized continuing experiments
  and pushing project work before Monday.
- Added periodic future-training recovery checkpoints and an aggregate exporter /
  Windows-awake watcher with restricted automatic report commits/pushes. Nine
  tests passed, including secret-field exclusion and refusal of unrelated staged
  files. Created Monday handoff. Local commit `3ebcd52` saved all project work.
  Native push required sign-in; connected app writes returned HTTP 403. Watcher
  launched local-only; no successful push. Full experiment status is in reports.

### 2026-11-06 — first-pass training and queued self-training

- Built a statement-only prompt and QLoRA training/prediction/consensus pipeline.
  Prepared 448 train/112 validation original/corrected pairs grouped by problem;
  excluded ambiguous/incorrect-English problems and deduplicated pairs.
- Completed real-checkpoint first-pass training and untuned/first-pass held-out
  inference. Accuracy improves while mismatch rejection worsens; recorded both.
- Implemented the user's agreement-only policy and a fresh-base second pass.
  Launched sequential driver for all Herald rows and subsequent stages. Prepared
  six unlabeled external source units from Compfiles and two OpenAI manuscripts;
  no independently verified errors or external accuracy claims.

### 2026-11-06 — reference downloads and LoRA clarification

- Downloaded immutable source snapshots for ProofNet-V and FaithSieve with
  archive/file checksums, row counts and schemas. Original labels preserved.
- Confirmed completed archived proof files and ignored data folders. Clarified
  trusted label scope: statement fidelity versus proof correctness versus our
  argument-fidelity target. Documented LLM-backed binary classification and LoRA.

### 2026-11-06 — verified sample data search

- Recorded ProofNet-Verified, Pistis, FaithSieve and revision-scoped human audit
  evidence with availability and target-label limitations. Found public FaithSieve
  benchmark files but not the 135 semantic-gate audit pairs. Recommended inspecting
  ProofNet-Verified for an auxiliary statement benchmark and locating Pistis's
  human-reviewed proof artifacts. No new data or model evaluation was performed.

### 2026-11-06 — setup and research design

- Cloned CSCE883 to `GitHub Repos/Public`; installed Git after initial setup issues.
- Read the proposal; inspected hardware and installed/verified the native ML and
  Lean environments. Downloaded/audited Herald and prepared review examples.
- Discussed supervised judging, generator rewards, GAN similarities, separate
  statement/argument labels, and human review versus weak supervision at scale.
- Added Mathlib documentation, IMO and OpenAI results to the data/test plans.
- Read ForTheL and developed controlled-language and commuting-diagram experiments.
- Added hierarchical chunk matching; verified AXLE extraction access and the saved
  key on synthetic proofs. Identified the Lean-version compatibility constraint.
- Updated ignore rules and created continuity/TODO documents. No pretrained-model
  download, research training, final labels, final split, commit or push completed.
- Clarified that the review file contains 30 random pairs selected with seed 883,
  not the first 30 or examples chosen for accessibility. Proposed a rubric with
  separate statement/argument ratings (match, partial mismatch, mismatch,
  uncertain, not assessable), confidence and verification status; it has not been
  applied or finalized with reviewers.
- Investigated Jev and added a typed-decision baseline option and the open-weight
  Clef-Flash candidate to the plan; no change to the selected-model status.
- The user confirmed that the target is faithful translation of the argument,
  and requested simplicity. Updated the main plan from multiple prediction heads
  to one binary fidelity label; mismatch tags are optional diagnostics.
- The user proposed correctness as the commuting diagram's second dimension.
  Recorded a validity-assessment square and the distinction between fidelity,
  English validity and Lean verification. Correct English can fail to translate;
  incorrect English can accompany valid Lean that repairs/changes its argument.
- The user deferred the 30-pair manual review and requested model selection and
  download. Selected Qwen3-8B for unlabeled/zero-shot work; began a pinned 15.27 GiB
  safetensors download. No adaptation objective or task training has been started.
- Completed Qwen3-8B download and verified file sizes/published LFS hashes. Local
  BF16 inference on the A6000 passed (`READY`, 15.27 GiB peak allocated VRAM).
  Added resumable download and local inference scripts plus a trackable manifest.
- Implemented the zero-shot pair runner and passed four guard tests covering
  evidence leakage, missing proofs, malformed responses and source immutability.
  Processed the 30 sampled pairs: 19 YES / 11 NO; no validated labels or metrics.
