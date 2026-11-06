# External evaluation: IMO and research manuscripts

Proposed 2026-11-06. These sources are candidates for held-out evaluation, not
automatically labeled examples. No external source corpus was cloned or compiled
for this planning update.

## Evaluation tiers

| Tier | Source | Intended role |
| --- | --- | --- |
| Internal | Reviewed Mathlib/Herald theorem families | Establish classification and calibration performance |
| External contest | IMO problems with complete Lean solutions and reviewed English arguments | Test transfer to contest mathematics and differing proof strategies |
| External research | Selected OpenAI manuscript sections with identifiable Lean counterparts | Stress-test scope, assumptions, long context and argument fidelity |

Keep the tiers separate in reporting. The research tier will initially be a
small set of qualitative/quantitative case studies; it cannot support broad
claims about research mathematics without representative sampling and expert
labels. Task difficulty and domain familiarity may explain failures independently
of the model's correspondence capability.

## IMO sources

https://dwrensha.github.io/compfiles/imo.html
https://github.com/dwrensha/compfiles

The catalog inspected on 2026-11-06 reports 274 formalized problems and 270
complete formalized solutions. These are catalog counts, not our verified usable
pair count. A problem statement and complete Lean solution do not necessarily
include a full English proof following that same argument.

Inspected example:
https://dwrensha.github.io/compfiles/problems/Compfiles.Imo2024P1.html

That page displays a statement-only template with `sorry`, links a complete
solution, and identifies its source as Mathlib's `Archive/Imo/Imo2024Q1.lean`.
Its generated-page commit is `47b19bbfe5f38dc49379a6b53008d2909c4d71c5`.
Use the complete source and its pinned project environment for proof checking,
not the extracted template. Inspect a source-matched English solution separately.

Proposed pilot: 10-20 IMO problems with manageable proofs and enough reviewed
English material, selected before seeing model outputs. Record year/problem
identity, alternative solutions and reformulations. Reserve all variants of each
problem across Mathlib (including Archive), Herald, Compfiles, Lean Workbook,
miniF2F and any other fine-tuning source. Old public IMO problems may already be
in pretrained models; describe this as external-domain evaluation, not proof
that the model has never encountered the problems. Publication dates relative
to a model's documented training cutoff can inform a separate temporal subset,
but do not by themselves establish that the model did not see the material.

The English/Lean pair is faithful only if it matches at the annotated level.
Two valid solutions to one IMO problem can intentionally use different methods:
these are useful statement-positive, argument-negative examples after review.

## OpenAI research source

The release identified is *Sharing AI progress in mathematics*, October 6, 2026:
https://openai.com/index/sharing-ai-progress-in-mathematics/

Repository and alignment metadata:
https://github.com/openai/math
https://github.com/openai/math/blob/main/lean/formalization.yaml
https://github.com/openai/math/blob/main/lean/README.md

The repository describes manuscripts at different verification stages, with Lean
formalizations available for a subset. `lean/formalization.yaml` supplies a
catalog of formalized results and associated manuscripts. This is a way to find
candidate counterparts, not a semantic match label. The Lean README recommends
building small portions of its shared library rather than the entire collection.

Verification instructions:
https://github.com/openai/math/blob/main/lean/ComparatorChallenges/README.md

Where applicable, follow the source's comparator instructions in addition to our
proof-integrity checks. Verification of a formal statement against a certificate
is distinct from agreement with the English manuscript or its proof argument.

Proposed pilot: 3-5 short, self-contained lemmas or theorem sections from distinct
manuscript families with identifiable source-level Lean counterparts and reviewable
dependencies. Prefer mathematical areas in which a qualified reviewer can judge
both sides. Identify the correspondence unit before viewing model predictions:
a paper, a theorem, a lemma, and a proof step are different evaluation units.

For every item record manuscript version and exact section, repository commit,
Lean declaration and source span, definitions, assumptions and imported context,
toolchain/dependency versions, artifact type, verification procedure and outcome,
and reviewer labels/rationale. If readable proof structure is unavailable, retain
the item for statement evaluation only; a certificate alone is insufficient for
our argument-fidelity experiment. Keep all companion papers and variants of a
result family together. Inspect overlap with training data and record uncertainty
about pretrained-model exposure; recent publication does not guarantee novelty
to every checkpoint or its later fine-tuning data.

Do not label every released pair faithful, and do not label disputed results
unfaithful merely because they are disputed. Review the actual correspondence
claim. Separate English-proof validity, formal validity, statement alignment,
and argument alignment; a failure in one is not a label for all the others.

## Shared test protocol

1. Define source-family exclusions and provisionally reserve candidates before
   building the training split. Keep a separate development set for rubric and
   prompt changes. Final test items stay untouched during tuning.
2. Have reviewers label the original English/Lean pairs independently of model
   scores and any generated controlled-language intermediary. Permit uncertain
   and missing labels; do not force expert disagreements into binary ground truth.
3. Add reviewed meaning-preserving paraphrases and subtle mismatches, including
   edits only to English while the valid Lean proof remains unchanged. Report
   constructed errors separately from naturally occurring correspondence errors.
4. Compare direct judging and controlled-language methods on identical source
   units. Preserve failures, unsupported fragments, timeouts and abstentions in
   coverage reports; do not silently drop long or difficult research proofs.
5. Report statement and argument metrics, false acceptance among valid formal
   proofs, calibration and coverage, plus error examples. Cluster uncertainty
   estimates by original IMO problem or research-result family, not mutated row.
6. Freeze source versions and label revisions in a small trackable manifest.
   Store downloaded repositories, manuscripts, certificates and build outputs
   under ignored `data/`/`artifacts/`; keep curated annotations and manifests in
   dedicated trackable directories outside those downloads. Record licenses and
   source links before redistributing text.

No benchmark labels or final test split have been produced yet. The pilot sizes
are feasibility targets, not claims of available independently verified examples.
