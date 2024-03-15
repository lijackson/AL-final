
from creature_gen import *
from simulator import *
from mutator import *
from evolver import *

def sim_generation():
    timer = time.time()

    evo = Evolver(50)
    evo.score_population()
    best = evo.get_best_performer_id()
    print(f"total time for generation of 5: {time.time()-timer}\n best score: {evo.scores[best]}")
    print(f"scores: {sorted(evo.scores.values())}")
    print(f"chosen for culling: {sorted([evo.scores[cid] for cid in evo.cull()])}")

    for c in evo.population:
        env = Environment()
        env.assemble(evo.population[c])

        sim = Simulator()
        sim.load_env(env)
        sim.view_sim(1000)

def sim_test_creature():
    c = get_test_creature()

    env = Environment()
    env.assemble(c)

    sim = Simulator()
    sim.load_env(env)
    sim.view_sim(1000)

def test_mutator():
    c = get_test_creature()
    for _ in range(100):
        Mutator.mutate(c)

    env = Environment()
    env.assemble(c)

    sim = Simulator()
    sim.load_env(env)
    sim.view_sim(1000)

def test_cloner():
    c = get_test_creature()
    for _ in range(40):
        Mutator.mutate(c)

    for i in range(5):
        env = Environment()
        sim = Simulator()
        c = clone_node_tree(c)
        env.assemble(c)
        sim.load_env(env)
        sim.run_sim(300)
        print(sim.score())

if __name__ == "__main__":
    sim_test_creature()