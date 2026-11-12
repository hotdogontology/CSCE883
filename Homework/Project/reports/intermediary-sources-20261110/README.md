# Intermediary libraries and larger-model engine investigation

Reviewed 2026-11-10. Sources are pinned and downloaded under ignored
`data/intermediary-sources/`; `manifest.json` records archive hashes. This work
supports the paired English/Lean argument-correspondence experiment. Library
examples and successful compilation do not establish that a generated view
preserves its source argument.

| Project | Pinned revision | License | Compatible environment |
| --- | --- | --- | --- |
| Verbose Lean | `ea52f4bf6c60d986cb3fa2a5b7d7a8429b886eed` | Apache-2.0 | Lean4.31.0, mathlib4.31.0 at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` |
| Natural Lean | `d7d0d5de14c0404a9e4d900d76fac2f19d304a56` | MIT; bundled notices retained | Lean4.36.0-rc2, pinned Aesop/Batteries, no Mathlib dependency |
| Colibri | `0a5504a1dc64f86fcd0fe7db298b0448c730e7e6` | Apache-2.0; bundled notices retained | Windows native CPU/Vulkan; published CUDA builds support compute capability8.0+ |

Sources: [Verbose configuration](https://github.com/PatrickMassot/verbose-lean4/blob/ea52f4bf6c60d986cb3fa2a5b7d7a8429b886eed/lakefile.toml),
[Natural configuration](https://github.com/medovina/natural_lean/blob/d7d0d5de14c0404a9e4d900d76fac2f19d304a56/lake-manifest.json),
[Colibri Windows documentation](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/windows.md).

## What was prepared

The generation prompts use compact syntax guides in
`prompts/intermediary-verbose-lean.txt` and
`prompts/intermediary-natural-lean.txt`, adapted from the pinned source syntax
and examples. They require preserving assumptions, witnesses, claims and proof
steps. A translation branch does not receive the other branch's source proof.
The guides are contextual instructions, not generator fine-tuning data.

Natural Lean and its full upstream example target built successfully locally.
The official Lean4.36.0-rc2 Windows archive was SHA256-checked against release
metadata (`ad1ed478bbde27cb178c46d8dfd4721d0d5424729280991a8d54537589e1949e`).
The minimal Natural Lean example in our guide also passed actual compilation.
The example library has limited mathematical coverage and supplies custom
definitions; arbitrary ProofNet Mathlib names will not become available merely
by importing Natural. This can limit coverage of the intermediary experiment.

The official Lean4.31.0 archive for Verbose Lean was also verified
(`f73208f53dcdc901745cb35fc916c476e0e18ed0856937740e46d07848f57f19`). The first
dependency checkout/cache attempt encountered Windows path-length limits. A
shorter isolated build copy at `data/vl431` resolved them. All8,538 Mathlib cache
files decompressed, and the complete Verbose library including English/French
example files built successfully (1,267 build jobs). The explicit English
example target also passed. Build provenance and executable paths are in
`data/intermediary-sources/verbose-lean4-setup.json`, now complete.

`scripts/check_intermediary_compilation.py` compiles cached generated code under
the matching environment, with a time/heartbeat/memory limit and a conservative
screen for admissions, executable extensions and non-library imports. It saves
a separate ledger and never changes semantic predictions or generation caches.
Compilation failures, unavailable environments, incomplete generations and
admitted proofs remain separate statuses. Compilation is not an independent
argument-fidelity label. Transitive axiom closures are not audited by this
initial checker. Six checker tests passed, including real Lean4.28 and Natural
Lean compilation; source admissions and executable commands were rejected.
Two further real Verbose Lean probes passed: an English tactic inside native
`example ... := by` syntax, and the complete `Example/Given/Assume/Conclusion/
Proof/QED` form used in the guide. Results are in `verbose-compiler-smoke.json`.
The frozen first checker conservatively scans string literals as well as code:
a title containing a word such as `constant` can be screened out. Such cases
are screening rejections, not Lean compiler failures, and may lower qualified
coverage. Review and replay these with a revised checker before drawing any
conclusion about dialect expressiveness from their count.

## Translation training data search

No ready-made, curated dataset of paired ordinary English/native Lean and
Verbose Lean or Natural Lean translations was located in the upstream
repositories, their linked teaching resources, or targeted searches. This is a
search outcome, not a claim that no such data exists anywhere.

Verbose Lean provides English examples and links to a teaching course; that
course's README says full solution files are available from the author on
request. No request was sent. Natural Lean supplies example mathematics and
syntax documentation, rather than an annotated parallel translation benchmark.
Therefore no separate dialect-generation adapter was trained during this
stage. Training on auto-produced pseudo-translations would be a new assumption
and a distinct experiment, not the verified translation dataset requested here.
[Verbose repository](https://github.com/PatrickMassot/verbose-lean4/tree/ea52f4bf6c60d986cb3fa2a5b7d7a8429b886eed),
[teaching course](https://github.com/PatrickMassot/proofs_with_lean),
[Natural examples](https://github.com/medovina/natural_lean/tree/d7d0d5de14c0404a9e4d900d76fac2f19d304a56/examples/Natural/Examples).

## Colibri findings

Colibri is worth a controlled follow-up for larger inference, but its advertised
large-model results cannot be treated as evidence for our unquantized workload.
The engine explicitly supports dense Qwen3 as well as mixture-of-experts models.
Current Windows CUDA releases support this machine's Ampere-class GPU. Most
published large-model performance examples use quantized weights and expert
streaming; dense Qwen3 activates all layers, so that benefit does not transfer
automatically. [Supported GGUF architectures and formats](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/gguf.md).

A read-only planner run on the existing original 14B checkpoint succeeded. It
recognized `qwen3`, the RTX A6000 with compute capability8.6, and zero routed
experts. It identified RAM bandwidth as the expected dense-model bottleneck.
The full raw plan is ignored; a small reproducible record is
`colibri-planner.json`. No Colibri model inference, speed measurement, larger
checkpoint download, engine binary installation or LoRA training occurred.

Precision needs explicit attention. The raw-safetensors Qwen engine normally
quantizes dense weights to int8 during loading. `COLI_DENSE_I8=0` retains the
float32 path; `COLI_DENSE_BITS=16` instead retains float16 matrices, which entails
converting original BF16 values to FP16. F16/BF16 GGUF files are also supported,
but their CPU matrices expand to float32, and the documented CUDA tiled BF16
path converts to FP16. Thus choosing a BF16 file or the launcher's `quality`
policy alone does not demonstrate equivalence to our Transformers BF16 run.
[Engine loading implementation](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/c/qwen36.c),
[format implementation notes](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/gguf.md).

A roughly32B dense model needs roughly64GB for16-bit weights before runtime
buffers, so it exceeds48GB VRAM and needs CPU/GPU partitioning. Float32 host
copies alone approach128GB before Windows and runtime overhead. These are
capacity estimates, not measurements of Colibri on this workstation. A future
probe should first use the existing14B checkpoint, explicit precision settings,
a fixed prompt and reference logits; measure actual peak RAM/VRAM and throughput
before acquiring a larger checkpoint. The current14B experiment remains on
original BF16 weights and ordinary LoRA.

Reproduce the completed planner-only probe:

```powershell
.\.venv\Scripts\python.exe scripts/probe_colibri_planner.py
```

Compile generated caches after an architecture run:

```powershell
.\.venv\Scripts\python.exe scripts/check_intermediary_compilation.py --cache-dir artifacts/hard-related-20261110/generation-cache --output artifacts/hard-related-20261110/compilation
```
