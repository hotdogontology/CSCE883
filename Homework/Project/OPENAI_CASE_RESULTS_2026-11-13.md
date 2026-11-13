# OpenAI informalization case study — November 13

Both selected cases completed through the trained Qwen3-14B informalizer and
the original English-pair judge. Both received MISMATCH. Neither diagnostic
explanation reliably localized the literature-documented discrepancy. Do not
report this as 100% semantic-detection accuracy or two demonstrated successes.

| Case | Translator input/output tokens | Judge decision | Assessment |
|---|---:|---|---|
| Lemma 8.6 inverse estimate | 2,563 / 670 | MISMATCH | Correct flag; inadequate explanation. The translation omits the explicit input-derivative requirement; the judge emphasizes terminology and abstraction rather than m+4 versus m+5. |
| Lemma 10.5 pressure-flux subargument | 8,396 / 292 | MISMATCH | Correct flag; inconclusive detection of the actual source discrepancy. Translation summarizes the wrapper, leaves the bound unspecified and omits the supplied helper arguments. Judge mainly rejects this loss of detail. |

## Procedure and evidence

- Used the saved Herald-trained adapter from `artifacts/informalization-14b-20261112/adapter`, with base Qwen3-14B BF16. No new training or direct baseline.
- Pinned OpenAI source revision `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`; source/PDF hashes and 41 selected declarations are in [preparation.json](reports/openai-informalization-20261113/preparation.json).
- Original English was manually normalized into scoped subarguments from the manuscript. Key equations were checked visually. These are subargument tests, not whole-lemma or whole-paper tests.
- Translator input contained selected Lean definitions and helper bodies plus the target declaration; no original English, critique text or expected label. The helper selection is not a complete transitive dependency closure.
- Judge input contained only original English and generated English plus a neutral scope instruction. Adapter disabled during English judging. The YES/NO next-token decision uses the existing judge prompt. An independent explanatory generation uses an additional explanation instruction, without receiving the decision or critique.
- Greedy generation, thinking disabled, no input truncation, 2,048 translation output limit and 1,536 explanation limit. No output hit its limit. Both inputs exceed the 2,048-total-token training cap; the external test is a substantial context/domain shift.
- The run reported peak PyTorch allocation of 53.80 GiB. This is an allocator reading under Windows/WDDM, not a claim that the 48-GB card physically holds that much VRAM. The run completed without an out-of-memory exception; paging was not separately measured.

Full generated English and explanations: [generated-outputs.md](reports/openai-informalization-20261113/generated-outputs.md).
Raw decisions and outputs: [results.jsonl](reports/openai-informalization-20261113/results.jsonl).
Run configuration and checkpoint hashes: [run.json](reports/openai-informalization-20261113/run.json).

## Interpretation

The inverse translation retains the Fourier coefficient inequalities and the
weight-to-the-minus-four sum, but does not state what derivative assumptions
the bound C represents. The judge's description of the two accounts as
mathematically distinct because one uses derivative words and seminorms is not
a satisfactory diagnosis: these can encode the same kinds of objects.

The pressure translation says the bound is a "specific expression" involving
the cutoff norm and dissipation root. It never writes that expression. It also
does not explain the Riesz/Sobolev route present in the supplied helpers. The
judge identifies missing detail in that translation, but cannot establish from
that alone which discrepancies originated in the actual Lean proof. Its claim
that the account does not use the tools in the English proof overstates what
absence from a summary establishes.

These are two literature-selected mismatch families with no faithful controls.
The flags agree with the expected labels, but the explanations are confounded
by translation omissions. This run provides evidence that the current pipeline
needs better dependency-aware informalization before its flags can serve as
actionable diagnoses on these cases. This is an agent assessment of recorded
outputs, not independent expert mathematical adjudication.

## Next improvement (not run)

Informalize named helper lemmas separately, preserve each exact mathematical
bound and its assumptions, then synthesize a theorem-level account from those
translations. Evaluate the revised method on both source cases and independently
assessed faithful controls, preserving this first run. Do not insert the known
discrepancy into the translator or judge prompt to manufacture a successful flag.
