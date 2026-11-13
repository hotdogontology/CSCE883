# Data for the English intermediary pipeline

Research recommendations, 2026-11-12; not a new training run or approved dataset
freeze. See informalization-experiment.md for the governing design.

## Stage one: Lean proof to English account

User clarification after this survey: reverse-direction training on Herald is
the intended approach. Stage one needs paired translation supervision, not the
binary argument-match labels needed by stage two. Data-quality assessment serves
translation evaluation and is not a prerequisite to accepting this approach.
English informalizations also have standalone value for human sanity checking.

Reversing paired formalization data is a valid supervised learning setup when
the English describes the actual formal argument. The input must include the
statement, full proof and required context; the target must describe reasoning,
not just restate the theorem. Do not show the target English at inference.

| Existing source | Recommended use | Qualification |
| --- | --- | --- |
| Herald_proofs | First bulk informalization candidate | Local audit has 44,553 rows with formal_proof, informal_proof and header. Original paired rows, not swapped negatives or classifier predictions, provide supervision. Argument fidelity remains to be audited. |
| ProofNet-Verified | Smaller supplementary source or reserved transfer evaluation | Our corrected extraction supplies 365 positive source pairs with full Lean proof bodies. User-authorized correspondence assumption is not independent certification that every proof route agrees. Use archived proof bodies, not placeholder fields. |
| ProofFlow | Selected paired generated artifacts for supplementary training; English proof graphs for decomposition | Main English/graph release and separate generated Lean artifacts have different coverage. Require complete matched pairs; generated code alone does not certify argument fidelity. |
| Faithform | Local inference/statement translation auxiliary | Only matching translations. Do not reverse perturbed or unfaithful translations into the original English. Not a substitute for full proof-body training; local examples can contain sorry. |
| Mathlib / IMO-Steps | Formal context and decomposition sources | Formal code alone does not supply English argument targets. Additional informalization/annotation is needed. |
| FaithSieve / ProofLoc | English error-localization auxiliary | Existing inspected data do not supply paired Lean proof targets. |

Herald card: https://huggingface.co/datasets/FrenzyMath/Herald_proofs
ProofNet-Verified: https://github.com/marcusm117/ProofNet-Verified
Local counts come from existing project audits/extraction, not newly downloaded
versions. This survey does not promote automatically generated English to gold.

## Stage two: English argument comparison

**NaturalProofs / ProofWiki** is the strongest lead for human-written alternative
proofs. NaturalProofs releases raw JSON by source (ProofWiki, Stacks and textbooks),
with roughly 30,000 theorem statements/proofs across the corpus. ProofWiki
explicitly supports multiple proofs per theorem. MIRB also documents multiple
associated ProofWiki proofs in its NaturalProofs-derived retrieval task. We have
not yet counted extractable alternative-proof groups in a local download.

- https://github.com/wellecks/naturalproofs
- https://arxiv.org/abs/2104.01112
- https://proofwiki.org/wiki/Help:Multiple_Proofs
- https://openreview.net/pdf?id=0pJtN4S9d6

These are theorem/proof and retrieval data, not pre-labeled same-argument pairs.
Two different proof texts can still express the same argument; alternative proof
numbers are candidates, not automatic mismatch labels. Preserve source licenses;
the code license is not a blanket license for all underlying text.

**Open Proof Corpus (OPC)** provides English model-generated solutions with human
scores and feedback, plus reference solutions. The paper reports approximately
5,000 human-evaluated proofs across more than 1,000 problems. The live viewer
explicitly contains repeated problem_id values with different solutions (e.g.
BMOSL_2016_18), so same-problem grouping is directly supported. Human feedback
helps identify omissions and invalid steps, but correctness scores are not
argument-correspondence labels. Inspect uncertainty and reference-issue fields.

- https://huggingface.co/datasets/INSAIT-Institute/OPC
- https://arxiv.org/abs/2506.21621
- Dataset license: CC-BY-NC-SA-4.0.

ProofFlow's English proof graphs and ProofLoc's error annotations remain useful
auxiliaries for steps/dependencies and omissions. Neither automatically labels
two English proofs as the same argument.

## Recommended construction and evaluation

1. Audit Herald and corrected ProofNet pairs for full-body reversible supervision.
   Start with Herald bulk training; decide whether to reserve ProofNet for transfer
   evaluation before mixing it into training.
2. Inspect NaturalProofs proof groups and OPC same-problem groups. Build positives
   from independently reviewed equivalent presentations; build hard negatives
   from confirmed distinct routes and identified semantic changes. Generated
   paraphrases can scale training but must retain provisional provenance.
3. Balance labels within each source and presentation style. Do not use one corpus
   only for positives and another only for negatives. Keep uncertain cases apart.
4. Split theorem/source families before generating pairs or translations. Check
   cross-corpus overlap (including mathlib and ProofWiki-derived material) and keep
   test families unseen by both stages.
5. Evaluate translator fidelity, English comparator and end-to-end English/Lean
   mismatch detection separately. The comparator is now an explicit pipeline
   component; its English-only score alone still does not measure end-to-end fidelity.

No ready-made, verified binary same-argument dataset was established by this
search. The promising finding is that natural same-theorem proof material exists;
we need to supply argument-pair labels, not invent all underlying proofs.
