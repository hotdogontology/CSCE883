# Homework 3 — Taylor Belcher

The report is `hw3_solutions-tbelcher.pdf`, built from `hw3_solutions-tbelcher.tex`. The three notebooks are:

- `hw3_question2c-tbelcher.ipynb`: float64 analytic, automatic, and central finite-difference gradient verification.
- `hw3_question4-tbelcher.ipynb`: DNA classification, frozen-model shuffling, and the neighboring-base investigation.
- `hw3_question5-tbelcher.ipynb`: superconductivity regression and the one/two/three-hidden-layer investigation.

Use Python 3.12. The top-level `requirements.txt` records the original dependency versions for all three notebooks, including Q2C's Autograd dependency. `requirements-python312.txt` provides a portable pip installation with Matplotlib 3.10.7, which has Python 3.12 wheels; the original saved run used the system-provided Matplotlib 3.6.3, which has no Python 3.12 wheel. From this directory, install a CPU-only PyTorch wheel with `python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu`, then install the remaining pinned requirements with `python -m pip install -r requirements-python312.txt`. Select that Python environment as the notebook kernel in VS Code or Jupyter. A standalone Jupyter interface is optional when using VS Code.

Run each notebook from its first cell to its last, one notebook at a time. Neural computations use the CPU and two PyTorch threads; no GPU is needed. Keep the original directory layout, including `../Homework3_revision/Homework3_revision/` with the supplied data files. Q4 and Q5 notebooks work when the notebook working directory is this directory or the course repository root. The README files inside `question4/` and `question5/` also describe running their standalone scripts.

The notebooks record dependency versions, hardware, seeds, configurations, checks, and elapsed runtime. Q4 and Q5 save their preregistered plans before fitting and finish all model selection before test evaluation. Their original result files, split indices, checkpoints, and figures are under the respective `results/` directories. Rerunning Q4 or Q5 overwrites that question's result artifacts. The report describes the original saved runs; if you rerun on different hardware or software, runtime and numerical results may differ and the report should be checked against the new outputs.

Build the PDF from this directory with `latexmk -pdf -interaction=nonstopmode -halt-on-error hw3_solutions-tbelcher.tex`. A TeX Live installation with the packages used by the source is required. Figures are loaded from `question4/results/` and `question5/results/`.

AI assistance is disclosed at the start of the report for Questions 1–3 and within Questions 4 and 5. Experiment interpretations, accepted suggestions, and implementation checks are recorded in the report.
