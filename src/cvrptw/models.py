from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CvrptwInstance:
    name: str
    distance_matrix: list[list[float]]
    time_matrix: list[list[float]]
    demands: list[float]
    time_windows: list[tuple[float, float]]
    service_times: list[float]
    vehicle_count: int
    vehicle_capacity: float
    coordinates: list[tuple[float, float]] | None = None

    @property
    def customer_count(self) -> int:
        return len(self.demands) - 1

    def validate(self) -> None:
        node_count = len(self.demands)

        if node_count < 2:
            raise ValueError("instance must contain one depot and at least one customer")

        if self.vehicle_count <= 0:
            raise ValueError("vehicle_count must be positive")

        if self.vehicle_capacity <= 0:
            raise ValueError("vehicle_capacity must be positive")

        expected_lengths = {
            "time_windows": len(self.time_windows),
            "service_times": len(self.service_times),
        }
        for name, length in expected_lengths.items():
            if length != node_count:
                raise ValueError(f"{name} length must equal node count")

        for matrix_name, matrix in (
            ("distance_matrix", self.distance_matrix),
            ("time_matrix", self.time_matrix),
        ):
            if len(matrix) != node_count:
                raise ValueError(f"{matrix_name} row count must equal node count")
            if any(len(row) != node_count for row in matrix):
                raise ValueError(f"{matrix_name} must be square")

        if any(demand < 0 for demand in self.demands):
            raise ValueError("demands cannot be negative")

        if any(start > end for start, end in self.time_windows):
            raise ValueError("time window start cannot exceed end")


@dataclass
class SolverResult:
    solver_name: str
    instance_name: str
    routes: list[list[int]]
    total_distance: float
    total_duration: float
    vehicles_used: int
    feasible: bool
    runtime_seconds: float
    iterations: int
    best_iteration: int
    random_seed: int
    objective_mode: str
    objective_value: float
    operator_statistics: dict[str, dict[str, int]]
    extra: dict[str, Any]
