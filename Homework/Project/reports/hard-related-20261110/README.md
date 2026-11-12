# Related-proof and intermediary experiment

Job: complete; current stage: finished.

Both English and Lean arguments are compared. Source positives are user-assumed;
related swaps are synthetic negatives. Scores do not certify subtle semantic fidelity.
The old 16-case core is a previously inspected diagnostic, not a new blind test.
Generation failures are abstentions; accuracy is conditional on scored examples.
Generated code is compiler-unchecked unless a separate compilation report exists.

| Model / architecture | Evaluation | Coverage | Accuracy | Mismatch F1 | False acceptance |
| --- | --- | ---: | ---: | ---: | ---: |
| untuned-direct | validation | 60/60 | 85.00% | 0.8696 | 0 |
| untuned-direct | test | 54/54 | 77.78% | 0.8182 | 0 |
| untuned-direct | previous_same_theorem_diagnostic | 16/16 | 93.75% | 0.9333 | 1 |
| tuned-direct | validation | 60/60 | 98.33% | 0.9836 | 0 |
| tuned-direct | test | 54/54 | 98.15% | 0.9818 | 0 |
| tuned-direct | previous_same_theorem_diagnostic | 16/16 | 68.75% | 0.5455 | 5 |
| nl_to_lean | test | 13/54 | 69.23% | 0.7500 | 0 |
| nl_to_lean | previous_same_theorem_diagnostic | 12/16 | 100.00% | 1.0000 | 0 |
| nl_to_lean | test (generated code compiled) | 0/54 | unscored | n/a | n/a |
| nl_to_lean | previous_same_theorem_diagnostic (generated code compiled) | 0/16 | unscored | n/a | n/a |
| lean_to_nl | test | 48/54 | 68.75% | 0.7619 | 0 |
| lean_to_nl | previous_same_theorem_diagnostic | 16/16 | 100.00% | 1.0000 | 0 |
| verbose_lean | test | 35/54 | 57.14% | 0.6939 | 0 |
| verbose_lean | previous_same_theorem_diagnostic | 16/16 | 100.00% | 1.0000 | 0 |
| verbose_lean | test (generated code compiled) | 0/54 | unscored | n/a | n/a |
| verbose_lean | previous_same_theorem_diagnostic (generated code compiled) | 0/16 | unscored | n/a | n/a |
| natural_lean | test | 42/54 | 61.90% | 0.7241 | 0 |
| natural_lean | previous_same_theorem_diagnostic | 16/16 | 100.00% | 1.0000 | 0 |
| natural_lean | test (generated code compiled) | 0/54 | unscored | n/a | n/a |
| natural_lean | previous_same_theorem_diagnostic (generated code compiled) | 0/16 | unscored | n/a | n/a |

See latest.json for both classes, confusion matrices, ranking metrics and status.
Raw prompts, generations, predictions, adapters and logs remain ignored local artifacts.

Generated-code compiler outcomes (not source-faithfulness labels):

- natural_lean: {"compile_failed": 63, "not_checked": 6, "rejected_executable_extension": 1}
- english: {"not_applicable": 35}
- lean: {"not_checked": 22, "compile_failed": 9, "rejected_import": 4}
- verbose_lean: {"compile_failed": 51, "not_checked": 10, "timeout": 1, "rejected_import": 5, "compiled": 2, "rejected_executable_extension": 1}
