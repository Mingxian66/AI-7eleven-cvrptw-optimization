# P2 Solomon expansion and route reproducibility

## Changes
- `run_comparison.py` saves a separate JSON route record for every successful solve in `output_dir/routes/`.
- Each JSON includes original routes (customer indices, depot 0), original instance path and SHA-256, solver name, repeat index, time budget, reported metrics, and independent validation results.
- `comparison_detailed.csv` adds `route_file` column; failed runs keep an empty route path.
- `experiment_manifest.json` captures parameters. It does not capture Python package versions or machine specifications; record those separately for a thesis.
- `verify_saved_routes.py` independently rechecks routes and CSV metrics against the source instance file.

## Run the three new Solomon instances (PyCharm module)
Module: `src.cvrptw.experiments.run_comparison`
Working directory: project root
Arguments:

```
--instances data/solomon/C102.txt data/solomon/R102.txt data/solomon/RC102.txt --seeds 11 22 33 44 55 --time-limit 60 --ortools-repeats 5 --output-dir results/p2_solomon_expansion_60s
```

45 runs, about 45 minutes plus overhead. Do not modify solver configuration mid-run.

## Verify routes after completion
Module: `src.cvrptw.experiments.verify_saved_routes`
Arguments:

```
--output-dir results/p2_solomon_expansion_60s
```

If the command exits nonzero, inspect the listed mismatches. Route files are saved for any returned result, even if validation marks it infeasible; the verifier currently checks only CSV records marked feasible.

## Optional combined run (six instances)
```
--instances data/solomon/C101.txt data/solomon/C102.txt data/solomon/R101.txt data/solomon/R102.txt data/solomon/RC101.txt data/solomon/RC102.txt --seeds 11 22 33 44 55 --time-limit 60 --ortools-repeats 5 --output-dir results/p2_solomon_six_instances_60s
```

90 runs, roughly 90 minutes plus overhead. Prefer new-only expansion first to preserve existing formal results.

## Caveats
- Existing 60-second experiment CSVs cannot be retroactively supplied with routes. They must be rerun to obtain route-level artifacts.
- OR-Tools `seed=not_varied` is a label for repeated fixed configuration, not five independent random seeds.
- BKS comparison must follow lexicographic ordering (vehicles first, then distance) and matching distance convention.
- This release was tested with Python unittest (15 tests, 1 skipped due to missing OR-Tools), not with a full 60-second benchmark.
