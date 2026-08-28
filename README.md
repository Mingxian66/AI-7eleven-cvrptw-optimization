# AI-Based 7-Eleven Retail Replenishment Vehicle Route Optimization

This repository contains the implementation for a research project on **Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)** for retail replenishment.

The study compares three practical routing approaches under common problem inputs, feasibility rules, and computational budgets:

- Simulated Annealing (SA)
- Genetic Algorithm (GA)
- Google OR-Tools

A semi-synthetic Petaling Jaya retail case will later be used to compare optimized routes with a transparent cluster-first operational baseline. The repository is being developed incrementally alongside the research project.

## Current implementation status

The current public version contains a working **neighborhood-based SA benchmark** plus the shared CVRPTW data and evaluation framework. GA and OR-Tools are currently scaffolded and will be implemented in later updates.

Completed components include:

- common `CvrptwInstance` and `SolverResult` structures
- Solomon benchmark loader
- Solomon input validation
- distance and travel-time matrix support
- SA with `relocate`, `exchange`, and `two_opt` neighborhoods
- hard capacity and time-window feasibility checking
- fixed random seeds
- wall-clock time limits
- common evaluation metrics
- automated unit tests
- initial SA benchmark outputs for C101, R101, and RC101

For a detailed development checklist, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Research design

The project follows two main experimental stages.

**Stage A — Solomon benchmark**

SA, GA, and OR-Tools will be tested on the same Solomon CVRPTW instances. Vehicle count is considered before travel distance when benchmark results are interpreted. Solution feasibility, distance, runtime, gap to reference results, and stochastic robustness are evaluated.

**Stage B — Petaling Jaya case study**

The same routing methods will be applied to selected 7-Eleven store locations in Petaling Jaya using road-network distance and travel-time matrices. Demand, service time, and delivery windows will be generated transparently because proprietary company replenishment data are not available. A cluster-first rule will provide an operational comparison baseline.

## SA benchmark design

The SA benchmark intentionally uses only three classic neighborhood operators:

1. `relocate` — move a customer to another position or route
2. `exchange` — swap two customers
3. `two_opt` — reverse a subsequence inside one route

The implementation does not use ALNS, Or-opt, or route-fusion operators. This keeps the benchmark clear and reproducible.

The solver supports two objective modes:

- `lexicographic`: vehicle count has priority over total distance; intended for Solomon-style comparison
- `distance`: total distance is minimized under a fixed fleet limit; intended for the Petaling Jaya case

## Repository structure

```text
AI-7eleven-cvrptw-optimization/
├── config/
│   └── default.json
├── data/
│   ├── pj/
│   └── solomon/
├── docs/
│   └── PROJECT_STATUS.md
├── results/
│   ├── README.md
│   └── sa_first_benchmark/
├── src/
│   └── cvrptw/
│       ├── evaluation/
│       │   └── metrics.py
│       ├── experiments/
│       │   └── run_sa.py
│       ├── io/
│       │   └── solomon.py
│       ├── solvers/
│       │   ├── ga_solver.py
│       │   ├── ortools_solver.py
│       │   └── sa_solver.py
│       └── models.py
├── tests/
│   ├── test_sa_solver.py
│   └── test_solomon_loader.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Requirements

The current SA implementation uses Python with NumPy and Pandas.

Install the dependencies with:

```bash
python -m pip install -r requirements.txt
```

> The research report plans Python 3.14 for the final experimental environment. The current repository code should be tested in the actual environment used for each formal experiment, and that version should be recorded with the results.

## Run the SA benchmark

Example using Solomon C101:

```bash
python -m src.cvrptw.experiments.run_sa \
  --instance data/solomon/C101.txt \
  --time-limit 60 \
  --seed 42 \
  --objective-mode lexicographic
```

To use total distance as the main objective instead:

```bash
python -m src.cvrptw.experiments.run_sa \
  --instance data/solomon/C101.txt \
  --time-limit 60 \
  --seed 42 \
  --objective-mode distance
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

At the time of this GitHub-ready release, the included test suite contains four tests covering the Solomon loader, SA feasibility behavior, capacity rejection, and seed-based reproducibility.

## Included benchmark data

The repository currently includes selected Solomon 100-customer instances from the C, R, and RC groups for research development and validation.

The original Solomon benchmark should be cited in academic work as:

> Solomon, M. M. (1987). Algorithms for the vehicle routing and scheduling problems with time window constraints. *Operations Research, 35*(2), 254–265. https://doi.org/10.1287/opre.35.2.254

## Reproducibility notes

For formal experiments, the project is designed to use:

- the same instance data for all methods
- the same hard CVRPTW feasibility rules
- the same wall-clock budget for a given test setting
- recorded random seeds for SA and GA
- saved generated scenario files
- independent feasibility verification before solution-quality comparison
- versioned result files

The initial results under `results/sa_first_benchmark/` are development-stage outputs and are not the final thesis results.

## Academic-use notice

This repository is made public for academic project visibility and reproducibility. No open-source license has been assigned in this version. Public access does not by itself grant permission to reuse the code beyond rights provided by applicable law.

## Repository updates

The repository will be updated as the GA, OR-Tools, Petaling Jaya dataset workflow, operational baseline, and formal experiments are completed.
