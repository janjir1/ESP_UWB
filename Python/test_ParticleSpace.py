from ParticleSpace import space
import time

init_space_dimension = [2, 4, 2]
particleSpace = space(10000, init_space_dimension)

particleSpace.update_anchor("11a1", [1, 1, 1])

start_time = time.perf_counter()
meassurment = 0.5
name = "11a1"

particleSpace.update_space(name, meassurment, start_time)
particleSpace.evolve_space()
particleSpace.visualize()




