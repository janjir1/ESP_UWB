from typing import Dict, Any
import numpy as np
from dataclasses import dataclass
import os, csv
import time
from Functions import *
from numba import njit, float64, float32

max_init_speed: tuple = (1, 1, 1)
max_acceleration = np.array([10, 10, 10])
to_keep = 0.1 # how many best particles are "elite"


class space:

    def __init__(self, num_particles: int, init_space_dimension: list):
        self.num_particles = num_particles
        self._init_create_particles(init_space_dimension)
        self.anchors: list = []
        self.last_time = time.perf_counter()
        self.runVisualize = True
        self.init_space_dimension = init_space_dimension
        self.last_tag = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        self.tag = np.empty((2, len(self.init_space_dimension)), dtype=np.float64)

    def _init_create_particles(self, space_dimension) -> None:
        
        self.particles: list =  []

        for _ in range(self.num_particles):

            velocity: list = []
            for max_speed_dimenion in max_init_speed:
                velocity.append(np.random.uniform(high=max_speed_dimenion))

            position: list = []
            for dimension in space_dimension:
                position.append(np.random.uniform(high=dimension))

            self.particles.append(particleClass(position, velocity))

            
    def update_space(self, anchor_name: str, distance: float, time: float) ->bool:
        
        if not any(i.name == anchor_name for i in self.anchors):
            print(f"unknown anchor {anchor_name} meassurment is ignored")
            return False
        
        for i in self.anchors:
                if i.name == anchor_name:
                    anchor_position = i.position
        
        self._get_timestep(time)

        
        for particle in self.particles:
            particle.new_meassurment(anchor_position, self.timestep, distance)
        

        #print(f"Update from {anchor_name}, distance {distance:.2f} m, timestep {self.timestep:.2f}, average fit {self.average_fit():.2f}")

        return True

    def _get_timestep(self, time):
        self.timestep = (time - self.last_time)
        self.last_time = time


    def evolve_space(self) -> None:        
        self.sorted_particles = sorted(self.particles, reverse=True)
        to_remove = int((1-to_keep) * len(self.sorted_particles))
        self.sorted_particles =  self.sorted_particles[:-to_remove]

        self.particles =  self.sorted_particles.copy()

        offsprings = int((1/to_keep)-1)

        for particle in self.sorted_particles:
            self._multipy_partcle(particle, offsprings)




    def _multipy_partcle(self, particle, replicate: int):
        position = particle.get_particle_position()
        velocity_parent = np.array(particle.get_particle_velocity())

        for _ in range(replicate):
            velocity = daughter_particle_velocity(velocity_parent, self.timestep)
            self.particles.append(particleClass(position, velocity))


    def update_anchor(self, anchor_name: str, position: list) -> None:

        if not any(i.name == anchor_name for i in self.anchors):
            self.anchors.append(anchorClass(anchor_name, position))

        else:
            for i in self.anchors:
                if i.name == anchor_name:
                    i.position = position
        
    def visualize(self) -> None:

        if self.runVisualize:
            self.runVisualize = False
            os.system("start python visualize.py")

        namafile = 'visualize.csv'
        fieldnames = ["x_coord", "y_coord", "z_coord", "type"]

        particle_positions = []
        for particle in self.sorted_particles:
            line = particle.get_particle_position()
            line.append("particle")
            particle_positions.append(line)


        anchor_positionis = []
        for anchor in self.anchors:
            line = anchor.position.copy()
            line.append("anchor")
            anchor_positionis.append(line)

        tag_position = self.tag[0].tolist()
        tag_position.append("tag_position")

        tag_velocity = self.tag[1].tolist()
        tag_velocity.append("tag_velocity")

        

        with open(namafile, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fieldnames)
            csv_writer.writerows(particle_positions)
            csv_writer.writerows(anchor_positionis)
            csv_writer.writerow(tag_position)
            csv_writer.writerow(tag_velocity)


    def average_fit(self) -> float:
        average_fit: float = 0
        for particle in self.particles:
            average_fit = average_fit + particle.get_fit()

        return average_fit/len(self.particles)
    
    def calculate_tag(self) -> None:
        particle_positions = np.empty((len(self.sorted_particles), len(self.init_space_dimension)), dtype=np.float64)
        particle_velocities = np.empty((len(self.sorted_particles), len(self.init_space_dimension)), dtype=np.float64)
        n=0
        for particle in self.sorted_particles:
            particle_positions[n] = particle.get_particle_position()
            particle_velocities[n] = particle.get_particle_velocity()
            n+=1
        
        #average_particle_position = get_average(particle_positions)
        #average_particle_velocity = get_average(particle_velocities)

        """
        if self.last_tag not in vars():
            self.last_tag = np.array([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
            self.tag = np.empty((2, len(self.init_space_dimension)), dtype=np.float64)
        """
        
        #TODO - average of self.last_tag[0] a average_particle_position
        #self.tag[0] = np.mean(np.vstack((self.last_tag[0], average_particle_position)), axis = 0)
        #self.tag[1] = np.mean(np.vstack((self.last_tag[1], average_particle_velocity)), axis = 0)
        self.tag[0] = get_average(particle_positions)
        self.tag[1] = get_average(particle_velocities)

        #self.last_tag = self.tag.copy()
        self._log_tag()

    def _log_tag(self):

        namafile = 'tag_log.csv'

        fieldnames = ["x_coord", "y_coord", "z_coord", "x_speed", "y_speed", "z_speed"]

        line = self.tag[0].tolist()
        line.append(self.tag[1].tolist())

        if os.path.exists(namafile):
            with open(namafile, 'a') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(line)
        else:
            with open(namafile, 'w') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(fieldnames)
                csv_writer.writerow(line)


