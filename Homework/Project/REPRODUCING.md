# Reproducing the project

Public repository: https://github.com/hotdogontology/CSCE883/tree/main/Homework/Project

Start in `Homework/Project`. The paper is `paper/main.pdf`; the separate evidence
supplement is `paper/supplement.pdf`. Presentation source and PDF are in
`presentation/`; `speaker-notes.md` allocates ten minutes across fourteen slides.

## Rebuild the reported results without a GPU

Use Python 3.11 or later. A minimal analysis environment needs `numpy`,
`scikit-learn`, `matplotlib`, and `pypdf`. The recorded workstation environment is
`requirements-lock-windows.txt`; `requirements.txt` lists the broader experiment
dependencies. Commands below assume `python` refers to your chosen environment.

```sh
python -m pip install numpy scikit-learn matplotlib pypdf
python scripts/restore_evidence.py --verify-only
python scripts/restore_evidence.py
python scripts/build_paper_results.py
python scripts/build_main_evidence.py
python scripts/build_informalization_paper_figure.py
python scripts/build_pipeline_figure.py
```

The evidence manifest hashes every archive and restored file. Restoration refuses
to overwrite a changed artifact. Archive entries are content-addressed to avoid
duplicating identical historical preparations. The exact train/validation/test
inputs, metadata, prediction scores, generated English, and text logs are retained.
Historical and superseded artifacts are included for audit, **not** pooled into the
reported evaluation. Use the paths and source hashes in `paper/results-snapshot.json`
to identify the reported runs. Reports under `reports/` provide curated provenance.

The builders recompute metrics from frozen outputs, not model inference. This
reproduces numerical analyses; it does not independently validate semantic labels.
Generated timestamps and PDF metadata may differ while metrics remain identical.
Mismatch is positive; coverage and protocol groups must be preserved.

## Build the PDFs

Install Tectonic or a TeX distribution with `acmart`, Beamer, and their dependencies.
Create `paper/build` and `presentation/build`, then run:

```sh
tectonic --outdir paper/build paper/main.tex
tectonic --outdir paper/build paper/supplement.tex
tectonic --outdir presentation/build presentation/slides.tex
```

PDFs distributed beside the sources are the reviewed build outputs; `build/`
directories and TeX caches remain ignored. The main report is eight pages including
references; the supplement is separate.

## Repeat the principal training experiments

The workstation used an NVIDIA RTX A6000 with 48 GB VRAM and 128 GB system RAM.
Install the recorded CUDA-compatible PyTorch environment and the training
dependencies. Training uses the full BF16 Qwen3-14B base and LoRA adapters, not
quantized weights. Allow storage for the base download and new checkpoints.

```sh
python scripts/download_model.py --repo Qwen/Qwen3-14B --manifest model-manifest-14b.json
python scripts/replay_informalization.py herald --output artifacts/replay-herald
python scripts/replay_informalization.py proofnet --output artifacts/replay-proofnet
```

These commands use the immutable model revision in the manifest and frozen split
files restored above. They train fresh adapters and run the original-model English
judge, preserving historical runs. Prompts, seed, LoRA settings, lengths, and loss
masking are in `scripts/informalization_pipeline.py`. The replay intentionally does
not automatically launch external-case inference. Its judgments are raw outputs;
exclude generation-limit cases when computing conditional classification metrics,
as implemented in `proofnet_informalization_pipeline.py` and the paper builder.
Hardware/library differences can change floating-point results; exact regeneration
of saved model decisions is not guaranteed.

Earlier protocols have their own experiment documents and scripts: `two-pass-experiment.md`,
`argument-experiment.md`, and related experiment documents in the project root.
Consult actual CLI help and their recorded manifests before starting an expensive
run. The 32B training probe was stopped; no tuned 32B result is claimed.

## Data provenance and distribution scope

ProofNet-Verified and Herald supply the original pairs; Faithform contributes to
the provisional pilot. Exact sampled/constructed inputs are in the evidence
archive, with preparation code and source manifests in the repository. See
`verified-data-manifest.json`, `references.md`, the paper bibliography, and the
individual experiment manifests for upstream locations and revisions. Original
corpus and software rights remain with their respective authors; this archive does
not relicense them. Source-corpus downloads and model weights are not bundled.

The four-family same-theorem diagnostic is agent-authored and not independently
human-adjudicated. Original ProofNet argument correspondence is assumed. Herald
acceptance is not accuracy. External OpenAI excerpts and pinned source details are
documented in `OPENAI_CASE_STUDY_PLAN.md`; the released outputs do not establish
reliable diagnosis of the cited discrepancies.

## Submission package

After committing the project, run `python scripts/package_submission.py`.
The ZIP contains tracked project code/documentation, report and supplement PDFs,
presentation source/PDF/notes, and the evidence archives. It includes a per-file
SHA-256 manifest and Git revision. It excludes weights, credentials, environments,
caches, and this ZIP itself. The ZIP is prepared locally for manual submission;
creating it does not submit anything to the course dropbox.
