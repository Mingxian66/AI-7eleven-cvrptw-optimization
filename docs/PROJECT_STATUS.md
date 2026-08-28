# Project Status

## Current stage

The repository is currently at the **SA benchmark implementation and initial benchmark test** stage.

## Completed

- Common CVRPTW data model and standardized solver-result structure.
- Solomon benchmark text-file loader.
- Data validation checks for Solomon instances.
- Separate distance and travel-time matrices in the common model.
- Neighborhood-based Simulated Annealing implementation.
- SA neighborhood operators: relocate, exchange, and 2-opt.
- Hard capacity and time-window feasibility checks.
- Fixed random seed support and wall-clock time limit support.
- Standard evaluation metrics module.
- Unit tests for the Solomon loader and SA solver.
- Initial SA benchmark outputs for C101, R101, and RC101.

## Scaffolded but not yet implemented

- Genetic Algorithm solver.
- Google OR-Tools solver.
- Petaling Jaya case-study data preparation.
- Cluster-first operational baseline.
- Repeated-run experiment runner for the formal comparison.
- Sensitivity analysis for time-window tightness.

## Planned next steps

1. Implement the Genetic Algorithm using the common solver interface.
2. Implement the Google OR-Tools CVRPTW model using the same input and evaluation rules.
3. Add independent result verification for every solver output.
4. Build the Petaling Jaya semi-synthetic case-study dataset and road-network matrices.
5. Implement the cluster-first operational baseline.
6. Run the formal Solomon and Petaling Jaya experiments.
