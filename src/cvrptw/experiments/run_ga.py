"""Command-line runner for the genetic algorithm."""
import argparse
import json

from ..evaluation.metrics import result_to_dict
from ..io.solomon import load_solomon_instance
from ..solvers.ga_solver import GaSolver


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GA on a Solomon CVRPTW instance")
    parser.add_argument("--instance", required=True)
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--population-size", type=int, default=24)
    parser.add_argument("--objective-mode", choices=["distance", "lexicographic"], default="lexicographic")
    args = parser.parse_args()
    instance = load_solomon_instance(args.instance)
    solver = GaSolver(population_size=args.population_size, objective_mode=args.objective_mode)
    result = solver.solve(instance, time_limit=args.time_limit, random_seed=args.seed)
    print(json.dumps(result_to_dict(instance, result), indent=2))


if __name__ == "__main__":
    main()
