from typing import Dict, Any
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import time
from Functions import *

max_init_speed: tuple = (1, 1, 1)
max_acceleration: tuple = (0.5, 0.5, 0.5)
to_keep = 0.01 # how many best particles are "elite"


class space:

    def __init__(self, num_particles: int, init_space_dimension: float):
        self.num_particles = num_particles
        self._init_create_particles(init_space_dimension)
        self.anchors: list = []
        self.last_time = time.perf_counter()

    def _init_create_particles(self, space_dimension) -> None:
        
        self.particles: list =  []

        for _ in range(self.num_particles):

            velocity: list = []
            for max_speed_dimenion in max_init_speed:
                velocity.append(np.random.uniform(high=max_speed_dimenion))

            position: list = []
            for dimension in space_dimension:
                position.append(np.random.uniform(high=dimension))

            self.particles.append(particle(position, velocity))

            
    def update_space(self, anchor_name: str, distance: float, time: float):
        
        if not any(i.name == anchor_name for i in self.anchors):
            print(f"unknown anchor {anchor_name} meassurment is ignored")
            return
        
        for i in self.anchors:
                if i.name == anchor_name:
                    anchor_position = i.position
        
        timestep = self._get_timestep(time)

        for particle in self.particles:
            particle.new_meassurment(anchor_position, timestep, distance)

    def _get_timestep(self, time) -> float:
        timestep = (time - self.last_time)
        self.last_time = time
        return timestep

    def evolve_space(self) -> None:
        sorted_particles = sorted(self.particles, reverse=True)
        to_remove = int((1-to_keep) * len(sorted_particles))
        self.particles = sorted_particles[:-to_remove]


    def get_tag_position(self) -> list:
        #averages top x% of pratricles, returns [position, velocity]
        None

    def update_anchor(self, anchor_name: str, position: list) -> None:

        if not any(i.name == anchor_name for i in self.anchors):
            self.anchors.append(anchor(anchor_name, position))

        else:
            for i in self.anchors:
                if i.name == anchor_name:
                    i.position = position
        
    def visualize(self) -> None:

        size = 1

        all_particles = [particle.get_particle_position() for particle in self.particles]
        particle_x, particle_y, particle_z = zip(*all_particles)

        all_anchors = [anchor.position for anchor in self.anchors]
        anchor_x, anchor_y, anchor_z = zip(*all_anchors)

        # Create the plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot all particles in one call
        ax.scatter(particle_x, particle_y, particle_z, marker="x", s = size)
        ax.scatter(anchor_x, anchor_y, anchor_z, marker="h", s = size*20)

        # Set labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.axis('equal')

        plt.show()



class particle:

    
    #velocity boundaries

    def __init__(self, position: list, velocity: list):

        #random velocity from given
        self.position = np.array(position)
        self.velocity = np.array(velocity)

        self.std_deviation = 0.027

    def new_meassurment(self, anchor_position: float, timestep_delta, distance_m: float) -> None:
        self._update_particle(timestep_delta)
        self._dist_to_anchor(anchor_position)
        self._calculate_fit(distance_m)

    def _update_particle(self, timestep: float) -> None:
        self.position = self.position + (self.velocity * timestep)

    def _dist_to_anchor(self, anchor_position: float) -> None:
        self.to_anchor: float = np.linalg.norm(self.position - np.array(anchor_position))

    def _calculate_fit(self, distance_m: float) -> None:
        self.fit=normal_dist(self.to_anchor, self.std_deviation, distance_m)

    def get_particle_position(self) -> list:
        return self.position


    def __lt__(self, value):
         return self.fit < value.fit


@dataclass
class anchor:
    name: str
    position: list #XYZ