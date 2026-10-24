"""Shared objective and lexicographic ranking for CVRPTW."""

def vehicle_penalty(instance):
    max_edge = max(max(row) for row in instance.distance_matrix)
    return max_edge * (instance.customer_count + instance.vehicle_count + 1) + 1.0

def objective_value(vehicles, distance, mode, penalty):
    if mode == 'distance':
        return distance
    if mode == 'lexicographic':
        return vehicles * penalty + distance
    raise ValueError('invalid objective mode')

def ranking_key(vehicles, distance):
    return (vehicles, distance)
