# Project session summary

Last updated: 2026-11-12 (America/New_York).

## Latest handoff: laptop discussion, 2026-11-12

**User's preferred next direction:** train Lean-to-English informalization, then
train English-to-English semantic argument comparison. See
[informalization-experiment.md](informalization-experiment.md) for the two-stage
design, dataset leads, evaluation distinctions and experiment-machine checklist.
The user believes this is now the most promising direct route and wants to resume
on the larger computer that runs local models. This session updated documentation
only; no local models were run and remote experiment status was not inspected.
Preserve prior results and check actual 14B job state on that machine before work.

The target remains argument fidelity, not just theorem equivalence: different
valid proofs of one theorem are candidate negatives. Existing English/Lean pairs
may support reverse-direction training, and multiple English proofs per theorem
may support comparator training; availability/quality remain to be researched.
Keep informalizer fidelity separate from comparator and end-to-end performance.
Earlier experiment-machine paths/statuses below are historical, not this laptop's
environment. Current laptop checkout is `C:\Users\tbelcher\USC Course Repos\CSCE883`.

Workstation integration, 2026-11-12: this handoff is now read and merged.
The current workspace is the GitHub Repos path below; the laptop path above
identifies the originating session. Completed 14B results remain preserved.
The authorized 32B direct-judge pilot is currently at its backward probe and
continues as a baseline; the new planning direction does not cancel it.

## Start here in a new session

Project: `Public/CSCE883/Homework/Project` in the `hotdogontology/CSCE883`
repository. On this workstation the full path is
`C:\Users\tbelcher\GitHub Repos\Public\CSCE883\Homework\Project`.

Read this document, [TODO.md](TODO.md), and [methodology.md](methodology.md).
For the current Tuesday-night extension, read [OVERNIGHT_2026-11-10.md](OVERNIGHT_2026-11-10.md)
and [the live report](reports/hard-related-20261110/README.md), then inspect
`artifacts/hard-related-20261110/job.json`. Older handoffs below are historical.
For the unattended Friday run, first read [MONDAY_HANDOFF.md](MONDAY_HANDOFF.md)
and [automatically published results](reports/two-pass/README.md). Those snapshots
may be newer than the static session notes below.
The methodology is the current experimental plan; TODO tracks execution. The
submitted `project-proposal-tbelcher.tex` anchors the research question; current
files record what was actually implemented and later user decisions.

A useful new-session request is: "Read Homework/Project/SESSION_SUMMARY.md and
TODO.md, check the current files, and continue the project."

This summary covers the project discussion and work available in this chat,
including references to earlier work preserved in the repository. It is not an
exhaustive transcript of sessions outside the available history. Verify current
files and tool availability before relying on older operational details.

## Objective

**User reaffirmed, 2026-11-10:** every test serves the single research question:
can we identify semantic differences between natural-language mathematical
proofs and their corresponding Lean proofs? The proposal was reread. Its target
includes changed assumptions, conclusions and argument steps, especially formally
valid Lean that is an unfaithful translation. English-only coherence, lexical
similarity and compilation are not substitutes for that question. Single-language
controls are secondary diagnostics, not evidence of cross-language semantic
ability. Same-theorem route comparisons are one important subset, not the entire
definition of semantic difference. This clarification is now in `AGENTS.md`.

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

2026-11-12 source-balanced pilot implemented and32B run launched. User authorized
mitigating dataset-source shortcuts. Read SOURCE_BALANCED_PILOT.md and the live
artifacts/source-balanced-20261112/qwen32/job.json. Dataset32rows (16/8/8), each
split equally balanced by source AND label.16 provisional agent-reviewed Faithform
local-inference pairs from4problems;16 existing ProofNet full-proof positive/related
swap pairs. Review rationale and manifest saved under reports/source-balanced-20261112.
Source-only control50%; other simple controls50–62.5%, too small to certify absence
of shortcuts.32B checkpoint download/hash verification complete. New static CPU/GPU
BF16 runner performs baseline, a backward/optimizer probe, then conditional one-epoch
LoRA and reevaluation. Started corrected processPID15256; inspect actual live state.
No human gold labels claimed; Faithform placeholders cannot establish full-proof
route fidelity. Tokenizer startup issue fixed before any experimental predictions.

