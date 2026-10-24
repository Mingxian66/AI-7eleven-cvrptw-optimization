import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.cvrptw.experiments.run_comparison import run_experiments
from src.cvrptw.experiments.verify_saved_routes import verify_directory
from src.cvrptw.models import SolverResult


class TestRouteExport(unittest.TestCase):
    def test_saved_routes_and_revalidation(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance_file = Path(tmp) / 'Tiny.txt'
            instance_file.write_text('''TINY\nVEHICLE\nNUMBER CAPACITY\n 2 10\nCUSTOMER\nCUST NO. XCOORD. YCOORD. DEMAND READY TIME DUE DATE SERVICE TIME\n0 0 0 0 0 100 0\n1 1 0 1 0 100 0\n''')
            class FakeSolver:
                def __init__(self, **kwargs):
                    pass
                def solve(self, instance, time_limit, random_seed):
                    return SolverResult('fake', instance.name, [[0, 1, 0]], 2.0, 2.0, 1,
                                        True, 0.01, 0, 0, random_seed, 'lexicographic', 2.0, {}, {})
            out = Path(tmp) / 'out'
            with patch('src.cvrptw.experiments.run_comparison.SaSolver', FakeSolver), \
                 patch('src.cvrptw.experiments.run_comparison.GaSolver', FakeSolver), \
                 patch('src.cvrptw.experiments.run_comparison.OrtoolsSolver', FakeSolver):
                rows = run_experiments([instance_file], [11], 1, out, 5, 1)
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(Path(row['route_file']).is_file() for row in rows))
            self.assertTrue(verify_directory(out))
            payload = json.loads(Path(rows[0]['route_file']).read_text())
            self.assertEqual(payload['routes'], [[0, 1, 0]])
            self.assertTrue((out / 'experiment_manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
