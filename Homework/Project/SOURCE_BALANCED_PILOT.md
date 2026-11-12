# Source-balanced correspondence pilot

Authorized and implemented 2026-11-12. This supersedes the proposed ProofNet-only
positives / Faithform-only negatives construction, not the preserved old results.

## Dataset

32 examples: 16 training, 8 validation, 8 test. Within EVERY split, ProofNet and
Faithform each contribute exactly equal numbers of positives and negatives and
equal total counts. This removes the deterministic dataset-source shortcut.

ProofNet uses existing assumed positive / related-swap negative pairs and keeps
their original splits. Donor and recipient groups are checked across the full
inherited split, including unselected records. Shorter complete pairs are selected
to reduce the length gap; evidence is never truncated. Existing related swaps
are retained rather than inventing additional edits without justification.

Faithform uses16 explicitly reviewed local pairs from four source problems in
the archived first100 LLM rows. Training: gsm8k-201/202; validation:203; test:204.
Each source problem has two positive and two negative examples. This is an
ordered convenience pilot, NOT a representative benchmark sample. Reviews are
provisional agent judgments with per-example rationale, not independent human
certification. Negative examples include added assumptions, omitted assumptions,
tautological reformulations, and changed quantification. Labels are not copied
from is_perturbed or proof_result.

Faithform's original autoformalizer output, not its separate refutation, supplies
the formal evidence. Its proof bodies are placeholders: it tests local inference
translation, while ProofNet supplies full argument comparisons. This mixed scope
is explicitly retained and metrics are broken down by source. The aggregate is
not a certified full-proof correspondence score.

## Inputs and safeguards

Only `input.english` and `input.lean` reach the judge. Labels, source, split,
upstream outcomes, model names and review rationale remain external metadata.
Generated reasoning and Lean comments are stripped. Target theorem names are
normalized. English dependency context is retained. All variants of a source
problem stay together. Build checks verify source/class balance, source/donor
split isolation, exact input duplicate isolation and extraction success.

All actual inputs fit the562-token maximum measured with the32B tokenizer.
The script refuses silent truncation and any example exceeding4096 tokens.

Reviewable outputs:

- [Dataset manifest](reports/source-balanced-20261112/dataset-manifest.json)
- [Side-by-side examples and label rationale](reports/source-balanced-20261112/review.md)
- [Shortcut controls](reports/source-balanced-20261112/shortcut-controls.json)

## Secondary controls

Train-only fits, evaluated on frozen validation/test splits:

| Control | Validation | Test |
| --- | ---: | ---: |
| Source-only random forest | 50% | 50% |
| Length-only random forest | 62.5% | 50% |
| English-only character TF-IDF/logistic | 50% | 50% |
| Lean-only character TF-IDF/logistic | 50% | 50% |
| Paired lexical TF-IDF/logistic | 50% | 50% |

These tiny-sample controls do not prove shortcut freedom. Several classifiers
predict mostly/all one class; chance performance is weak evidence. They are
dataset diagnostics, not the main semantic model results. Do not repeatedly
tune construction against test performance. No topic-matching claim is made:
the mathematical source/topic gap remains and needs larger reviewed coverage.

## 32B run

Checkpoint download completed with recorded size and LFS SHA-256 verification.
Original Qwen3-32B revision9216db5781bf21249d130ec9da846c4624c16137.
Runner: scripts/run_source_balanced_32b.py. Live state:
artifacts/source-balanced-20261112/qwen32/job.json.

Uses unquantized BF16, a static GPU prefix and CPU suffix, explicit autograd-aware
tensor transfers, and no inference-only offload hooks. GPU base-weight budget35GiB
leaves activation headroom. Baseline evaluation precedes training. Longest training
example must pass finite loss, gradients for all adapter tensors, and an optimizer
step; adapter weights are restored after the probe. Only then: fresh rank16 LoRA,
one epoch, learning rate1e-4, accumulation4, seed883. No hyperparameter search or
selection on test. Reevaluate identical held-out pairs and report mismatch
precision/recall/F1, confusion matrices and accuracy by source as well as overall.

One startup was aborted after detecting a tokenizer API return-type difference,
before predictions/training. Corrected runner explicitly requests token IDs and
checks their types. Archived startup directory is not an experimental result.

Execution may be slow on CPU; consult the job file before claiming completion.
Do not infer successful fine-tuning from a successful model load or baseline.

## Reproduction

Run in the project environment:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_source_balanced_pilot.py
.\.venv\Scripts\python.exe -X utf8 scripts/source_balanced_controls.py
.\.venv\Scripts\python.exe -X utf8 -u scripts/run_source_balanced_32b.py
```

The model runner refuses an existing output directory to protect completed runs.
Weights, input corpora, checkpoints and raw predictions remain gitignored.
