import unittest
from test_sa_solver import create_small_instance
from src.cvrptw.evaluation.independent_validator import validate_routes, validate_result
from src.cvrptw.solvers.ga_solver import GaSolver


class TestIndependentValidator(unittest.TestCase):
    def test_ga_independently_feasible(self):
        instance = create_small_instance()
        result = GaSolver(population_size=8).solve(instance, time_limit=0.2, random_seed=42)
        self.assertTrue(validate_result(instance, result)['feasible'])

    def test_repeated_customer_rejected(self):
        instance = create_small_instance()
        report = validate_routes(instance, [[0, 1, 2, 0], [0, 2, 3, 4, 0]])
        self.assertFalse(report['feasible'])

    def test_missing_customer_rejected(self):
        instance = create_small_instance()
        self.assertFalse(validate_routes(instance, [[0, 1, 2, 3, 0]])['feasible'])

    def test_capacity_rejected(self):
        instance = create_small_instance()
        instance.demands[1] = instance.vehicle_capacity + 1
        self.assertFalse(validate_routes(instance, [[0, 1, 0], [0, 2, 3, 4, 0]])['feasible'])

    def test_time_window_rejected(self):
        instance = create_small_instance()
        instance.time_windows[1] = (0, 0)
        self.assertFalse(validate_routes(instance, [[0, 1, 0], [0, 2, 3, 4, 0]])['feasible'])