class particleClass:
    #velocity boundaries

    def __init__(self, position: list, velocity: list):

        #random velocity from given
        self.position = np.array(position)
        self.velocity = np.array(velocity)

        self.std_deviation = 0.027

    def new_meassurment(self, anchor_position: float, timestep_delta, distance_m: float) -> None:
        #self._update_particle(timestep_delta)
        self.position = update_particle(timestep_delta, self.position, self.velocity)
        #self._dist_to_anchor(anchor_position)
        self.to_anchor = dist_to_anchor(np.array(anchor_position), self.position)
        #self._calculate_fit(distance_m)
        self.fit=normal_dist(self.to_anchor, self.std_deviation, distance_m)

    
    def _update_particle(self, timestep: float) -> None:
        self.position = self.position + (self.velocity * timestep)

    def _dist_to_anchor(self, anchor_position: float) -> None:
        self.to_anchor: float = np.linalg.norm(self.position - np.array(anchor_position))

    def _calculate_fit(self, distance_m: float) -> None:
        self.fit=normal_dist(self.to_anchor, self.std_deviation, distance_m)

    def get_particle_position(self) -> list:
        return self.position.tolist()
    
    def get_particle_velocity(self) -> list:
        return self.velocity.tolist()
    
    def get_fit(self) -> float:
        return self.fit

    def __lt__(self, value):
         return self.fit < value.fit


@dataclass
class anchorClass:
    name: str
    position: list #XYZ

@njit(float64(float64[:]), cache=True)
def custom_norm(arr):
    return np.sqrt(np.sum(arr ** 2))

@njit(float64(float64[:], float64[:]), cache=True)
def dist_to_anchor(anchor_position, position):
    return custom_norm(position - anchor_position)

@njit(float32(float32, float32, float32), cache=True)
def normal_dist(mean, std_deviation, number):
    exp = ((number - mean) / std_deviation) ** 2 / 2
    return (1 / (std_deviation * (2 * pi) ** 0.5)) * euler ** (-exp)

@njit(float64[:](float64, float64[:], float64[:]), cache=True)
def update_particle(timestep, position, velocity):
        return (position + (velocity * timestep))

@njit(float64[:](float64[:], float64), cache=True)
def daughter_particle_velocity(velocity_parent, timestep):
    random = np.random.random(3) -0.5
    return velocity_parent + ((random * max_acceleration * 2) * timestep)

#@njit(float64[:](float64[:]), cache = True)
def get_average(array):
    return np.mean(array, axis = 0)
    