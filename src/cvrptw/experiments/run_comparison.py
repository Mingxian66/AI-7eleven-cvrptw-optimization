"""Run a consistent Solomon SA/GA/OR-Tools comparison and export CSV files."""
import argparse
import csv
import json
import hashlib
from datetime import datetime, timezone
import statistics
from pathlib import Path

from ..evaluation.independent_validator import validate_result
from ..io.solomon import load_solomon_instance
from ..solvers.sa_solver import SaSolver
from ..solvers.ga_solver import GaSolver
from ..solvers.ortools_solver import OrtoolsSolver

FIELDS = ['instance', 'algorithm', 'seed', 'time_limit_seconds', 'runtime_seconds',
          'vehicles', 'distance', 'duration', 'feasible', 'validation_errors', 'repeat', 'route_file']


def run_experiments(instances, seeds, time_limit, output_dir, population_size, ortools_repeats=1):
    if time_limit <= 0 or not seeds or ortools_repeats < 1:
        raise ValueError('time limit must be positive and seeds cannot be empty')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    route_dir = output_dir / 'routes'
    route_dir.mkdir(parents=True, exist_ok=True)
    for path in instances:
        instance = load_solomon_instance(str(path))
        for algorithm in ('sa', 'ga', 'ortools'):
            # OR-Tools GLS is run once per instance: its seed is not varied in this setup.
            trial_seeds = seeds if algorithm != 'ortools' else [seeds[0]] * ortools_repeats
            for repeat, seed in enumerate(trial_seeds, start=1):
                if algorithm == 'sa':
                    solver = SaSolver(objective_mode='lexicographic')
                elif algorithm == 'ga':
                    solver = GaSolver(population_size=population_size, objective_mode='lexicographic')
                else:
                    solver = OrtoolsSolver(objective_mode='lexicographic')
                route_file = route_dir / f'{instance.name}_{algorithm}_repeat{repeat:02d}.json'
                try:
                    result = solver.solve(instance, time_limit=time_limit, random_seed=seed)
                    validation = validate_result(instance, result)
                    payload = {
                        'schema_version': 1, 'instance': instance.name,
                        'instance_file': str(path),
                        'instance_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                        'algorithm': algorithm, 'repeat': repeat,
                        'seed': seed if algorithm != 'ortools' else 'not_varied',
                        'time_limit_seconds': time_limit,
                        'routes': result.routes,
                        'reported': {'vehicles': result.vehicles_used,
                                     'distance': result.total_distance,
                                     'duration': result.total_duration,
                                     'runtime_seconds': result.runtime_seconds},
                        'independent_validation': validation,
                        'objective_mode': result.objective_mode,
                    }
                    route_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
                    row = dict(instance=instance.name, algorithm=algorithm,
                               seed=seed if algorithm != 'ortools' else 'not_varied',
                               time_limit_seconds=time_limit,
                               runtime_seconds=round(result.runtime_seconds, 4),
                               vehicles=result.vehicles_used,
                               distance=round(result.total_distance, 6),
                               duration=round(result.total_duration, 6),
                               feasible=validation['feasible'],
                               validation_errors='; '.join(validation['errors']), repeat=repeat,
                               route_file=str(route_file.as_posix()))
                except Exception as exc:
                    row = dict(instance=instance.name, algorithm=algorithm,
                               seed=seed if algorithm != 'ortools' else 'not_varied',
                               time_limit_seconds=time_limit, runtime_seconds='',
                               vehicles='', distance='', duration='', feasible=False,
                               validation_errors=f'{type(exc).__name__}: {exc}', repeat=repeat,
                               route_file='')
                rows.append(row)
                print(f"{instance.name} | {algorithm} | seed={row['seed']} | "
                      f"vehicles={row['vehicles']} | distance={row['distance']} | "
                      f"feasible={row['feasible']}", flush=True)
    with (output_dir / 'comparison_detailed.csv').open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = []
    for instance_name in sorted({row['instance'] for row in rows}):
        for algorithm in ('sa', 'ga', 'ortools'):
            group = [r for r in rows if r['instance'] == instance_name and r['algorithm'] == algorithm]
            valid = [r for r in group if r['feasible']]
            distances = [r['distance'] for r in valid]
            summary.append(dict(instance=instance_name, algorithm=algorithm,
                                runs=len(group), feasible_runs=len(valid),
                                best_vehicles=min((r['vehicles'] for r in valid), default=''),
                                best_distance_at_best_vehicles=(min((r['distance'] for r in valid
                                    if r['vehicles'] == min(v['vehicles'] for v in valid)), default='') if valid else ''),
                                mean_vehicles=round(statistics.mean(r['vehicles'] for r in valid), 4) if valid else '',
                                sd_vehicles=round(statistics.stdev(r['vehicles'] for r in valid), 4) if len(valid)>1 else '',
                                feasibility_rate=round(len(valid)/len(group), 4) if group else '',
                                mean_distance=round(statistics.mean(distances), 6) if distances else '',
                                sd_distance=round(statistics.stdev(distances), 6) if len(distances) > 1 else '',
                                mean_runtime=round(statistics.mean(r['runtime_seconds'] for r in valid), 4) if valid else ''))
    with (output_dir / 'comparison_summary.csv').open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    manifest = {'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'instances': [str(p) for p in instances], 'seeds': list(seeds),
                'time_limit_seconds': time_limit, 'population_size': population_size,
                'ortools_repeats': ortools_repeats,
                'objective': 'lexicographic: vehicles then distance',
                'note': 'OR-Tools repeats use a fixed search configuration; seed is not varied.'}
    (output_dir / 'experiment_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return rows


def main():
    parser = argparse.ArgumentParser(description='Compare SA, GA and OR-Tools on Solomon instances')
    parser.add_argument('--instances', nargs='+', default=['data/solomon/C101.txt',
                        'data/solomon/R101.txt', 'data/solomon/RC101.txt'])
    parser.add_argument('--seeds', nargs='+', type=int, default=[11, 22, 33])
    parser.add_argument('--time-limit', type=float, default=60.0)
    parser.add_argument('--ortools-repeats', type=int, default=1)
    parser.add_argument('--population-size', type=int, default=24)
    parser.add_argument('--output-dir', default='results/p2_comparison')
    args = parser.parse_args()
    run_experiments(args.instances, args.seeds, args.time_limit, args.output_dir, args.population_size, args.ortools_repeats)
    print(f'CSV files saved to: {args.output_dir}')


if __name__ == '__main__':
    main()
