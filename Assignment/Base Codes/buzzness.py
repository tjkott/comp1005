# Student Name: <put your name here> 
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information: 
#     2024-04-07 : Initial Version released
#
import random

class Bee():
    """
    Provides state and behaviour for worker bee in the simulation
    """

    def __init__(self, ID, pos):
        """
        Initialise Bee object
        ID:  identifier for the bee
        pos: (x,y) position of bee
        age: set to zero at birth
        inhive: is the bee inside the hive, or out in the world?, True at birth
        """
        self.ID = ID
        self.pos = pos
        self.age = 0
        self.inhive = True

    def step_change(self, subgrid=None):
        """
        Update Bee object on each timestep
        subgrid: gives view of surroundings for choosing where to move (not used for now)
        """
        validmoves = [(1,0),(1,1),(-1,-1)]     # list of valid moves
        move = random.choice(validmoves)       # randomly choose a move
        print(self.pos, move)
        # need to update the position based on the move
        
    def get_pos(self):
        return self.pos
    
    def get_inhive(self):
        return self.inhive
    
    def set_inhive(self, value):
        self.inhive = value
