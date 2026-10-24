import unittest

from src.cvrptw.solvers.ga_solver import GaSolver
from test_sa_solver import create_small_instance


class TestGaSolver(unittest.TestCase):
    def test_feasible_result(self):
        instance = create_small_instance()
        result = GaSolver(population_size=8).solve(instance, time_limit=0.2, random_seed=42)
        self.assertTrue(result.feasible)
        self.assertLessEqual(result.vehicles_used, instance.vehicle_count)
        self.assertEqual(sorted(n for r in result.routes for n in r[1:-1]), [1, 2, 3, 4])

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            GaSolver(population_size=2)

    def test_infeasible_input(self):
        instance = create_small_instance()
        instance.demands[1] = 99
        with self.assertRaises(ValueError):
            GaSolver(population_size=8).solve(instance, time_limit=0.2)
