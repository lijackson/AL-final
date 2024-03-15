from creature_gen import *
from simulator import *
from mutator import *
from evolver import *

def run_evolution():
    # pass the population size to the evolver
    evo = Evolver(80)

    # evolve however many generations you want to see
    evo.evolve(500)

if __name__ == "__main__":
    run_evolution()
    