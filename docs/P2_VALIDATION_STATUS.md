# P2 validation status (development checkpoint)

## GA independent feasibility verification

`src/cvrptw/evaluation/independent_validator.py` independently checks depot endpoints, unique coverage, capacity, hard time windows (including return to depot), fleet size, and recomputed distance/duration. It does not call SA/GA feasibility methods.

Run: `python -m unittest discover -s tests`

## GA multi-seed smoke test (NOT final benchmark)

Run: `python -m src.cvrptw.experiments.run_ga_multiseed --seeds 11 22 33 --time-limit 1`

Results stored in `results/ga_multiseed/ga_runs.csv`. All nine instance/seed combinations passed independent feasibility validation. C101 yielded 10 vehicles and 828.936867 distance for each seed; R101 yielded 20 vehicles; RC101 yielded 17 vehicles. These are one-second development smoke tests, not tuned or repeated formal benchmarks. Similar C101 results across seeds can reflect the same deterministic initial solution; seed diversity alone does not demonstrate search robustness.

## OR-Tools development

`src/cvrptw/solvers/ortools_solver.py` and `src/cvrptw/experiments/run_ortools.py` have been implemented with RoutingModel, capacity/time dimensions, Guided Local Search, integer scaling and independent output verification. `requirements.txt` now includes `ortools>=9.10`.

**Environment limitation:** OR-Tools could not be installed in the current execution environment because package network access failed. The OR-Tools integration test was skipped, so the OR-Tools implementation has **not yet been execution-validated**. On a machine with network access run:

```
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python -m src.cvrptw.experiments.run_ortools --instance data/solomon/C101.txt --time-limit 10
```

If a feasible route cannot be found within the budget, the runner raises a clear error. OR-Tools is a heuristic comparison, not an exact solver. Its internal integer-scaled objective is not directly comparable with the floating-point GA/SA objective; use returned vehicle count and original-data distance.

## Next research tasks

1. Execute and validate OR-Tools on the user's Windows environment.
2. Run SA/GA/OR-Tools under the same specified time budgets and instance inputs.
3. Perform longer repeated runs with more seeds; record mean/std and vehicle-first comparisons.
4. Investigate GA search diversity and tune operators without changing feasibility rules.
