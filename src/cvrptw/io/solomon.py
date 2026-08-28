from pathlib import Path
import math

from ..models import CvrptwInstance


def _euclidean_matrix(coordinates: list[tuple[float, float]]) -> list[list[float]]:
    node_count = len(coordinates)
    matrix = [[0.0] * node_count for _ in range(node_count)]

    for i in range(node_count):
        x_i, y_i = coordinates[i]
        for j in range(node_count):
            x_j, y_j = coordinates[j]
            matrix[i][j] = math.hypot(x_i - x_j, y_i - y_j)

    return matrix


def load_solomon_instance(file_path: str | Path) -> CvrptwInstance:
    path = Path(file_path)
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    vehicle_count = None
    vehicle_capacity = None

    for index, line in enumerate(lines):
        if "NUMBER" in line.upper() and "CAPACITY" in line.upper():
            for next_line in lines[index + 1:]:
                parts = next_line.split()
                if len(parts) >= 2:
                    try:
                        vehicle_count = int(float(parts[0]))
                        vehicle_capacity = float(parts[1])
                        break
                    except ValueError:
                        continue
            break

    if vehicle_count is None or vehicle_capacity is None:
        raise ValueError(f"cannot read vehicle information from {path}")

    customer_rows = []
    customer_section_found = False

    for line in lines:
        upper_line = line.upper()
        if "CUSTOMER" in upper_line:
            customer_section_found = True
            continue

        if not customer_section_found:
            continue

        parts = line.split()
        if len(parts) < 7:
            continue

        try:
            row = (
                int(parts[0]),
                float(parts[1]),
                float(parts[2]),
                float(parts[3]),
                float(parts[4]),
                float(parts[5]),
                float(parts[6]),
            )
        except ValueError:
            continue

        customer_rows.append(row)

    if not customer_rows:
        raise ValueError(f"cannot read customer data from {path}")

    customer_rows.sort(key=lambda row: row[0])

    expected_ids = list(range(customer_rows[-1][0] + 1))
    actual_ids = [row[0] for row in customer_rows]
    if actual_ids != expected_ids:
        raise ValueError("customer ids must be consecutive and start from 0")

    coordinates = [(row[1], row[2]) for row in customer_rows]
    demands = [row[3] for row in customer_rows]
    time_windows = [(row[4], row[5]) for row in customer_rows]
    service_times = [row[6] for row in customer_rows]

    distance_matrix = _euclidean_matrix(coordinates)

    # Solomon benchmark convention: travel time equals Euclidean distance.
    time_matrix = [row[:] for row in distance_matrix]

    instance = CvrptwInstance(
        name=path.stem,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        demands=demands,
        time_windows=time_windows,
        service_times=service_times,
        vehicle_count=vehicle_count,
        vehicle_capacity=vehicle_capacity,
        coordinates=coordinates,
    )
    instance.validate()
    return instance
