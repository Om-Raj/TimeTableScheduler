import copy
import random
import time
from bisect import bisect_left
from math import exp


class Schedule:
    def __init__(self, slots, fitness):
        self.slots = slots
        self.fitness = fitness
        self.age = 0    # Age of genetic line for Simulated Annealing


class GeneticAlgorithm:

    def __init__(self, fnGetFitness, fnCreate, fnMutate, fnDisplay, max_age):
        self.get_fitness = fnGetFitness
        self._create = fnCreate
        self._mutate = fnMutate
        self.display = fnDisplay
        self.max_age = max_age

    def generate_parent(self):
        slots = self._create()
        return Schedule(slots, self.get_fitness(slots))


    def mutate(self, parent):
        slots = copy.deepcopy(parent.slots)
        self._mutate(slots)
        fitness = self.get_fitness(slots)
        return Schedule(slots, fitness)

    def _get_improvement(self, start_time, time_limit):
        best_parent = parent = self.generate_parent()
        historical_fitness = [best_parent.fitness]
        yield best_parent
        while True:
            if time.time() - start_time > time_limit:
                return

            child = self.mutate(parent)
            if parent.fitness > child.fitness:
                if self.max_age is None:
                    continue
                parent.age += 1
                if self.max_age > parent.age:
                    continue
                index = bisect_left(historical_fitness, child.fitness, 0, len(historical_fitness))
                proportion_similar = index / len(historical_fitness)
                if random.random() < exp(-proportion_similar):
                    parent = child
                    continue
                best_parent.age = 0
                parent = best_parent
                continue
            if not child.fitness > parent.fitness:
                child.age = parent.age + 1
                parent = child
                continue
            parent = child
            if child.fitness > best_parent.fitness:
                best_parent = child
                yield best_parent
                historical_fitness.append(best_parent.fitness)


    def get_best(self, optimal_fitness, time_limit):
        start_time = time.time()
        last_improvement = None
        for improvement in self._get_improvement(start_time, time_limit):
            last_improvement = improvement
            self.display(improvement)
            if not optimal_fitness > improvement.fitness:
                return improvement
        return last_improvement
