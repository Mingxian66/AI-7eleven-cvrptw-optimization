"""Independently recheck stored routes against the exact original instance file."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from ..io.solomon import load_solomon_instance
from ..evaluation.independent_validator import validate_routes


def verify_directory(output_dir):
    output_dir = Path(output_dir)
    detail = output_dir / 'comparison_detailed.csv'
    with detail.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    checked = 0
    errors = []
    for row in rows:
        if str(row['feasible']).lower() != 'true':
            continue
        file_path = Path(row['route_file'])
        if not file_path.is_file():
            errors.append(f"{row['instance']} {row['algorithm']} repeat {row['repeat']}: missing route file")
            continue
        data = json.loads(file_path.read_text(encoding='utf-8'))
        instance_path = Path(data['instance_file'])
        if hashlib.sha256(instance_path.read_bytes()).hexdigest() != data['instance_sha256']:
            errors.append(f'{file_path}: source instance file changed')
            continue
        instance = load_solomon_instance(str(instance_path))
        report = validate_routes(instance, data['routes'])
        if not report['feasible']:
            errors.append(f"{file_path}: {report['errors']}")
        if report['vehicles'] != int(row['vehicles']):
            errors.append(f'{file_path}: vehicle count differs from CSV')
        if abs(report['distance'] - float(row['distance'])) > 1e-5:
            errors.append(f'{file_path}: distance differs from CSV')
        if abs(report['duration'] - float(row['duration'])) > 1e-5:
            errors.append(f'{file_path}: duration differs from CSV')
        checked += 1
    print(f'Verified {checked} saved feasible routes; errors: {len(errors)}')
    for err in errors:
        print('ERROR:', err)
    return not errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    if not verify_directory(args.output_dir):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
