Artificial Life Final Project - Liam Jackson

Background:
Just a little bit of description: this simulation uses cubes connected by actuators to build a "creature"
I chose this design because it was the most flexible, and I thought would result in the most visible evolution,
since you can see the physical changes to the creature, and they are pretty unrestricted
Each generation, the worst performers are eliminated, and the best performers get a chance to duplicate. Then
all the remaining creatures get mutated to finalize the next generation. I chose to mutate even the best
performers because if I kept them unmutated, they would continue to beat all of the mutated offspring in the
next generation, stifling the evolution. With increased randomness, it stopped the simulator from getting stuck
in local maximums.
Another note, it kept trying to cheat the physics simulator. I had a bug where the muscle strength was uncapped,
and the top performing creature figured out a way to spin up to unholy speeds, hit the ground with the force of
a neutron star, and promptly crashed the simulation.


How to use this project yourself!

Basic use:
 - run "runner.py" to run evolution with a population size of 80 for 500 generations. This will take a while
 - To edit the population size, you can simply change the values passed into "Evolver(<population_size>)"
 - To edit the number of generations, you can simply change the values passed into "evo.evolve(<num_gens>)"

 More options / using Evolver:
  - Evolver.evolve(num_gens: int, term_fit_freq=5: int, disp_freq=100: int)
    - num_gens is the number of generations being run
    - term_fit_frequency: is the frequency with which the top performer / highest fitness is logged in the terminal
    - disp_freq: is the frequency with which a simulation of the top performer is displayed

Getting into some more fine-tuning things:

Constants to mess with:
 - creature_gen.py
   - JROM: the range of motion for the joints between the cubes
   - SPAWN_H: how high the root node block spawns
 - mutator.py
   - FREQ_RANGE: the range of allowed values for the wave frequency of muscle activation
   - STREN_RANGE: the range of allowed values for the muscle strength
   - OFFS_RANGE: the range of allowed values for the wave offset of muscle activation
   - SIGMA: the amount that a muscle attribute is allowed to be mutated, by fraction of range size
   - P_...: probability of each type of mutation being chosen
