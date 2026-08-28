from __future__ import annotations

import math
import random
import time
from copy import deepcopy

from ..models import CvrptwInstance, SolverResult


class SaSolver:
    """Simple and reproducible simulated annealing benchmark for CVRPTW.

    Neighborhood operators:
    - relocate
    - exchange
    - two_opt

    Capacity, time windows, depot return time, and maximum vehicle count are
    treated as hard constraints. Only feasible candidate solutions are accepted
    into the SA search.
    """

    def __init__(
        self,
        initial_temperature: float = 100.0,
        cooling_rate: float = 0.995,
        minimum_temperature: float = 0.01,
        max_iterations: int = 200000,
        neighbor_attempts: int = 60,
        objective_mode: str = "distance",
    ) -> None:
        if initial_temperature <= 0:
            raise ValueError("initial_temperature must be positive")
        if not 0 < cooling_rate < 1:
            raise ValueError("cooling_rate must be between 0 and 1")
        if minimum_temperature <= 0:
            raise ValueError("minimum_temperature must be positive")
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        if neighbor_attempts <= 0:
            raise ValueError("neighbor_attempts must be positive")
        if objective_mode not in {"distance", "lexicographic"}:
            raise ValueError("objective_mode must be 'distance' or 'lexicographic'")

        self.initial_temperature = float(initial_temperature)
        self.cooling_rate = float(cooling_rate)
        self.minimum_temperature = float(minimum_temperature)
        self.max_iterations = int(max_iterations)
        self.neighbor_attempts = int(neighbor_attempts)
        self.objective_mode = objective_mode

        self.instance: CvrptwInstance | None = None
        self.random: random.Random | None = None
        self.vehicle_penalty = 0.0
        self.deadline: float | None = None

    def solve(
        self,
        instance: CvrptwInstance,
        time_limit: float = 60.0,
        random_seed: int = 42,
        initial_solution: list[list[int]] | None = None,
    ) -> SolverResult:
        if time_limit <= 0:
            raise ValueError("time_limit must be positive")

        start_time = time.perf_counter()
        self.deadline = start_time + time_limit

        instance.validate()
        self.instance = instance
        self.random = random.Random(random_seed)
        self.vehicle_penalty = self._calculate_vehicle_penalty()

        if initial_solution is None:
            current_solution = self._create_initial_solution()
        else:
            current_solution = self._normalize_solution(deepcopy(initial_solution))
            if not self.is_feasible_solution(current_solution):
                raise ValueError("initial_solution is not feasible")

        current_value = self._objective_value(current_solution)
        best_solution = deepcopy(current_solution)
        best_value = current_value

        temperature = self.initial_temperature
        iterations = 0
        best_iteration = 0

        operator_statistics = {
            "relocate": {"used": 0, "accepted": 0, "improved": 0},
            "exchange": {"used": 0, "accepted": 0, "improved": 0},
            "two_opt": {"used": 0, "accepted": 0, "improved": 0},
        }

        operators = {
            "relocate": self._relocate_neighbor,
            "exchange": self._exchange_neighbor,
            "two_opt": self._two_opt_neighbor,
        }
        operator_names = list(operators)

        while iterations < self.max_iterations:
            if self._time_expired():
                break

            operator_name = self.random.choice(operator_names)
            operator_statistics[operator_name]["used"] += 1

            candidate_solution = operators[operator_name](current_solution)
            iterations += 1

            if candidate_solution is None:
                temperature = max(
                    self.minimum_temperature,
                    temperature * self.cooling_rate,
                )
                continue

            candidate_value = self._objective_value(candidate_solution)
            delta = candidate_value - current_value

            if self._accept(delta, temperature):
                current_solution = candidate_solution
                current_value = candidate_value
                operator_statistics[operator_name]["accepted"] += 1

                if candidate_value + 1e-9 < best_value:
                    best_solution = deepcopy(candidate_solution)
                    best_value = candidate_value
                    best_iteration = iterations
                    operator_statistics[operator_name]["improved"] += 1

            temperature = max(
                self.minimum_temperature,
                temperature * self.cooling_rate,
            )

        runtime_seconds = time.perf_counter() - start_time
        best_solution = self._normalize_solution(best_solution)

        return SolverResult(
            solver_name="sa",
            instance_name=instance.name,
            routes=best_solution,
            total_distance=self.total_distance(best_solution),
            total_duration=self.total_duration(best_solution),
            vehicles_used=len(best_solution),
            feasible=self.is_feasible_solution(best_solution),
            runtime_seconds=runtime_seconds,
            iterations=iterations,
            best_iteration=best_iteration,
            random_seed=random_seed,
            objective_mode=self.objective_mode,
            objective_value=best_value,
            operator_statistics=operator_statistics,
            extra={
                "initial_temperature": self.initial_temperature,
                "cooling_rate": self.cooling_rate,
                "minimum_temperature": self.minimum_temperature,
                "neighbor_attempts": self.neighbor_attempts,
            },
        )

    def _create_initial_solution(self) -> list[list[int]]:
        instance = self._require_instance()

        # Earlier due dates are inserted first because they are harder to place.
        customers = list(range(1, instance.customer_count + 1))
        customers.sort(
            key=lambda customer: (
                instance.time_windows[customer][1],
                instance.time_windows[customer][0],
                -instance.demands[customer],
            )
        )

        routes: list[list[int]] = []

        for customer in customers:
            best_routes = None
            best_delta = math.inf

            # Try insertion into every existing route.
            for route_index, route in enumerate(routes):
                old_distance = self.route_distance(route)
                for position in range(1, len(route)):
                    new_route = route[:position] + [customer] + route[position:]
                    if not self.is_feasible_route(new_route):
                        continue

                    delta = self.route_distance(new_route) - old_distance
                    if delta < best_delta:
                        candidate_routes = deepcopy(routes)
                        candidate_routes[route_index] = new_route
                        best_routes = candidate_routes
                        best_delta = delta

            # If necessary, open a new vehicle route.
            if len(routes) < instance.vehicle_count:
                new_route = [0, customer, 0]
                if self.is_feasible_route(new_route):
                    delta = self.route_distance(new_route)
                    if delta < best_delta:
                        best_routes = deepcopy(routes) + [new_route]
                        best_delta = delta

            if best_routes is None:
                raise ValueError(
                    f"cannot construct a feasible initial solution for customer {customer}; "
                    "check vehicle count, capacity, time windows, and travel times"
                )

            routes = best_routes

        return self._normalize_solution(routes)

    def _relocate_neighbor(
        self,
        solution: list[list[int]],
    ) -> list[list[int]] | None:
        if not solution:
            return None

        for _ in range(self.neighbor_attempts):
            if self._time_expired():
                return None
            candidate = deepcopy(solution)
            source_index = self.random.randrange(len(candidate))
            source_route = candidate[source_index]

            if len(source_route) <= 2:
                continue

            source_position = self.random.randrange(1, len(source_route) - 1)
            customer = source_route.pop(source_position)

            target_index = self.random.randrange(len(candidate))
            target_route = candidate[target_index]
            target_position = self.random.randrange(1, len(target_route))
            target_route.insert(target_position, customer)

            candidate = self._normalize_solution(candidate)

            if candidate == solution:
                continue

            if self.is_feasible_solution(candidate):
                return candidate

        return None

    def _exchange_neighbor(
        self,
        solution: list[list[int]],
    ) -> list[list[int]] | None:
        customer_locations = [
            (route_index, position)
            for route_index, route in enumerate(solution)
            for position in range(1, len(route) - 1)
        ]

        if len(customer_locations) < 2:
            return None

        for _ in range(self.neighbor_attempts):
            if self._time_expired():
                return None
            first, second = self.random.sample(customer_locations, 2)
            first_route, first_position = first
            second_route, second_position = second

            candidate = deepcopy(solution)
            candidate[first_route][first_position], candidate[second_route][second_position] = (
                candidate[second_route][second_position],
                candidate[first_route][first_position],
            )

            if candidate == solution:
                continue

            if self.is_feasible_solution(candidate):
                return candidate

        return None

    def _two_opt_neighbor(
        self,
        solution: list[list[int]],
    ) -> list[list[int]] | None:
        eligible_routes = [
            index
            for index, route in enumerate(solution)
            if len(route) >= 4
        ]

        if not eligible_routes:
            return None

        for _ in range(self.neighbor_attempts):
            if self._time_expired():
                return None
            route_index = self.random.choice(eligible_routes)
            route = solution[route_index]

            first_position, second_position = sorted(
                self.random.sample(range(1, len(route) - 1), 2)
            )

            candidate = deepcopy(solution)
            candidate[route_index] = (
                route[:first_position]
                + list(reversed(route[first_position:second_position + 1]))
                + route[second_position + 1:]
            )

            if candidate == solution:
                continue

            if self.is_feasible_solution(candidate):
                return candidate

        return None


    def _time_expired(self) -> bool:
        return self.deadline is not None and time.perf_counter() >= self.deadline

    def _accept(self, delta: float, temperature: float) -> bool:
        if delta <= 0:
            return True

        probability = math.exp(-delta / max(temperature, 1e-12))
        return self.random.random() < probability

    def _calculate_vehicle_penalty(self) -> float:
        instance = self._require_instance()
        max_edge = max(max(row) for row in instance.distance_matrix)
        return max_edge * (instance.customer_count + instance.vehicle_count + 1) + 1.0

    def _objective_value(self, solution: list[list[int]]) -> float:
        distance = self.total_distance(solution)

        if self.objective_mode == "distance":
            return distance

        return len(solution) * self.vehicle_penalty + distance

    def is_feasible_solution(self, solution: list[list[int]]) -> bool:
        instance = self._require_instance()
        normalized = self._normalize_solution(solution)

        if len(normalized) > instance.vehicle_count:
            return False

        customers = [
            customer
            for route in normalized
            for customer in route[1:-1]
        ]

        expected_customers = list(range(1, instance.customer_count + 1))
        if sorted(customers) != expected_customers:
            return False

        return all(self.is_feasible_route(route) for route in normalized)

    def is_feasible_route(self, route: list[int]) -> bool:
        instance = self._require_instance()

        if len(route) < 2 or route[0] != 0 or route[-1] != 0:
            return False

        load = sum(instance.demands[customer] for customer in route[1:-1])
        if load > instance.vehicle_capacity + 1e-9:
            return False

        current_time = max(0.0, instance.time_windows[0][0])

        for index in range(1, len(route)):
            previous_node = route[index - 1]
            current_node = route[index]

            arrival_time = current_time + instance.time_matrix[previous_node][current_node]
            window_start, window_end = instance.time_windows[current_node]

            if arrival_time > window_end + 1e-9:
                return False

            service_start = max(arrival_time, window_start)
            current_time = service_start + instance.service_times[current_node]

        return True

    def route_distance(self, route: list[int]) -> float:
        instance = self._require_instance()
        return sum(
            instance.distance_matrix[route[index - 1]][route[index]]
            for index in range(1, len(route))
        )

    def route_duration(self, route: list[int]) -> float:
        instance = self._require_instance()
        current_time = max(0.0, instance.time_windows[0][0])
        start_time = current_time

        for index in range(1, len(route)):
            previous_node = route[index - 1]
            current_node = route[index]

            arrival_time = current_time + instance.time_matrix[previous_node][current_node]
            window_start, _ = instance.time_windows[current_node]
            service_start = max(arrival_time, window_start)
            current_time = service_start + instance.service_times[current_node]

        return current_time - start_time

    def total_distance(self, solution: list[list[int]]) -> float:
        return sum(self.route_distance(route) for route in solution)

    def total_duration(self, solution: list[list[int]]) -> float:
        return sum(self.route_duration(route) for route in solution)

    @staticmethod
    def _normalize_solution(solution: list[list[int]]) -> list[list[int]]:
        normalized = []
        for route in solution:
            if not route:
                continue

            clean_route = list(route)
            if clean_route[0] != 0:
                clean_route.insert(0, 0)
            if clean_route[-1] != 0:
                clean_route.append(0)

            if len(clean_route) > 2:
                normalized.append(clean_route)

        return normalized

    def _require_instance(self) -> CvrptwInstance:
        if self.instance is None:
            raise RuntimeError("solver instance is not initialized")
        return self.instance
