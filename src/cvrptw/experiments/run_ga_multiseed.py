"""Repeated GA runs with independently checked results and CSV output."""
import argparse
import csv
import json
import statistics
from pathlib import Path

from ..evaluation.independent_validator import validate_result
from ..io.solomon import load_solomon_instance
from ..solvers.ga_solver import GaSolver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--instances', nargs='+', default=['data/solomon/C101.txt', 'data/solomon/R101.txt', 'data/solomon/RC101.txt'])
    parser.add_argument('--seeds', nargs='+', type=int, default=[11, 22, 33, 44, 55])
    parser.add_argument('--time-limit', type=float, default=5.0)
    parser.add_argument('--population-size', type=int, default=24)
    parser.add_argument('--output', default='results/ga_multiseed/ga_runs.csv')
    args = parser.parse_args()
    rows = []
    for path in args.instances:
        instance = load_solomon_instance(path)
        for seed in args.seeds:
            result = GaSolver(population_size=args.population_size).solve(instance, time_limit=args.time_limit, random_seed=seed)
            report = validate_result(instance, result)
            row = {'instance': instance.name, 'seed': seed, 'vehicles': result.vehicles_used,
                   'distance': round(result.total_distance, 6), 'runtime_seconds': round(result.runtime_seconds, 4),
                   'generations': result.iterations, 'independently_feasible': report['feasible'],
                   'errors': '; '.join(report['errors'])}
            rows.append(row)
            print(json.dumps(row))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print('\nSummary:')
    for name in sorted(set(row['instance'] for row in rows)):
        subset = [row for row in rows if row['instance'] == name]
        print(name, 'feasible', sum(row['independently_feasible'] for row in subset), '/', len(subset),
              'vehicles range', (min(row['vehicles'] for row in subset), max(row['vehicles'] for row in subset)),
              'distance mean', round(statistics.mean(row['distance'] for row in subset), 2),
              'distance std', round(statistics.stdev(row['distance'] for row in subset), 2) if len(subset) > 1 else 0)
    print('Saved:', output)


if __name__ == '__main__':
    main()
