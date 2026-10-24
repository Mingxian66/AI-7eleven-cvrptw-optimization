"""OR-Tools RoutingModel with hard capacity/time windows and GLS.

Integer scaling is used because OR-Tools routing transit callbacks require ints.
Outputs are independently checked against original floating-point inputs.
"""
import time

from ..models import SolverResult
from ..evaluation.independent_validator import validate_routes


class OrtoolsSolver:
    def __init__(self, objective_mode='lexicographic', scale=100000):
        if objective_mode not in ('distance', 'lexicographic'):
            raise ValueError('invalid objective mode')
        if scale < 1:
            raise ValueError('scale must be positive')
        self.objective_mode = objective_mode
        self.scale = scale

    def solve(self, instance, time_limit=60.0, random_seed=42):
        try:
            from ortools.constraint_solver import pywrapcp, routing_enums_pb2
        except ImportError as error:
            raise ImportError('OR-Tools is required: python -m pip install ortools') from error
        if time_limit <= 0:
            raise ValueError('time_limit must be positive')
        instance.validate()
        start = time.perf_counter()
        n = len(instance.demands)
        manager = pywrapcp.RoutingIndexManager(n, instance.vehicle_count, 0)
        routing = pywrapcp.RoutingModel(manager)
        scale = self.scale
        def scaled(value):
            # Round upwards for time and demand to avoid accepting violations.
            import math
            return int(math.ceil(value * scale - 1e-10))
        dist = [[scaled(x) for x in row] for row in instance.distance_matrix]
        travel = [[scaled(x) for x in row] for row in instance.time_matrix]
        services = [scaled(x) for x in instance.service_times]
        demands = [scaled(x) for x in instance.demands]
        windows = [(scaled(a), int(b * scale + 1e-9)) for a, b in instance.time_windows]
        def distance_callback(i, j):
            return dist[manager.IndexToNode(i)][manager.IndexToNode(j)]
        distance_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(distance_index)
        def demand_callback(i):
            return demands[manager.IndexToNode(i)]
        demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(demand_index, 0,
            [int(instance.vehicle_capacity * scale + 1e-9)] * instance.vehicle_count, True, 'Capacity')
        def time_callback(i, j):
            a = manager.IndexToNode(i)
            b = manager.IndexToNode(j)
            return travel[a][b] + services[a]
        time_index = routing.RegisterTransitCallback(time_callback)
        horizon = max(end for _, end in windows)
        routing.AddDimension(time_index, horizon, horizon, False, 'Time')
        time_dimension = routing.GetDimensionOrDie('Time')
        for node in range(1, n):
            index = manager.NodeToIndex(node)
            time_dimension.CumulVar(index).SetRange(*windows[node])
        for vehicle in range(instance.vehicle_count):
            time_dimension.CumulVar(routing.Start(vehicle)).SetRange(*windows[0])
            time_dimension.CumulVar(routing.End(vehicle)).SetRange(*windows[0])
        if self.objective_mode == 'lexicographic':
            # Fixed per-used-vehicle cost dominates any possible total distance difference.
            max_arc = max(max(row) for row in dist)
            routing.SetFixedCostOfAllVehicles(max_arc * (n + instance.vehicle_count + 1) + 1)
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.FromMilliseconds(max(1, int(time_limit * 1000)))
        solution = routing.SolveWithParameters(params)
        if solution is None:
            raise ValueError('OR-Tools found no feasible solution within the time limit; check first-solution search and integer scaling')
        routes = []
        for vehicle in range(instance.vehicle_count):
            index = routing.Start(vehicle)
            route = [0]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
            if len(route) > 2:
                routes.append(route)
        report = validate_routes(instance, routes)
        if not report['feasible']:
            raise ValueError('OR-Tools route fails independent original-data verification: ' + '; '.join(report['errors'][:5]))
        return SolverResult(solver_name='ortools', instance_name=instance.name,
            routes=routes, total_distance=report['distance'], total_duration=report['duration'],
            vehicles_used=len(routes), feasible=True, runtime_seconds=time.perf_counter() - start,
            iterations=0, best_iteration=0, random_seed=random_seed,
            objective_mode=self.objective_mode, objective_value=float(solution.ObjectiveValue()),
            operator_statistics={}, extra={'metaheuristic': 'GUIDED_LOCAL_SEARCH', 'scale': scale,
            'note': 'OR-Tools integer-scaled objective; independently validated original distances'})
