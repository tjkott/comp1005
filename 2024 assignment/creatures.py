import numpy as np
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Puppy():
    def __init__(self, name, colour, pos):
        self.name = name
        self.colour = colour
        self.pos = pos
        self.energy = 100 

    def get_pos(self):
        return self.pos

    def step_change(self, limits):
        validmoves = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
        move = random.choice(validmoves)
        new_pos = (self.pos[0] + move[0], self.pos[1] + move[1], self.pos[2] + move[2])
        if (0 <= new_pos[0] < limits[0]) and (0 <= new_pos[1] < limits[1]) and (0 <= new_pos[2] < limits[2]):
            self.pos = new_pos

    def consume_food(self, food_pos): 
        if np.linalg.norm(np.array(food_pos) - np.array(self.pos)) <= 4: # if puppy is within 4 units of food, its energy is replenished. 
            self.energy = 100  

class Cat():
    def __init__(self, name, colour, pos):
        self.name = name
        self.colour = colour
        self.pos = pos
        self.energy = 100  # Initial energy level

    def get_pos(self):
        return self.pos

    def step_change(self, house_bounds):
        validmoves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        move = random.choice(validmoves)
        new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
        if (house_bounds[0][0] <= new_pos[0] < house_bounds[1][0]) and \
           (house_bounds[0][1] <= new_pos[1] < house_bounds[1][1]):
            self.pos = (new_pos[0], new_pos[1], 0)

    def consume_food(self, food_pos):
        if np.linalg.norm(np.array(food_pos) - np.array(self.pos)) <= 4: # if cat is within 4 units of food, its energy is replenished. 
            self.energy = 100  

class Squirrel():
    def __init__(self, name, colour, pos):
        self.name = name
        self.colour = colour
        self.pos = pos

    def get_pos(self):
        return self.pos

    def step_change(self, limits, house_bounds):
        validmoves = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        move = random.choice(validmoves)
        new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
        # Ensure new position is within the backyard boundaries and outside the house boundaries
        if ((0 <= new_pos[0] < limits[0]) and (0 <= new_pos[1] < limits[1])) and \
           (not ((house_bounds[0][0] <= new_pos[0] < house_bounds[1][0]) and 
                 (house_bounds[0][1] <= new_pos[1] < house_bounds[1][1]))):
            self.pos = (new_pos[0], new_pos[1], 0)