2026-11-12: user corrected intended32B dataset from ProofFlow to Faithform;
requested label inspection. Read FAITHFORM_LABEL_AUDIT.md. Inspected first100
rows of each paired release plus upstream metric/prover/perturbation code.
Labels are validity/intervention outcomes, not human binary correspondence.
Found concrete missing-hypothesis and assumed-conclusion mismatch candidates,
and a perturbed example that appears still valid. Truth-status reversals can
mine negatives under checked assumptions; same status cannot certify positives.
No training/new binary labels. Earlier ProofFlow question/plan is historical,
not the currently intended dataset.

Qwen32/ProofFlow audit update: 737 JSON files downloaded and blob-hash verified;
366 full English–Lean pairs extracted across184 groups, all fidelity labels null.
Upstream compilation flags31pass/335fail are not correspondence labels or local
verification. Another368 step-schema files need source joins. Download of32B
remains in progress, with final hash verification pending. Training policy awaits
the user's answer; no base/tuned comparison has run.

2026-11-11 Qwen32/ProofFlow work authorized and started. See
[QWEN32_PROOFFLOW.md](QWEN32_PROOFFLOW.md). Qwen3-32B download launched (PID33988),
61.04 GiB, separate qwen32-model-manifest.json and ignored weights/logs. Confirm
download_complete before loading. Found 736 upstream ProofFlow JSON result
artifacts with English/generated-Lean content beyond the graph-only main file;
pinned JSON-only audit running. Semantic labels remain unknown. Asked user to
choose existing training data plus external ProofFlow evaluation versus a new
provisionally labeled ProofFlow training set. No 32B tuning/evaluation yet;
GPU-only 14B loader cannot support it unchanged, and training offload needs proof.

2026-11-11 larger-model feasibility refresh: live hardware check found RTX A6000
49140 MiB VRAM (634 MiB used), 127.8 GiB host RAM (105.7 GiB available), and
3475.9 GiB free on the project drive. Rechecked current Colibri README/GGUF docs.
Recommended first larger controlled comparison is Qwen3-32B BF16 with GPU/CPU
placement via Transformers/Accelerate; roughly 64 GB of weights exceeds VRAM
but fits host memory. Feasibility estimate only, no throughput measured.
Colibri supports Qwen3 dense and MoE, but strongest streaming benefits concern
sparse MoE; documented CPU F16/BF16 matrices expand to F32 and CUDA tiled BF16
converts to FP16. Preserve precision explicitly. No larger model downloaded or
installed, no inference/training run in this refresh. Running an offloaded model
does not establish that LoRA training will fit.

2026-11-11 dataset follow-up: added Pistis and Robert Joseph George's supplied
blog to references.md. Confirmed Faithform-AF/LLMs have English-step/generated-
Lean pairs plus prover results (~153k/~102k viewer rows, repeated problems).
Validity/refutation and perturbation flags are NOT correspondence labels.
IMO-Steps HF is the public Lean release; inspected tree still lacks individual
o3-mini paired annotations. User retains interest in ProofFlow graphs without
Lean counterparts. Details and proposed blog-inspired extensions are in the
semantic data search report. No new training or label changes.

2026-11-11 dataset search: user requested real semantic-correspondence training
data beyond the synthetic 16-pair diagnostic. Read
[SEMANTIC_DATA_SEARCH_2026-11-11.md](SEMANTIC_DATA_SEARCH_2026-11-11.md).
Pistis human fidelity ratings and IMO-Steps individual model mismatch annotations
are promising leads, but their per-example releases were not located. ProofFlow
has 184 English proof/graph rows, not ready labeled English–Lean pairs; spot checks
found source-alignment concerns. FaithformBench/RobustPABench offer constructed
step-level stress tests. Statement-only datasets remain auxiliary. No new
training, imported labels, or author outreach occurred.

