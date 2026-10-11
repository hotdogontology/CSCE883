# Homework 3 review — 11 October 2026

The audit found no substantive error in the derivations, numerical results, or declared experimental protocols. It covered the assignment PDF, LaTeX report, all three notebooks, both experiment scripts, documentation, and saved artifacts.

## Independent verification

- Q1: checked the chain-rule bound and residual Jacobian; independently reproduced CNN dimensions and parameter counts in PyTorch.
- Q2: checked the five derivatives, simultaneous updates, Softplus limit, and ReLU convention. Independent float64 PyTorch differentiation agreed with both sets of analytic weight gradients.
- Q3: checked the leakage explanation, test-selection bias, validation/stopping protocol, and material grouping.
- Q4: reconstructed features and splits, refitted the fixed logistic regressions, and reloaded neural checkpoints. Predictions, validation minima, and both accuracy metrics reproduced.
- Q5: reconstructed splits and train-only scalers; independently verified ridge selection, neural predictions, inverse scaling, subgroups, and every metric.
- Recomputed means, sample standard deviations, and paired differences; report tables matched saved results at displayed precision.
- Executed all three notebooks in separate fresh Jupyter kernels, sequentially, using isolated copies in `/tmp`. Q4 and Q5 exactly reproduced their predictions, metrics, selected epochs, and validation losses; Q5 also reproduced subgroups. Original artifacts and runtimes were preserved. These are reproducibility checks, not new independent experiments.
- Rebuilt the 21-page PDF with no errors or overfull lines.

## Corrections

- Called Q1's sigmoid network scalar rather than linear, corrected Kronecker's spelling, and clarified the weight-magnitude constraint.
- Replaced the definite claim about training time with the gradient-attenuation implication supported by the bound.
- Restored Q2A's explicit pre-update-weight statement and repaired a Q2C sentence.
- Added Q2C's saved comparison runtime and CPU to the report.
- Added shared reproduction instructions and requirements, including Q2C's Autograd dependency.
- Added `requirements-python312.txt`: the original system-provided Matplotlib 3.6.3 has no Python 3.12 wheel. The portable file pins Matplotlib 3.10.7 instead. Its wheel was verified, and all six Q4/Q5 figures regenerated successfully with that version. Other package pins remain unchanged. A completely clean dependency installation was not performed.

## Interpretation limits

Q4 conclusions concern sequence statistics, and Q5 conclusions concern the supplied row splits. Q5's repeated feature profiles prevent treating random-row performance as evidence for unseen material families. The depth experiment changes parameter count as well as depth; a third layer's smaller advantage is not established as statistically significant. These are limitations of the experiments, not code errors.

No architecture, training configuration, split, test threshold, subgroup, or experimental conclusion was changed in response to the reproduction runs.
