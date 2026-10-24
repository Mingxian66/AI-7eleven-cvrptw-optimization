"""Run OR-Tools on a Solomon instance."""
import argparse
import json
from ..io.solomon import load_solomon_instance
from ..evaluation.metrics import result_to_dict
from ..solvers.ortools_solver import OrtoolsSolver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance', required=True)
    parser.add_argument('--time-limit', type=float, default=60)
    parser.add_argument('--objective-mode', choices=['distance', 'lexicographic'], default='lexicographic')
    args = parser.parse_args()
    instance = load_solomon_instance(args.instance)
    result = OrtoolsSolver(objective_mode=args.objective_mode).solve(instance, time_limit=args.time_limit)
    print(json.dumps(result_to_dict(instance, result), indent=2))


if __name__ == '__main__':
    main()