2026-11-11 results review: all8stages of the Tuesday queue completed at21:19
Eastern onNovember10. Read `RESULTS_2026-11-11.md`; earlier launch statuses below
are historical. New related-proof test: original42/54 (77.78%), freshLoRA53/54
(98.15%); both reject all27synthetic negatives, false rejections12->1. Validation
51/60->59/60. Old16-case same-theorem diagnostic15/16->11/16; tuned falsely accepts
5/8mismatches, although both retainAUROC1.0. No threshold selected on this diagnostic.
Training366balanced rows,46steps,35.65minutes,39.81GiBpeak; adapterverified.
Original-model intermediary test correct/scored: English->Lean9/13 (13/54coverage),
Lean->English33/48, Verbose20/35, Natural26/42. Oldcore12/12(firstmethod,4unscored)
and16/16(otherthree). These are text judgments on different covered subsets.
Zero complete code-intermediary comparison pairs have all generated branches
compiled. Only2Verbose-target individual outputs compiled and both are ordinary
Mathlib Lean, not actual Verbose syntax. Both dialect environments built correctly.
Generator fine-tuning was conditional on suitable paired data, which was not
found; Colibri was researched/planned only, without larger-model inference.
No new model run during this review. Raw results and historical runs preserved.

2026-11-10 evening: user authorized a new relatedness-threshold train/validation/
test dataset, original vs freshly LoRA-tuned Qwen3-14B, four translation-based
architectures (English-to-Lean, Lean-to-English, dual Verbose Lean, dual Natural
Lean), and Colibri feasibility research. Work resumed after a connection error;
see `OVERNIGHT_2026-11-10.md`. The background queue started at 17:53 Eastern;
initial stage is `untuned-direct`. Read the live job file instead of assuming
all requested stages have completed. Dataset is frozen: 366 training, 60
validation, 54 test rows, each balanced. Threshold0.20; family split70/15/15
before filtering; exact English/Lean marginals across labels. Primary negatives
swap coherent English statement/proof bundles; proof-only diagnostics are saved.
All four generation paths passed real GPU execution checks on old diagnostic
examples; these are smoke checks, not new generalization evidence. English-to-
Lean smoke outputs contain invalid Lean4 syntax. Separate compiler checks and
compiler-qualified coverage prevent interpreting those outputs as verified Lean.
The eight-stage queue uses one GPU worker at a time and writes an aggregate
report after each stage. Original vs tuned direct judging uses validation/test/
old-core; generation architectures use test plus old-core only.
Natural Lean and upstream examples compile in isolated4.36-rc2; Verbose4.31
also built successfully, including upstream examples and two actual syntax probes.
Both matching compiler environments are now ready. No suitable curated paired
dialect-generation dataset was located, so generation LoRA is not performed.
Colibri source/planner research is in `reports/intermediary-sources-20261110/`:
Windows/A6000 support exists, but default raw-safetensors loading uses int8 and
requires explicit precision/memory testing before larger unquantized inference.
No larger checkpoint download or Colibri model inference was performed.
The new authorization permits synthetic similar-proof negative labels without
requiring a manual review first; their assumed status must remain explicit.
Earlier results and adapters are preserved. No second-pass self-training.

2026-11-10 context correction: user challenged the emphasis on English-only
controls. Agent acknowledged that these do not measure the target English–Lean
semantic comparison, reread the original proposal, and updated AGENTS/methodology/
TODO to keep every experiment tied to that question. No new run, relabeling,
training or change to historical measurements accompanied this correction.

