from creature_gen import *
from simulator import *
from mutator import *
import pickle

# number of sim steps, mapped to 10ms each
SIMTIME = 500 # 5 is a little too short

SCORE_DIST_W = 1000 # how much should traveled distance impact score
SCORE_ENERGY_W = -0.1 # how much should amount of used energy impact score

class Evolver:

    population = None
    scores = None
    best_seen = None

    def __init__(self, pop_size):
        self.best_seen = [None, None]
        self.saved_xml_creatures = []
        self.population = {}
        self.scores = {}
        for _ in range(pop_size):
            # get empty creature
            new_creature = get_default_creature()

            # add 2 units to the creature, give us something to work with
            Mutator.mutate_add(new_creature)
            Mutator.mutate_add(new_creature)
            Mutator.mutate_add(new_creature)
            Mutator.mutate_add(new_creature)

            # add creature to population
            self.population[new_creature.id] = new_creature
        
        # we need to start off with population scores (for consistency)
        self.score_population()

    def score_population(self):
        self.scores = {}
        for cid, creature in self.population.items():
            self.scores[cid] = self.score(creature)

    def score(self, creature):
        env = Environment()
        env.assemble(creature)

        sim = Simulator()
        sim.load_env(env)
        sim.run_sim(SIMTIME)

        # most important part of fitness is distance traveled
        score = -SCORE_DIST_W*(sim.d.body("rootnode").xpos[0] + sim.d.body("rootnode").xpos[1])

        
        return score

    def cull(self):
        pop_ids = list(self.population.keys())
        sort_by_perf = sorted(pop_ids, key=lambda cid:self.scores[cid])
        to_kill_ids = sort_by_perf[:len(sort_by_perf)//2]

        for cid in to_kill_ids:
            del self.population[cid]

    def reproduce(self):
        offspring = []
        for cid in self.population:
            new_creature = clone_node_tree(self.population[cid])
            Mutator.mutate(new_creature)
            offspring.append(new_creature)
        
        for creature in offspring:
            self.population[creature.id] = creature

        for cid in self.population:
            Mutator.mutate(self.population[cid])

    def next_generation(self):
        self.cull()
        self.reproduce()
        self.score_population()

    def evolve(self, num_gens, term_fit_freq=5, fdump_freq=100):
        self.best_seen = [None, 0]
        for gen in range(num_gens+1):
            self.next_generation()
            bestid = self.get_best_performer_id()
            if self.scores[bestid] > self.best_seen[1]:
                self.best_seen = [self.population[bestid], self.scores[bestid]]
            if gen%term_fit_freq == 0:
                print(f"[GEN {gen}] peak fitness: {self.scores[bestid]}")
            if gen%fdump_freq == 0:
                creature = self.population[bestid]

                env = Environment()
                env.assemble(creature)

                sim = Simulator()
                sim.load_env(env)
                sim.view_sim(SIMTIME)
        
            

    def get_best_performer_id(self):
        best = None
        for id in self.population:
            if best == None or self.scores[best] < self.scores[id]:
                best = id
        
        return best
    
