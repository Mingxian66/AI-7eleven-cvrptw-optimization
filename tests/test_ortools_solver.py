import unittest
from test_sa_solver import create_small_instance
from src.cvrptw.solvers.ortools_solver import OrtoolsSolver
from src.cvrptw.evaluation.independent_validator import validate_result


class TestOrtoolsSolver(unittest.TestCase):
    def test_small_instance(self):
        try:
            import ortools
        except ImportError:
            self.skipTest('ortools is not installed')
        instance = create_small_instance()
        result = OrtoolsSolver().solve(instance, time_limit=1)
        self.assertTrue(validate_result(instance, result)['feasible'])

    def test_invalid_objective(self):
        with self.assertRaises(ValueError):
            OrtoolsSolver(objective_mode='invalid')
