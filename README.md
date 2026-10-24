# AI-Based 7-Eleven Retail Replenishment Vehicle Route Optimization

Master's research implementation of the **Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)**. The current completed stage compares **Simulated Annealing (SA)**, **Genetic Algorithm (GA)**, and **Google OR-Tools Routing Solver** on six Solomon 100-customer instances. A semi-synthetic Petaling Jaya 7-Eleven case study is **planned, not yet completed**.

## Current research status (24 October 2026)

- Implemented SA (relocate, exchange, intra-route 2-opt), GA, and OR-Tools solvers with a shared input model.
- Completed 60-second experiments on **C101, C102, R101, R102, RC101, RC102**.
- Ran **five repetitions per solver and instance: 6 × 3 × 5 = 90 runs**. SA and GA use seeds 11, 22, 33, 44, 55; OR-Tools uses a fixed search configuration repeated five times (**not five different seeds**).
- Saved **90 route JSON files** and experiment manifests; all 90 routes passed the project's independent feasibility verifier (zero reported errors).
- Used the **lexicographic benchmark objective: minimize number of vehicles first, then total Euclidean distance**.
- These are heuristic/computational results, **not proofs of optimality**. Best-known solutions (BKS) are reference values, not necessarily certified optima.

## Repository contents

```text
config/                                  Algorithm configuration
data/solomon/                            Solomon input instances (including six evaluated cases)
data/pj/                                 Placeholder for planned case study
docs/reports/                            Editable English Results and Discussion draft
docs/                                    Experiment, validation and fairness notes
src/cvrptw/solvers/                      SA, GA, OR-Tools implementations
src/cvrptw/evaluation/                   Shared objective and independent validation
src/cvrptw/experiments/                  Experiment runners and route verification
src/cvrptw/io/                           Solomon parser
tests/                                   Automated tests
results/p2_solomon_formal_60s_verified/  C101, R101, RC101: 45 runs + routes
results/p2_solomon_expansion_60s/        C102, R102, RC102: 45 runs + routes
results/solomon_six_instance_analysis/   Consolidated CSV and BKS comparison charts
```

Earlier exploratory runs, IDE configuration, caches, and local temporary files are intentionally excluded from this GitHub release.

## Installation

Use Python 3.14 (the environment used for the recorded experiments) or a compatible Python version supported by the installed dependencies:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

## Re-run benchmark experiments

Run from the **repository root**. Each command is approximately **45 minutes** of solver budget (45 runs × 60 seconds), plus overhead. Use separate output directories to preserve the published records.

```bash
python -m src.cvrptw.experiments.run_comparison --instances data/solomon/C101.txt data/solomon/R101.txt data/solomon/RC101.txt --seeds 11 22 33 44 55 --time-limit 60 --ortools-repeats 5 --output-dir results/reproduction_C101_R101_RC101

python -m src.cvrptw.experiments.run_comparison --instances data/solomon/C102.txt data/solomon/R102.txt data/solomon/RC102.txt --seeds 11 22 33 44 55 --time-limit 60 --ortools-repeats 5 --output-dir results/reproduction_C102_R102_RC102
```

## Verify saved routes

```bash
python -m src.cvrptw.experiments.verify_saved_routes --output-dir results/p2_solomon_formal_60s_verified
python -m src.cvrptw.experiments.verify_saved_routes --output-dir results/p2_solomon_expansion_60s
```

Both published result sets were independently re-validated by the project verifier, with **45 feasible routes and 0 errors** each. This validates implemented constraints; it does not establish optimality.

## Results and interpretation

See [`results/solomon_six_instance_analysis/`](results/solomon_six_instance_analysis/) for the consolidated results CSV and BKS figures, and [`docs/reports/`](docs/reports/) for the editable English report draft. Comparisons prioritize fleet size; a shorter distance with **more vehicles** is not a better lexicographic result.

### Limitations

- Six selected Solomon instances do not establish general superiority across the full benchmark.
- OR-Tools Routing Solver uses heuristic search, not an exact optimality certificate.
- OR-Tools fixed-configuration repeats should not be interpreted as varied random-seed trials.
- Solver costs and timing may differ with hardware, dependencies and runtime conditions.
- Petaling Jaya road-network matrices, semi-synthetic demand and the operational baseline are future work.

## Data and references

Solomon VRPTW benchmark data: [Solomon (1987)](https://doi.org/10.1287/opre.35.2.254). Best-known solution reference: [SINTEF VRPTW benchmark](https://www.sintef.no/projectweb/top/vrptw/100-customers/). Source datasets remain attributed to their respective authors; check redistribution conditions before public release.

## Repository maintenance

Do not commit passwords, API keys, private customer data, personal paths, IDE caches, or obsolete experiment runs. Keep raw published result folders unchanged; place future runs in new directories.
