import tempfile
import unittest
from pathlib import Path

from src.cvrptw.io.solomon import load_solomon_instance


SAMPLE = """TEST

VEHICLE
NUMBER     CAPACITY
  2          10

CUSTOMER
CUST NO.  XCOORD.  YCOORD.  DEMAND  READY TIME  DUE DATE  SERVICE TIME

    0      0      0       0       0       100       0
    1      3      4       2       0        50       1
    2      6      8       2       0        50       1
"""


class TestSolomonLoader(unittest.TestCase):
    def test_loader(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_text(SAMPLE, encoding="utf-8")

            instance = load_solomon_instance(path)

            self.assertEqual(instance.vehicle_count, 2)
            self.assertEqual(instance.vehicle_capacity, 10)
            self.assertEqual(instance.customer_count, 2)
            self.assertAlmostEqual(instance.distance_matrix[0][1], 5.0)
            self.assertEqual(instance.time_matrix, instance.distance_matrix)


if __name__ == "__main__":
    unittest.main()
