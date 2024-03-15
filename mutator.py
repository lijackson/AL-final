from creature_gen import *
from simulator import *
import random

# set max/min (inclusive) values for random mutation

# motor sin wave styled control
# frequency of wave
FREQ_RANGE = [1, 8]

# motor strength
STREN_RANGE = [1, 10]

# period offset of wave
OFFS_RANGE = [0, 359]

# max percentage of range that we can modify values each step
SIGMA = 0.1

# set mutation probability weights
P_ADD = 0.1
P_REM = 0.1
P_MOD_STREN = 0.2
P_MOD_FREQ = 0.3
P_MOD_OFFS = 0.3
P_MOD_VALS = P_MOD_OFFS + P_MOD_STREN + P_MOD_FREQ

class Mutator:

    def mutate(rootnode):
        mutation_choice = random.choices([
            Mutator.mutate_add,
            Mutator.mutate_rem,
            Mutator.mutate_vals
        ], weights=[
            P_ADD,
            P_REM,
            P_MOD_VALS
        ], k=1)[0]

        mutation_choice(rootnode)
    
    def mutate_add(rootnode):
        possible_adds = empty_faces(rootnode)
        new_location = random.choice(possible_adds)

        new_node = gen_rand_node(new_location[1], FREQ_RANGE, STREN_RANGE, OFFS_RANGE)
        new_location[0].add_child(new_node)

    def mutate_rem(rootnode):
        leaves = get_leaves(rootnode)
        if len(leaves) == 0:
            return
        to_remove = random.choice(leaves)
        to_remove[0].remove_child(to_remove[1])

    def mutate_vals(rootnode):
        all_nodes = unwrap_nodes(rootnode)
        to_modify = random.choice(all_nodes)
        attr, range = random.choices([("strength", STREN_RANGE), ("frequency", FREQ_RANGE), ("offset", OFFS_RANGE)],
                                     [P_MOD_STREN,               P_MOD_FREQ,                P_MOD_OFFS], k=1)[0]
        
        max_delta = SIGMA * (range[1]-range[0])
        diff = random.random()*max_delta*2 - max_delta
        current = to_modify.get_joint_attr(attr)
        if current == None:
            return # attribute doesnt exist (usually this means its the root node)
        
        final_val = max(range[0], min(range[1], current + diff))
        to_modify.set_joint_attr(attr, final_val)
        

# TODO: 3d graph search to stop overlapping cubes? complicated, maybe not worth it, those creatures should die quickly anyway
def empty_faces(node):
    faces = []
    for d in range(5):
        # this direction goes back to parent
        if d == node.dir - 2*(node.dir%2) + 1:
            continue
        child = get_child_by_dir(node, d)
        if child == None:
            faces.append([node, d])
        else:
            faces += empty_faces(child)
    return faces

def get_leaves(node):
    leaves = []
    for c in node.children:
        if len(c.children) == 0:
            leaves.append((node, c)) # returns a leaf as (parent, child)
        else:
            child_leaves = get_leaves(c)
            leaves += child_leaves
    return leaves

def unwrap_nodes(node):
    nodes = [node]
    for child in node.children:
        nodes += unwrap_nodes(child)
    return nodes

def get_child_by_dir(n, d):
    for c in n.children:
        if c.dir == d:
            return c
    return None

if __name__ == "__main__":
    
    creature = get_test_creature()
    leaves = get_leaves(creature)

    print(len(leaves))





    






