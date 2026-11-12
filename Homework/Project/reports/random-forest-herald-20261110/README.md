# Random forest / Qwen Herald comparison

Completed 2026-11-10. Both forests use the same original 510-row training set
and fixed settings as the earlier baseline. Original validation and diagnostic
metrics reproduced. No Herald labels or Qwen predictions were used for training.

Coverage is identical for all four models: **44,537 pairs**, excluding the same
16 pairs that exceeded Qwen's context limit. IDs are unique and equal across
all four prediction files. Forest inference used batches of 128 to bound memory.

| Model | YES | NO | YES rate |
| --- | ---: | ---: | ---: |
| English-only forest | 44,531 | 6 | 99.9865% |
| English + Lean forest | 44,535 | 2 | 99.9955% |
| Untuned Qwen3-14B | 34,901 | 9,636 | 78.3641% |
| LoRA Qwen3-14B | 44,385 | 152 | 99.6587% |

Both forests accept nearly every Herald pair. Agreement with tuned Qwen is
99.67% and 99.65%, respectively, largely reflecting the dominant YES decision.
Agreement is not validation: Herald has no independent argument-correspondence
labels, and the accuracy of these predictions remains unknown. Similar prediction
rates do not establish equivalent semantic capabilities.

The forests disagree on eight pairs and reject disjoint sets. Both-language
forest differs from untuned Qwen on 9,634 and tuned Qwen on 154 pairs.
Full pairwise tables, exact counts and input/code hashes are in `summary.json`.
Raw scores/predictions remain ignored in `artifacts/random-forest-herald-20261110/`.

See [related-proof pilot](../relatedness-20261110/README.md) for the controlled
comparison on closer proof swaps. The English-only forest's acceptance of coherent
English bundles and nearly all Herald pairs illustrates why statement/proof
coherence alone is insufficient for the intended argument-correspondence task.
