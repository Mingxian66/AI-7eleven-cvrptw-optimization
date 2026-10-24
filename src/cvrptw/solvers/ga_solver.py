"""Feasible-route genetic algorithm for deterministic CVRPTW.

Route-preserving crossover, feasible neighborhood mutation, and elitism.
The shared SA route evaluator is reused to keep feasibility definitions aligned.
"""
from __future__ import annotations

import math
import random
import time
from copy import deepcopy

from ..models import CvrptwInstance, SolverResult
from .sa_solver import SaSolver


class GaSolver:
    def __init__(self, population_size: int = 24, elite_count: int = 2,
                 crossover_rate: float = 0.8, mutation_rate: float = 0.35,
                 tournament_size: int = 3, max_generations: int = 100000,
                 objective_mode: str = "lexicographic") -> None:
        if population_size < 4 or elite_count < 1 or elite_count >= population_size:
            raise ValueError("invalid population or elite size")
        if not 0 <= crossover_rate <= 1 or not 0 <= mutation_rate <= 1:
            raise ValueError("crossover_rate and mutation_rate must be in [0, 1]")
        if tournament_size < 2 or max_generations < 1:
            raise ValueError("invalid tournament size or generations")
        if objective_mode not in {"distance", "lexicographic"}:
            raise ValueError("invalid objective mode")
        self.population_size = population_size
        self.elite_count = elite_count
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.max_generations = max_generations
        self.objective_mode = objective_mode

    def solve(self, instance: CvrptwInstance, time_limit: float = 60.0,
              random_seed: int = 42) -> SolverResult:
        if time_limit <= 0:
            raise ValueError("time_limit must be positive")
        start = time.perf_counter()
        deadline = start + time_limit
        instance.validate()
        rng = random.Random(random_seed)
        evaluator = SaSolver(objective_mode=self.objective_mode, neighbor_attempts=12)
        evaluator.instance = instance
        evaluator.random = rng
        evaluator.deadline = deadline
        evaluator.vehicle_penalty = evaluator._calculate_vehicle_penalty()
        initial = evaluator._create_initial_solution()
        population = [initial]
        operators = [evaluator._relocate_neighbor, evaluator._exchange_neighbor,
                     evaluator._two_opt_neighbor]
        while len(population) < self.population_size and time.perf_counter() < deadline:
            parent = rng.choice(population)
            child = rng.choice(operators)(parent)
            population.append(child if child is not None else deepcopy(parent))
        if not population:
            raise ValueError("no feasible initial solution")
        best = min(population, key=evaluator._objective_value)
        best = deepcopy(best)
        best_score = evaluator._objective_value(best)
        best_generation = 0
        generation = 0
        crossover_count = 0
        mutation_count = 0

        def tournament():
            candidates = rng.sample(population, min(self.tournament_size, len(population)))
            return min(candidates, key=evaluator._objective_value)

        def crossover(first, second):
            # Preserve a random subset of complete feasible routes from parent 1.
            kept = [deepcopy(route) for route in first if rng.random() < 0.5]
            used = {node for route in kept for node in route[1:-1]}
            order = [node for route in second for node in route[1:-1] if node not in used]
            child = kept
            for customer in order:
                if time.perf_counter() >= deadline:
                    return None
                choices = []
                for index, route in enumerate(child):
                    old_distance = evaluator.route_distance(route)
                    for pos in range(1, len(route)):
                        trial = route[:pos] + [customer] + route[pos:]
                        if evaluator.is_feasible_route(trial):
                            choices.append((evaluator.route_distance(trial) - old_distance, index, trial))
                if len(child) < instance.vehicle_count:
                    trial = [0, customer, 0]
                    if evaluator.is_feasible_route(trial):
                        choices.append((evaluator.route_distance(trial), len(child), trial))
                if not choices:
                    return None
                _, index, route = min(choices, key=lambda item: item[0])
                if index == len(child):
                    child.append(route)
                else:
                    child[index] = route
            child = evaluator._normalize_solution(child)
            return child if evaluator.is_feasible_solution(child) else None

        while generation < self.max_generations and time.perf_counter() < deadline:
            population.sort(key=evaluator._objective_value)
            next_population = [deepcopy(item) for item in population[:self.elite_count]]
            while len(next_population) < self.population_size and time.perf_counter() < deadline:
                parent_a = tournament()
                parent_b = tournament()
                child = None
                if rng.random() < self.crossover_rate:
                    child = crossover(parent_a, parent_b)
                    crossover_count += 1
                if child is None:
                    child = deepcopy(parent_a)
                if rng.random() < self.mutation_rate:
                    mutated = rng.choice(operators)(child)
                    if mutated is not None:
                        child = mutated
                        mutation_count += 1
                next_population.append(child)
                score = evaluator._objective_value(child)
                if score + 1e-9 < best_score:
                    best, best_score = deepcopy(child), score
                    best_generation = generation + 1
            if len(next_population) < self.population_size:
                break
            population = next_population
            generation += 1
        return SolverResult(
            solver_name="ga", instance_name=instance.name, routes=best,
            total_distance=evaluator.total_distance(best),
            total_duration=evaluator.total_duration(best), vehicles_used=len(best),
            feasible=evaluator.is_feasible_solution(best),
            runtime_seconds=time.perf_counter() - start, iterations=generation,
            best_iteration=best_generation, random_seed=random_seed,
            objective_mode=self.objective_mode, objective_value=best_score,
            operator_statistics={},
            extra={"population_size": self.population_size,
                   "elite_count": self.elite_count,
                   "crossover_attempts": crossover_count,
                   "successful_mutations": mutation_count},
        )
