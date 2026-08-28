from ..models import CvrptwInstance, SolverResult


def calculate_capacity_utilization(
    instance: CvrptwInstance,
    routes: list[list[int]],
) -> float:
    if not routes:
        return 0.0

    utilizations = []
    for route in routes:
        load = sum(instance.demands[customer] for customer in route[1:-1])
        utilizations.append(load / instance.vehicle_capacity)

    return sum(utilizations) / len(utilizations)


def result_to_dict(
    instance: CvrptwInstance,
    result: SolverResult,
) -> dict:
    return {
        "solver_name": result.solver_name,
        "instance_name": result.instance_name,
        "total_distance": result.total_distance,
        "total_duration": result.total_duration,
        "vehicles_used": result.vehicles_used,
        "capacity_utilization": calculate_capacity_utilization(instance, result.routes),
        "feasible": result.feasible,
        "runtime_seconds": result.runtime_seconds,
        "iterations": result.iterations,
        "best_iteration": result.best_iteration,
        "random_seed": result.random_seed,
        "objective_mode": result.objective_mode,
        "objective_value": result.objective_value,
        "routes": result.routes,
    }
