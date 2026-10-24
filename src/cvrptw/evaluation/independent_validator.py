"""Independent route verification; does not call any solver feasibility function."""
from collections import Counter
from math import isclose


def validate_routes(instance, routes):
    instance.validate()
    errors = []
    seen = []
    distance = 0.0
    duration = 0.0
    if len(routes) > instance.vehicle_count:
        errors.append('fleet limit exceeded')
    for index, route in enumerate(routes):
        if len(route) < 3 or route[0] != 0 or route[-1] != 0:
            errors.append(f'route {index}: invalid depot endpoints or empty route')
            continue
        if any(not isinstance(node, int) or node < 0 or node > instance.customer_count for node in route):
            errors.append(f'route {index}: invalid node id')
            continue
        if 0 in route[1:-1]:
            errors.append(f'route {index}: depot appears inside route')
        seen.extend(route[1:-1])
        load = sum(instance.demands[node] for node in route[1:-1])
        if load > instance.vehicle_capacity + 1e-7:
            errors.append(f'route {index}: capacity exceeded')
        clock = max(0.0, instance.time_windows[0][0])
        departure = clock
        for previous, node in zip(route[:-1], route[1:]):
            distance += instance.distance_matrix[previous][node]
            arrival = clock + instance.time_matrix[previous][node]
            start, end = instance.time_windows[node]
            if arrival > end + 1e-7:
                errors.append(f'route {index}: time window violated at node {node}')
            clock = max(arrival, start) + instance.service_times[node]
        duration += clock - departure
    counts = Counter(seen)
    for node in range(1, instance.customer_count + 1):
        if counts[node] != 1:
            errors.append(f'customer {node}: served {counts[node]} times')
    return {'feasible': not errors, 'errors': errors, 'distance': distance,
            'duration': duration, 'vehicles': len(routes)}


def validate_result(instance, result):
    report = validate_routes(instance, result.routes)
    if not isclose(report['distance'], result.total_distance, rel_tol=1e-8, abs_tol=1e-6):
        report['errors'].append('reported distance mismatch')
    if not isclose(report['duration'], result.total_duration, rel_tol=1e-8, abs_tol=1e-6):
        report['errors'].append('reported duration mismatch')
    if report['vehicles'] != result.vehicles_used:
        report['errors'].append('reported vehicle count mismatch')
    if not result.feasible:
        report['errors'].append('solver reported infeasible')
    report['feasible'] = not report['errors']
    return report
