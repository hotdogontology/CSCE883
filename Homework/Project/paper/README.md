# Paper workspace

- `main.tex`: ACM prose draft with abstract, background, experiment summaries,
  and detailed informalization methods/results. Compiled length: 8 pages including
  references. Taylor Belcher and ChatGPT (explicit AI collaborator) are authors.
  All 30 metric rows/matrices remain. Main figures show related-swap curves,
  earlier intermediary curves and Herald training/judge counts; other plots
  remain in the supplement. Bold scores are maxima within protocol/evaluation
  groups, including ties; singleton groups are not highlighted. Intermediary
  comparisons still have unequal scored subsets. Draft awaits Taylor's review.
- `supplement.tex`: preserved full inventory, matrices, plots and diagnostics.
- `references.bib`: starter bibliography; complete publication metadata before submission.
- `tables/`, `figures/`: generated metric tables, confusion matrices and ROC/PR plots.
- `results.csv`, `results-snapshot.json`: numerical snapshot, source paths and hashes.
- `build/main.pdf`: local compiled preview (ignored).

Format: main paper uses ACM `acmart`, `sigconf,nonacm`; the supplement retains
the single-column manuscript layout. `conference.tex` is an alias for the main
paper. Course requirements: [PROJECT_REQUIREMENTS.md](../PROJECT_REQUIREMENTS.md).
Target 6–8 pages. The 14-page supplement is separate from the
report limit; it also retains larger individual plots and additional diagnostics.
Official template guidance:
https://www.acm.org/publications/proceedings-template

From the project directory:

```powershell
.venv\Scripts\python.exe -X utf8 scripts/build_paper_results.py
.venv\Scripts\python.exe -X utf8 scripts/build_main_evidence.py
.venv\Scripts\python.exe -X utf8 scripts/build_informalization_paper_figure.py
downloads\tectonic\tectonic.exe --outdir paper/build --keep-logs paper/main.tex
downloads\tectonic\tectonic.exe --outdir paper/build --keep-logs paper/supplement.tex
```

The first command reads existing predictions on CPU; it does not run models or
modify the live training job. It overwrites generated tables/figures/snapshots,
never `main.tex`. Completed experiment results are frozen. The ProofNet run and
OpenAI follow-up are complete and included: 29/46 scored correct out of 54 attempted,
eight abstentions; external translation failures are reported separately. The
main paper includes its ROC/PR curve and updated tables.

Conventions: mismatch is positive; matrix order is mismatch, match on both axes.
False acceptance is FN; false rejection is FP. Precision/recall/F1 with a zero
denominator use zero. ROC and average precision use saved continuous scores,
preferably logit margins to avoid saturated probabilities; no thresholds are fit.
Coverage is scored/total. Unlabeled corpora receive decision-count tables only.
Different protocols and conditional scored subsets must not be pooled.

The November 13 request authorized prose based on the original proposal and an
explicit AI co-author. The prior outline is in `archive/main-outline-20261113.tex`.
The supplement includes contributions. Human review and mathematical adjudication
remain pending.

Final PDFs are also published as `main.pdf` and `supplement.pdf`. The main report
includes the pipeline diagram and public repository link. See [REPRODUCING.md](../REPRODUCING.md)
for evidence restoration and the presentation/submission package.
