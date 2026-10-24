# P2 Solomon comparison — PyCharm guide

Run configuration in PyCharm:

- Type: Python / Module name
- Module: `src.cvrptw.experiments.run_comparison`
- Parameters: `--instances data/solomon/C101.txt data/solomon/R101.txt data/solomon/RC101.txt --seeds 11 22 33 --time-limit 10`
- Working directory: project root (contains `src`, `data`, and `requirements.txt`)
- Interpreter: existing Python installation with `numpy`, `pandas`, and `ortools`

Start with a quick functional run using 10 seconds per run. This runs SA and GA three times per instance and OR-Tools once per instance (21 runs, approximately 210 seconds plus overhead). For formal experiments increase the time limit to 60 seconds or a predefined budget, document the machine, and repeat as required.

Output:
- `results/p2_comparison/comparison_detailed.csv`: one row per run, with independent feasibility validation and error messages.
- `results/p2_comparison/comparison_summary.csv`: run counts, feasible counts, best vehicle count, best distance among runs using that vehicle count, and mean/SD distance. Means are descriptive; compare vehicle count before distance for Solomon.

The OR-Tools implementation is not seeded across runs in this experiment; it is run once per instance. A failed run is recorded with an error, not silently discarded. The summary does not contain BKS gaps: add verified BKS references and calculate gaps separately before using these as final thesis tables.
