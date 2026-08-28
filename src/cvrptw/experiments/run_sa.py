import argparse
import json

from ..evaluation.metrics import result_to_dict
from ..io.solomon import load_solomon_instance
from ..solvers.sa_solver import SaSolver


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SA benchmark on a Solomon CVRPTW instance")
    parser.add_argument("--instance", required=True, help="path to Solomon instance")
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--objective-mode",
        choices=["distance", "lexicographic"],
        default="lexicographic",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    instance = load_solomon_instance(args.instance)
    solver = SaSolver(objective_mode=args.objective_mode)

    result = solver.solve(
        instance=instance,
        time_limit=args.time_limit,
        random_seed=args.seed,
    )

    print(json.dumps(result_to_dict(instance, result), indent=2))


if __name__ == "__main__":
    main()
