# Homework 3, Question 4

Run `hw3_question4-tbelcher.ipynb` (in the parent directory) from top to bottom, or run `python run_question4.py` from this directory. Both contain the same experiment. Use Python 3.12 and install the packages in `requirements.txt`. A notebook interface additionally requires Jupyter and ipykernel. For CPU-only PyTorch, install `torch==2.14.1` from `https://download.pytorch.org/whl/cpu` before installing the remaining requirements.

The input files are read from `../../Homework3_revision/Homework3_revision/`: `humanvsran.seq.txt` and `humanvsran_label.txt`. Keep the supplied directory layout. No downloads of data are needed.

The first code cell records the hypothesis, predictions, challenge criteria, architectures, and single candidate training configuration before fitting. The experiment uses split seeds 11, 22, and 33; initialization seeds s+1000; loader seeds s+2000; and shuffling seeds s+100. It reserves the test set first, then creates training and validation subsets. No learned preprocessing is applied to the count or one-hot features. All model checkpoints are selected before any test evaluation. Re-running overwrites the result files.

`results/` contains the declared plan, data audit and file hashes, environment and runtime, split indices, selected neural checkpoints, per-epoch loss histories, per-run metrics, sample-standard-deviation summaries, paired differences, test predictions, and three figures. Notebook outputs retain the printed audit, training records, metrics, and runtime. The total timer starts after imports and excludes package installation; per-model training times are in `training.csv`.

Feature checks compare ACGTA with hand-counted nucleotide and adjacent-pair frequencies. Other assertions verify labels, one-hot encoding, disjoint balanced splits, preservation of counts by shuffling, and identical frequency-baseline predictions before and after shuffling. Dinucleotide order is AA, AC, AG, AT, CA, CC, CG, CT, GA, GC, GG, GT, TA, TC, TG, TT. Frequencies are divided by 250 and pair frequencies by 249.

AI assistance: ChatGPT proposed the neighboring-base comparison, implemented the notebook and script, ran the checks and experiments, and drafted the report. The student selected the hypothesis and accepted the neighboring-base investigation. The accepted suggestion was checked using the ACGTA hand calculation and the controlled frequency-versus-pair comparison. The final interpretation should be reviewed by the student. The consolidated disclosure belongs at the end of the LaTeX report.

The saved run took 271.5 seconds on an Intel Core i7-8650U with 8 logical CPUs, using two PyTorch threads and no GPU. Mean original-test accuracies were 78.87% (frequencies), 97.07% (frequencies plus dinucleotides), 82.49% (MLP), and 99.24% (CNN). These results and their per-run variation are reported in the LaTeX document. An independent check of the saved predictions reproduced all 24 reported accuracy scores.
