# Student Name: <put your name here> 
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information: 
#     2024-04-07 : Initial Version released
#
import random

class Bee(): # Providing state and behaviour for worker bee in the simulation
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

    def step_change(self, subgrid=None, maxX=None, maxY=None): # sets default value of the maxX parameter to be None (empty value)
        """
        Update Bee object on each timestep
        subgrid: gives view of surroundings for choosing where to move (not used for now)
        Made changes so that bees don't move outside the boundary of the plots. 
        """
        # maxX and maxY are the maximum coordinate boundaries of the plot. 
        validmoves = [(0,0), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]  ## (d) In the Bee, update the valid moves to inlcude all 9 Moore neighbouhoods. 

        # Try to find a valid move that keeps the bee within boundaries
        valid_step = False #default assumption of hte new step is false. 
        attempts = 0
        max_attempts = 10  # In order to prevent infinite loop
        
        while not valid_step and attempts < max_attempts:
            move = random.choice(validmoves)  # randomly choose a move out of the validmoves array. 
            newX = self.pos[0] + move[0]
            newY = self.pos[1] + move[1]
            
            if maxX is None or maxY is None: # Check if new position is within boundaries
                valid_step = True
            else:
                if 0 <= newX < maxX and 0 <= newY < maxY: #Ensure the new position is in between the origin and the max coordinates of the pot. 
                    valid_step = True
            attempts += 1
        
        if valid_step: 
            print(f"{self.ID}: {self.pos} -> {(newX, newY)}")
            self.pos = (newX, newY)  # update the position of the bee
        else:
            # If no valid_steps found after max attempts, stay in place
            print(f"{self.ID}: Staying at {self.pos} (no valid moves)")

        # Remove the duplicate position update that was causing bugs
        # print(self.pos, move)
        # self.pos = (self.pos[0] + move[0], self.pos[1] + move[1]) <- This line was causing bees to move outside boundaries
    
    def get_pos(self):
        return self.pos
    
    def get_inhive(self):
        
        return self.inhive
    
    def set_inhive(self, value):
        self.inhive = value

