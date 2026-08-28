import unittest

from src.cvrptw.models import CvrptwInstance
from src.cvrptw.solvers.sa_solver import SaSolver


def create_small_instance() -> CvrptwInstance:
    distance_matrix = [
        [0, 4, 6, 8, 7],
        [4, 0, 3, 5, 6],
        [6, 3, 0, 4, 2],
        [8, 5, 4, 0, 3],
        [7, 6, 2, 3, 0],
    ]

    time_matrix = [row[:] for row in distance_matrix]

    return CvrptwInstance(
        name="small_test",
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        demands=[0, 2, 2, 2, 2],
        time_windows=[
            (0, 100),
            (0, 40),
            (0, 40),
            (0, 40),
            (0, 40),
        ],
        service_times=[0, 1, 1, 1, 1],
        vehicle_count=2,
        vehicle_capacity=4,
    )


class TestSaSolver(unittest.TestCase):
    def test_solver_returns_feasible_solution(self):
        instance = create_small_instance()
        solver = SaSolver(
            max_iterations=3000,
            neighbor_attempts=30,
            objective_mode="distance",
        )

        result = solver.solve(
            instance=instance,
            time_limit=0.2,
            random_seed=42,
        )

        self.assertTrue(result.feasible)
        self.assertLessEqual(result.vehicles_used, instance.vehicle_count)

        visited = sorted(
            customer
            for route in result.routes
            for customer in route[1:-1]
        )
        self.assertEqual(visited, [1, 2, 3, 4])

    def test_same_seed_is_reproducible_by_iterations(self):
        instance = create_small_instance()

        solver_1 = SaSolver(max_iterations=1000, neighbor_attempts=20)
        result_1 = solver_1.solve(instance, time_limit=10, random_seed=7)

        solver_2 = SaSolver(max_iterations=1000, neighbor_attempts=20)
        result_2 = solver_2.solve(instance, time_limit=10, random_seed=7)

        self.assertEqual(result_1.routes, result_2.routes)
        self.assertAlmostEqual(result_1.total_distance, result_2.total_distance)

    def test_infeasible_vehicle_capacity_is_rejected(self):
        instance = create_small_instance()
        bad_instance = CvrptwInstance(
            name="bad",
            distance_matrix=instance.distance_matrix,
            time_matrix=instance.time_matrix,
            demands=[0, 5, 5, 5, 5],
            time_windows=instance.time_windows,
            service_times=instance.service_times,
            vehicle_count=2,
            vehicle_capacity=4,
        )

        solver = SaSolver()

        with self.assertRaises(ValueError):
            solver.solve(bad_instance, time_limit=0.1, random_seed=1)


if __name__ == "__main__":
    unittest.main()
