# Completed ProofNet informalization results

Fresh Qwen3-14B BF16 LoRA trained on 176 original ProofNet-derived pairs, with
36 validation pairs. English judge remained the original base model. Training
and the 54-pair evaluation finished November 13 at 11:16 Eastern; the external
case sequence finished at 11:26 Eastern. Validation completion NLL: 0.727638.

## Related-swap evaluation

All 54 pairs received translations and raw judgments. Eight translations hit
the 1,024-token cap: both pairings for four source proofs (four assumed matches
and four synthetic mismatches). These are abstentions, not semantic negatives.

| Metric | Result |
|---|---:|
| Scored / total | 46 / 54 |
| Correct / scored | 29 / 46 |
| Accuracy | 63.04% |
| Mismatch precision | 0.5750 |
| Mismatch recall | 1.0000 |
| Mismatch F1 | 0.7302 |
| Macro F1 | 0.5720 |
| AUROC | 0.9575 |
| Average precision | 0.9565 |

Confusion matrix, actual rows/predicted columns ordered mismatch,match:
`[[23,0],[17,6]]`. All scored synthetic mismatches were rejected, but so were
17/23 assumed matches. No test-set threshold fitting. Scores use the negative
saved YES probability for mismatch ranking; they are not calibrated confidence.
The earlier pretrained English intermediary scored 33/48 on a different scored
subset and with a different prompt protocol; this is not a controlled ablation.

## OpenAI cases

Both raw decisions were MISMATCH. The inverse translation was only 27 tokens
and omitted the argument and derivative requirement. The pressure translation
repeated a scalar/vector observation until the 2,048-token limit; that case
is an abstention for semantic scoring. The judge identified missing/repetitive
content, not the documented mathematical discrepancies. This does not establish
successful reproduction of the critique. Assessment is agent review, not
independent expert mathematical adjudication.

Raw sources: `artifacts/informalization-proofnet-14b-20261113` and
`artifacts/openai-proofnet-informalization-20261113`. Curated external outputs:
[generated-outputs.md](reports/openai-proofnet-informalization-20261113/generated-outputs.md).
Paper builders now include all 30 classification rows/matrices and nine protocol
curve figures. The paper includes the new result and curve, keeping older plots
available in the supplement. No inference was rerun for this reporting update.