Completed follow-up (2026-11-10): user authorized about an hour of independent work.
Read `RELATEDNESS_RUN_2026-11-10.md` and live
`artifacts/relatedness-20261110/job.json`. Isolated official Lean4.28/mathlib cache
installed; all365 extracted targets replay successfully. Graph10343nodes/83785
edges.765train/177validation views: controls, related English-proof swaps,
related English bundles. All unlabeled, within original splits, donor marginals
preserved, <=4096tokens. Frozen RF/Qwen surveys complete and original controls
reproduce. Acceptance outof59 (control/proofswap/bundle): EnglishRF51/31/51,
bothRF50/39/48, untuned37/2/0, tuned59/9/8. Not candidate accuracy. See
`reports/relatedness-20261110/README.md`. Exact normalized signature audit found
no duplicates (not an equivalence check). Full Herald forest survey completed:
same 44,537 unique scored IDs; English-only forest YES44,531/NO6, both-language
YES44,535/NO2. Original RF metrics reproduced; no known Herald accuracy. See
`reports/random-forest-herald-20261110/README.md`. Raw predictions ignored.
No new fine-tuning. Do not start duplicate drivers or interpret candidate survey
acceptance counts as accuracy. Large environments/graphs/raw candidates ignored.

2026-11-10 follow-up: user requested mathlib-based relatedness/harder proof swaps
and a random forest comparison. See `relatedness-and-baselines.md`. Implemented
and ran `scripts/random_forest_argument.py` on the unchanged510/118 split and
16-case diagnostic: both-language forest105/118 (88.98%),9/16 (56.25%);
English-only108/118 (91.53%),8/16. Training-only TF-IDF/SVD/features/forest fitting,
fixed hyperparameters/0.5 threshold; no Qwen rerun. Full metrics and predictions
in `reports/random-forest-20261110/`. Mathlib graph is a design, not completed
extraction: use statement vs proof dependency/module features, candidate mining
within splits and actual label review. Local4.11 vs ProofNet4.28 version mismatch
must be resolved before authoritative elaborated dependency extraction.

**Latest verified status (2026-11-10): the full corrected overnight 14B pipeline
completed at07:01 Eastern.** Read `RESULTS_2026-11-10.md` and
`reports/argument-14b-overnight/`. All setup/running/audit-hold entries below are
historical. No model rerun or new training was started during this status review.

Unquantized BF16 Qwen3-14B LoRA trained on510 balanced proof-body examples for
3983.39s (~66.4min),64optimizer steps,39.72GiB peak VRAM; adapter saved.
Coarse proof-swap validation: untuned96/118 (81.36%), tuned118/118 (100%).
English-only control107/118 (90.68%) confirms this task's shortcut limitation.
Same-theorem constructed diagnostic (4groups/16cells): untuned15/16 (93.75%),
tuned8/16 (50%, all YES). Masked-formal control8/16 forboth. Crucially AUROC is
1.0 forboth: all positives still rank above all negatives, but tuned scores
saturate above the fixed decision threshold. Do not call this universal loss of
argument discrimination or choose a new threshold on these diagnostic cases.

Herald: each file verified44553uniqueIDs;44537scored,16too-long. UntunedYES34901 /
NO9636; tunedYES44385 /NO152. Agreement34995,disagreement9542;9513NO-to-YES,
29YES-to-NO. No independent Herald accuracy. Fullnight~13h15m. New score review
saved at `reports/argument-14b-overnight/review-20261110.json`. Next recommendation:
independent calibration and expanded same-theorem tests before more adaptation.

**Latest authorization and active run (2026-11-09 evening):** user left for the
night and requested the next stage. Audit extraction/split defects were corrected
and checked before restarting, and a compiled same-theorem diagnostic was added.
See `OVERNIGHT_2026-11-09.md`. Active job is now
`artifacts/argument-14b/overnight-20261109/job.json`, reports in
`reports/argument-14b-overnight/`; earlier held v3 is historical and points to this
new run. Source-v4 integrity checks pass, no full Lean4.28 corpus replay claimed.

Data-v4: 365 positive sources, 588 train/142 validation rows before length filtering.
After 4096-token filtering and negative regeneration: 510 train/118 validation,
balanced with exact English-proof marginal equality. All 99 Herald splits and
ProofNet289 fixed; genuine helpers60/185/257 retained; family/shared-proof split
overlap fixed. Core: four theorem groups, eight compiled routes, sixteen crossed
agent-constructed cases plus formal-proof-masked control; never training material.

