# Published benchmark results

- `p2_solomon_formal_60s_verified/`: C101, R101, RC101, five repeats per algorithm, 45 route JSON files.
- `p2_solomon_expansion_60s/`: C102, R102, RC102, five repeats per algorithm, 45 route JSON files.
- `solomon_six_instance_analysis/`: combined English summary and BKS figures.

Use `python -m src.cvrptw.experiments.verify_saved_routes --output-dir <directory>` to independently recheck the route JSON files. Original experimental outputs should not be edited.
