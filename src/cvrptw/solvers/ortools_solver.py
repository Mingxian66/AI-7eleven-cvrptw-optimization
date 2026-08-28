"""Google OR-Tools solver placeholder.

The OR-Tools implementation will use the same CvrptwInstance and SolverResult
interfaces as the SA benchmark so all algorithms can be compared fairly.
"""


class OrtoolsSolver:
    def solve(self, *args, **kwargs):
        raise NotImplementedError("OR-Tools solver will be implemented in the next stage")