Real BF16 14B probe passed at 4096 tokens (actual3946), backward/optimizer included,
39.11GiB allocated peak,32.82s. An8192 trial was stopped after240s near GPU capacity;
no quantized fallback. Pipeline now runs untuned validation/core/masked, ordinary
LoRA, tuned evaluations, then both Herald passes. No second pass; coarse swap
accuracy alone is not proof-route evidence. Twenty-four guard tests passed.
The user's Light/Medium thinking preference was recorded; active app effort could
not be changed through available tools. No global configuration change was made.

**Latest: 2026-11-09 audit completed.** Read `PLAN_AUDIT_2026-11-09.md` and the
current-protocol table in methodology.md before new work. Qwen3-14B downloaded
and all published LFS hashes verified. Fixed its manifest path to the actual
14B directory. Driver was held while still waiting for download, before any
real-model probe/training; current state `held_for_audit`. Old statements below
about an ongoing download or automatic training are historical.

Audit findings: new v3 proof swaps admit an English-only shortcut (TF-IDF control
132/144 = 91.67%, threshold trained only on training data); cannot claim learned
cross-language proof-route matching. Confirmed extraction bugs: 99 malformed
Herald boundaries, malformed ProofNet-289 boundary, dangling context in IDs
60/185/257, shared English proof across train324/validation141. Regenerate after
parser/dependency/family fixes. Preserve v3 for audit; no silent input overwrite.

Old 8B metrics recompute correctly, but context-only source-style cue scores
74/112 = 66.07% (rule direction selected on training). First-pass AUROC improves
.6458 to .7215, despite lower mismatch recall at the fixed decision rule. Old
training row35-corrected retained a proof; no validation row did. There are 71
source problems in 112 validation rows. Limit claims to this particular recipe
and benchmark; second-pass non-improvement is not a universal self-training result.

Proposed core evaluation: same theorem, valid routes A/B in English and Lean,
diagonal YES / off-diagonal NO, grouped by theorem with independent held-out
families. English-only and masked-formal ablations required. ProofNet positives
remain user-assumed as authorized. Future verbose Lean uses the same test rather
than compilation/equal-output alone. Diagnostic artifacts in `reports/audit-20261109/`.

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

### 2026-11-10 — completed overnight results review

- Read handoff, plans, actual job state and all aggregate evaluations. Confirmed
  complete pipeline, training metadata, unique Herald coverage and score behavior.
- Saved post-run descriptive review. Coarse validation improved to100%, fixed-rule
  core accuracy dropped to50% (allYES), while core ranking remainedperfectAUROC1.
  Reported threshold/score saturation separately from actual ranking ability;
  no calibration or model rerun performed. Updated completed TODOs/results note.

### 2026-11-09 — corrected overnight continuation

- User authorized proceeding while away. Implemented signature/dependency/split
  fixes, regenerated versioned data and preserved earlier artifacts/results.
- Built and compiled four two-route core matrices plus a masked-formal control.
  Added post-budget negative regeneration, provenance gates and duplicate-worker
  guards. Passed24 guard tests; real14B BF16 probe fits4096 tokens at39.11GiB.
- Launched fresh sequential overnight pipeline; current results/stages are in
  the new run/report paths. No completed LoRA/Herald result implied by setup note.

### 2026-11-09 — research and implementation audit

- Parallel read-only reviews examined methodology, implementation and saved 8B
  results. Root reproduced English-only and context-only controls plus extraction
  defects and token-filter marginal imbalance; saved scripts and JSON reports.
- Held queued driver before model loading due concrete extraction/split defects.
  Download completed independently; corrected manifest metadata. No model training
  or historical-result rewrite performed. Updated authoritative protocol table,
  audit report and TODOs with specific fixes and a same-theorem core test.

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
