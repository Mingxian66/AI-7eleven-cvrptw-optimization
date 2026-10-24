# P2 fairness audit (development)

- Common instances, input model, capacity and hard time-window feasibility rules.
- Shared scalar objective for SA and GA; final comparison uses `(vehicles, distance)` from independently validated original floating-point results.
- OR-Tools uses integer-scaled internal objective and a separate GLS search. Its `random_seed` argument is currently recorded but not used to vary the OR-Tools search configuration.
- The GA still reuses SA initialization, route evaluator, and mutation neighborhoods. This coupling is documented and remains a refactoring task; it does not mean GA and SA are independent implementations.
- `--ortools-repeats N` repeats OR-Tools with the same fixed search configuration, not different random seeds.
- Failed runs remain in the detailed CSV and contribute to feasibility rate, but are excluded from distance means.
- Do not mix 10-second development results with future 60-second formal results. Use a new `--output-dir`.
- Benchmark BKS reference values must be separately verified before reporting gaps.
