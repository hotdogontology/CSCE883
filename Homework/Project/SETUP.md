# Local research environment

The native Windows environment is in `Homework/Project/.venv`. The Microsoft
Visual C++ x64 redistributable is required and has been installed. Python 3.12,
CUDA-enabled PyTorch, Transformers, PEFT, TRL, bitsandbytes, dataset/evaluation
packages, and Jupyter are installed. Qwen3-8B is the selected first checkpoint;
`model-manifest.json` records revision and download-completion status.
See [methodology.md](methodology.md) for the experiment design.

Download/resume and run the model from this directory:

```powershell
.\.venv\Scripts\python.exe scripts\download_model.py
.\.venv\Scripts\python.exe scripts\run_model.py
.\.venv\Scripts\python.exe scripts\run_model.py --prompt "Explain what Lean checks in a proof."
```

The download script reuses the pinned revision, downloads safetensors/config/tokenizer
files into ignored `data/models/Qwen3-8B/`, and verifies sizes and published weight
hashes. The inference runner loads only local files in BF16 on the GPU, with
remote code disabled and thinking disabled. Its default prompt is a readiness
smoke test; arbitrary prompt results are not validated mathematical judgments.
The latest run report is written under ignored `artifacts/`.

## Zero-shot pair judgments

From the project directory:

```powershell
.\.venv\Scripts\python.exe scripts\judge_pairs.py
.\.venv\Scripts\python.exe scripts\judge_pairs.py --limit 5 --offset 0
```

The default input is `data/herald/review-unlabeled.jsonl`; the default limit is
30. Use `--input path/to/another.jsonl` for the same field schema. The model loads
once per run and processes pairs sequentially on the GPU. It uses the fixed
`prompts/fidelity-v1.txt` rubric, non-thinking mode and greedy generation.

Every run creates a new ignored `artifacts/zero-shot/<UTC-run-id>/` directory:

- `predictions.jsonl`: binary predictions (`true`/`false`), exact messages,
  raw responses, source IDs/revisions/row hashes, token counts and status.
- `run.json`: model revision, complete prompt/hash, input-file hash, generation
  settings, package versions, aggregate counts, timings and GPU memory use.
- `summary.csv`: compact row-by-row YES/NO table.

No source records or review labels are modified. Only English statement/proof,
Lean header and completed `formal_proof` are sent; admitted statement templates,
`commented_proof` and review fields are excluded. Missing evidence, oversized
inputs, out-of-memory failures and nonconforming responses remain explicit
statuses with null predictions. Inputs over 8,192 tokens are skipped rather
than silently truncated; the limit can be adjusted with `--max-input-tokens`.

This runner does not invoke Lean or expand imported definitions/lemma bodies.
Outputs are unvalidated zero-shot predictions, not human labels, accuracy scores,
calibrated confidence or evidence of fine-tuning. GPU results can vary across
hardware/library versions even with a recorded seed and greedy decoding.

Guard tests: `.\.venv\Scripts\python.exe -m unittest discover -s scripts -p test_judge_pairs.py -v`.

From this directory in PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\check_gpu.py
.\.venv\Scripts\python.exe scripts\audit_herald.py
.\.venv\Scripts\python.exe -m jupyterlab
```

In VS Code select `.venv/Scripts/python.exe` as the interpreter and choose the
`CSCE883 correspondence` notebook kernel once registered. No environment
activation is required when using the explicit Python path above.

Lean is managed by elan; this project's `lean/lean-toolchain` pins Lean 4.11.0
to match Herald. `lean/lake-manifest.json` pins Mathlib and transitive dependencies.
Open `lean/` as a VS Code folder when working on Lean files. In a new terminal:

```powershell
cd lean
lake build
lake env lean generated\HeraldReplay.lean
```

The replay file is created by `audit_herald.py`. It renames the target declaration
to avoid a duplicate Mathlib name. Passing this probe does not certify all corpus
rows, semantic correspondence, or absence of circular target dependencies.

`setup.ps1` can recreate the stack after Python, Git, and elan installation;
`setup.ps1 -SkipInstall` reruns the GPU and Lean smoke checks. The requirements
file requests compatible current packages. Use `requirements-lock-windows.txt`
for the exact installed package versions; install its torch build from the CUDA
12.8 index using `--extra-index-url https://download.pytorch.org/whl/cu128`.

Restart VS Code after installing Python/elan to refresh PATH. The PyTorch wheel
includes its CUDA runtime; a separate CUDA Toolkit is unnecessary for these
prebuilt packages. WSL2 remains an option if a later training backend needs Linux;
the initial stack is native Windows. FlashAttention/vLLM are not prerequisites
for the proposed classifier experiment.

Ignored local directories include the virtual environment, corpus downloads,
model checkpoints, experiment artifacts, and Mathlib build cache. Setup logs
and machine-specific reports go in `artifacts/`; keep human-reviewed dataset
labels and their provenance separate from those generated audit files.
