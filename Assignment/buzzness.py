# Student Name: Thejana Kottawatta Hewage
# Student ID:   22307822
#
# buzzness.py - module with class definitions for beeworld.py
#
# Version information: 
#     2024-04-07 : Initial Version released
#

import random
import argparse # Used for command-line argument parsing
import csv      # Used for reading CSV files for map and parameters
import numpy as np
import matplotlib.pyplot as plt

class Flower(): # 
    """
    Flower class
    """
    def __init__(self, ID, pos, name, colour, nectarCapacity=5, dead_duration=10):
        """
        Initialise Flower object
        ID: unique identifier for the flower
        pos: x, y tuple for the flower's position within the property
        name: string name of the flower type (e.g., "Rose")
        colour: string color of the flower (e.g., "Red")
        nectarCapacity: maximum nectar units the flower can hold
        currentNectar: Flower starts full of nectar
        state: Initial state of the flower - 'ALIVE' or 'DEAD'
        regeneration_cooldown: timer for when a 'DEAD' flower can start refilling
        deadDuration: timesteps the flower stays dead after nectar depletion
        is_refilling: State to describe that the flower is in the process of refilling nectar
        """
        self.ID = ID
        self.pos = pos 
        self.name = name # e.g.: "Rose", "Tulip"
        self.colour = colour # e.g. "Red", "Yellow"
        self.nectarCapacity = nectarCapacity # Maximum nectar this flower can hold
        self.currentNectar = nectarCapacity # Flower starts full of nectar
        self.state = 'ALIVE' 
        self.regeneration_cooldown = 0
        self.deadDuration = dead_duration # How long the flower remains in the DEAD state
        self.is_refilling = False 

    def get_pos(self):
        """
        Returns the x, y position of the flower.
        """
        return self.pos

    def get_nectar(self):
        """
        Returns the current amount of nectar in the flower.
        """
        return self.currentNectar

    def take_nectar(self, amount=1):
        """
        Method for a bee to take nectar
        amount: the amount of nectar the bee attempts to take
        Returns the amount of nectar actually taken.
        """
        taken = min(amount, self.currentNectar) # Bee cannot take more nectar than what is currently available at the time step
        self.currentNectar -= taken 
        if self.currentNectar <= 0 and self.state == 'ALIVE': #If flower runs out of nectar
            self.currentNectar = 0 # Ensure nectar doesn't go negative
            self.state = 'DEAD' # Set flower state to "DEAD"
            self.regeneration_cooldown = self.deadDuration # Start "DEAD" state cooldown"
            self.is_refilling = False # No longer refilling if it is "DEAD:"
            print(f"Flower {self.ID} ({self.name}) is now DEAD.")
        elif self.currentNectar > 0: 
            self.is_refilling = False # If nectar is taken but not depleted, it's not in the special "refilling from dead" state
        return taken

    def regenerate_nectar(self, rate=1): # 
        """
        Method for flower to regenerate nectar over time
        rate:  amount of nectar to regenerate per timestep
        
        """
        if self.state == 'DEAD': 
            if self.regeneration_cooldown > 0:
                self.regeneration_cooldown -= 1 # Countdown the cooldown timer
            else: 
                self.state = 'ALIVE' # Flower gets "ALIVE" state once cooldown is finished. 
                self.is_refilling = True # Enters a state of actively refilling its nectar from 0. 
                print(f"Flower {self.ID} ({self.name}) is ALIVE and has started refilling  nectar.")
        if self.state == 'ALIVE' and self.is_refilling: # Only regenregenerates rates if it just became ALIVE or is explicitly refilling
            if self.currentNectar < self.nectarCapacity:
                self.currentNectar = min(self.nectarCapacity, self.currentNectar + rate) 
                if self.currentNectar == self.nectarCapacity:
                    self.is_refilling = False # Stop the special refilling state once full
                    print(f"Flower {self.ID} ({self.name}) has maximum nectar.")
    def is_available_for_bees(self):
        """Returns: TRUE if flower is in the state = "ALIVE" and has nectar>0"""
        return self.state == 'ALIVE' and self.currentNectar > 0

class Bee(): 
    def __init__(self, ID, initial_pos, hive_entrance_pos, max_nectarCarry=1, empty_flower_avoiding_duration=20, max_clogCount=5):
        """
        Initialises the Bee class.
        - ID: Identification for bees. 
        - initial_pos: inital x, y starting position of the bee inside the hive
        - hive_entrance_pos: x, y location of the hive entrance on the property plot. 
        - max_nectarCarry: maximum nectar units the bee can carry
        - empty_flower_avoiding_duration: no. of timesteps a bee avoids a flower it just emptied
        - clogCount: no. of timesteps a bee can be stuck before resetting its state/task
        - max_clogCount: no. of timesteps a bee can be stuck before resetting its task
        """
        self.ID = ID
        self.pos = initial_pos 
        self.hive_entrance_pos = hive_entrance_pos #  entrance of the hive
        self.age = 0 # Age per bee in terms of timesteps
        self.inhive = True # True if bee is inside the hive, False if in property
        self.state = 'IDLE_IN_HIVE' # Current behavioural state of the bee
        self.nectarCarried = 0 # Amount of nectar the bee is carrying at given timestep. 
        self.max_nectarCarry = max_nectarCarry # Maximum nectar capacity for this bee
        self.current_move_pos = None # Target moving x, y pos of the bee. 
        self.current_move_object = None # Target object of the bee. 
        self.path = []
        self.recently_emptied_flowers = {} # recently depleted flowers by the bee. 
        self.empty_flower_avoiding_duration = empty_flower_avoiding_duration # How long to avoid an emptied flower
        self.clogCount = 0 
        self.max_clogCount = max_clogCount # Maximum timesteps of being stuck

    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config, current_timestep, other_bees_details_list): # Main update logic for the bee each timestep
        """
        Update Bee per new timestep taking into account both object's state and setting (property vs. hive)
        property_map_data:   numpy array of the main property terrain
        flowers_list:   list of Flower objects
        hive_data:   numpy array representing the hive's internal state (combs, nectar)
        hive_layout_config:   dictionary with hive dimensions and fixed points
        property_config:   dictionary with property dimensions and hive location
        current_timestep:   the current simulation time
        other_bees_details_list:   list of dicts with info about other bees for collision avoidance

        **BEE STATES**
        - IDLE_IN_HIVE
        - IDLE_ON_PROPERTY
        - MOVING_TO_HIVE_EXIT
        - SEEKING_FLOWER
        - MOVING_TO_FLOWER
        - COLLECTING_NECTAR
        - RETURNING_TO_HIVE_ENTRANCE
        - MOVING_TO_COMB_BUILD_SITE
        - BUILDING_COMB
        - MOVING_TO_COMB_DEPOSIT_SITE
        """
        self.age += 1 #Bee's timestep age
        moved_during_current_timestep = False 
        occupiedPos = set() # for avoiding 2 bees occupying the same pos. 
        if self.inhive: # if bee is in the hive
            occupiedPos = {info['pos'] for info in other_bees_details_list if info['inhive']}
        else: # If bee is on the property
            occupiedPos = {info['pos'] for info in other_bees_details_list if not info['inhive']}
        ## (1) BEE STATES
        if self.state == 'IDLE_IN_HIVE': # IDLE_IN_HIVE = bee is in the hive, no task. 
            self.clogCount = 0
            moved_during_current_timestep = True #Got assigned task
            if self.nectarCarried >= 1 and self.build(hive_data, hive_layout_config): # If bee carrying nectar and build comb. 
                comb_build_target_pos = self.buildFrames(hive_data, hive_layout_config) # Try to find a place to build comb
                if comb_build_target_pos: # if build pos is decided:
                    self.current_move_pos = comb_build_target_pos
                    self.state = 'MOVING_TO_COMB_BUILD_SITE' # MOVING_TO_COMB_BUILD_SITE = bee is moving to the determined pos to build comb
                    print(f"Bee {self.ID} (in hive) is assigned to build comb at {self.current_move_pos}.")
                else: 
                    comb_deposit_target = self.depositNectar(hive_data, hive_layout_config)
                    if comb_deposit_target: # If a nectar deposit site is found
                        self.current_move_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE' # MOVING_TO_COMB_DEPOSIT_SITE = bee is moving to the determined pos to build comb. 
                        print(f"Bee {self.ID} (in hive) is assigned to deposit nectar at {self.current_move_pos}.")
                    elif self.nectarCarried < self.max_nectarCarry: # Has nectar, but everything too else too busy to build at current timestep. Therefore, collect more nectar from property. 
                        self.current_move_pos = hive_layout_config['hive_exit_cell_inside'] # Target internal hive exit
                        self.state = 'MOVING_TO_HIVE_EXIT' # MOVING_TO_HIVE_EXIT = bee is moving to twoards hive entrance to go collect more nectar
            elif self.nectarCarried < self.max_nectarCarry: 
                self.current_move_pos = hive_layout_config['hive_exit_cell_inside'] 
                self.state = 'MOVING_TO_HIVE_EXIT' 
                print(f"Bee {self.ID} (in hive) needs more nectar, heading to property.")
        # Prventing clogging at the hive entrance
        elif self.state == 'MOVING_TO_HIVE_EXIT': # Bee is moving towards the exit pos of the hive
            if self.pos == self.current_move_pos: # if bee already at the hive exit pos
                hive_exit_pos = self.hive_entrance_pos # = property entrace from the hive
                property_entrace_into_hive = False # Check if another bee is blocking the property spohive entry pos.
                for other_bee_info in other_bees_details_list:
                    if not other_bee_info['inhive'] and other_bee_info['pos'] == hive_exit_pos:
                        property_entrace_into_hive = True
                        break
                if property_entrace_into_hive: 
                    moved_during_current_timestep = self.moveRandomly(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupiedPos) # Jiggle inside near exit
                else: 
                    self.inhive = False # Bee is now outside the hive
                    self.pos = hive_exit_pos # Update bee's position to the external hive entrance
                    self.state = 'SEEKING_FLOWER' # Change state to look for flowers
                    self.current_move_pos = None # Clear previous target
                    moved_during_current_timestep = True
                    print(f"Bee {self.ID} has exited the hive at {self.pos}, destination: flower.")
            else: # Not yet at internal exit cell, continue moving
                moved_during_current_timestep = self.moveBee(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupiedPos, is_in_hive=True)
        elif self.state == 'SEEKING_FLOWER': 
            moved_during_current_timestep = True # Decision process is an "action"
            self.current_move_object = self.seekFlower(flowers_list, current_timestep) # Find a suitable flower
            if self.current_move_object: # If a flower is found
                self.current_move_pos = self.current_move_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
                print(f"Bee {self.ID} (on property) decided on a flower {self.current_move_object.ID} at {self.current_move_pos}.")
            else: 
                self.state = 'IDLE_ON_PROPERTY' # Bee becomes idle on the property it didn't find a flower. 
                self.current_move_pos = None
                print(f"Bee {self.ID} (on property), now idle.")
        elif self.state == 'MOVING_TO_FLOWER': # Bee is moving towards a targeted flower
            if self.current_move_object is None or not self.current_move_object.is_available_for_bees(): # If target flower becomes unavailable
                if self.current_move_object: # If it had a target that's now gone/empty
                    self.recently_emptied_flowers[self.current_move_object.ID] = current_timestep # Remember this flower to avoid it for a while
                self.state = 'SEEKING_FLOWER' 
                self.current_move_pos = None
                self.current_move_object = None
                moved_during_current_timestep = True # Re-evaluating is an action
            elif self.pos == self.current_move_pos: # If bee arrived at the flower
                self.state = 'COLLECTING_NECTAR'
                moved_during_current_timestep = True
                print(f"Bee {self.ID} arrived at flower {self.current_move_object.ID}.")
            else: 
                moved_during_current_timestep = self.moveBee(property_map_data, property_config['max_x'], property_config['max_y'], occupiedPos, is_in_hive=False)
        elif self.state == 'COLLECTING_NECTAR':
            moved_during_current_timestep = True # Collecting costs a timestep
            if self.current_move_object and self.current_move_object.is_available_for_bees() and self.nectarCarried < self.max_nectarCarry:
                amount_to_take = self.max_nectarCarry - self.nectarCarried 
                taken = self.current_move_object.take_nectar(amount_to_take) # Take nectar from flower
                self.nectarCarried += taken
            if self.nectarCarried >= self.max_nectarCarry or not self.current_move_object or (self.current_move_object and not self.current_move_object.is_available_for_bees()):
                if self.current_move_object and not self.current_move_object.is_available_for_bees(): 
                    self.recently_emptied_flowers[self.current_move_object.ID] = current_timestep # Remember if flower was emptied
                self.current_move_pos = self.hive_entrance_pos # Set target to hive entrance
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_move_object = None # No longer targeting the flower
                print(f"Bee {self.ID} finished collecting, returning to hive. Carried: {self.nectarCarried}.")
        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE': # Bee is returning to the hive entrance on property
            if self.pos == self.current_move_pos: # If bee arrived at the external hive entrance
                internal_entry_pos = hive_layout_config['hive_entry_cell_inside'] # Target the fixed internal entry point
                hive_entry_occupied = False # Check if another bee is blocking the internal entry spot
                for other_bee_info in other_bees_details_list: 
                    if other_bee_info['inhive'] and other_bee_info['pos'] == internal_entry_pos:
                        hive_entry_occupied = True
                        break
                if hive_entry_occupied: # If internal entry is blocked
                    moved_during_current_timestep = self.moveRandomly(property_map_data, property_config['max_x'], property_config['max_y'], occupiedPos) # Jiggle outside entrance
                else: # Internal entry is clear
                    self.inhive = True # Bee is now inside the hive
                    self.pos = internal_entry_pos # Update bee's position to the internal hive entry
                    self.state = 'IDLE_IN_HIVE' # Bee becomes idle inside the hive
                    self.current_move_pos = None
                    moved_during_current_timestep = True
                    print(f"Bee {self.ID} entered hive at {self.pos}.")
            else: # Not yet at hive entrance, continue moving
                moved_during_current_timestep = self.moveBee(property_map_data, property_config['max_x'], property_config['max_y'], occupiedPos, is_in_hive=False)
        elif self.state == 'MOVING_TO_COMB_BUILD_SITE': # Bee is in hive, moving to a site to build comb
            if self.pos == self.current_move_pos: # If arrived at build site
                self.state = 'BUILDING_COMB'
                moved_during_current_timestep = True
            else: # Not yet at comb-building site, continue moving
                moved_during_current_timestep = self.moveBee(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupiedPos, is_in_hive=True)
        elif self.state == 'BUILDING_COMB': # Bee is at site, building a new comb unit
            moved_during_current_timestep = True 
            x, y = self.pos
            # Check if cell is valid for building
            if self.nectarCarried >= 1 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x, y, 0] == 0: # 0=empty, 1=built comb
                hive_data[x, y, 0] = 1 # 1 = comb built
                hive_data[x, y, 1] = 0 
                self.nectarCarried -= 1 # Cost 1 nectar to build comb
                print(f"Bee {self.ID} built comb at {self.pos}. Nectar left: {self.nectarCarried}")
            self.state = 'IDLE_IN_HIVE' # Return to idle to decide next action
            self.current_move_pos = None
        elif self.state == 'MOVING_TO_COMB_DEPOSIT_SITE': # Bee is in hive, moving to a comb cell to deposit nectar
            if self.pos == self.current_move_pos: # If arrived at deposit site
                self.state = 'DEPOSITING_NECTAR'
                moved_during_current_timestep = True
            else: # Not yet at deposit site, continue moving
                moved_during_current_timestep = self.moveBee(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupiedPos, is_in_hive=True)
        elif self.state == 'DEPOSITING_NECTAR': # Bee is at comb, depositing nectar
            moved_during_current_timestep = True # Depositing is an action
            x,y = self.pos
            # Check if cell is valid for depositing
            if self.nectarCarried > 0 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x,y,0] == 1: # Cell must be built comb
                can_deposit = hive_layout_config['max_nectar_per_cell'] - hive_data[x,y,1] # Layer 1 is nectar amount
                deposited_amount = min(self.nectarCarried, can_deposit) # Deposit what it can
                if deposited_amount > 0:
                    hive_data[x,y,1] += deposited_amount
                    self.nectarCarried -= deposited_amount
                    print(f"Bee {self.ID} deposited {deposited_amount} nectar at {self.pos}. Cell now has {hive_data[x,y,1]}. Nectar left: {self.nectarCarried}")
            self.state = 'IDLE_IN_HIVE' 
            self.current_move_pos = None
        elif self.state == 'IDLE_ON_PROPERTY': 
            moved_during_current_timestep = True 
            if self.age % 10 == 0 : # if idel on property for too long, decide to return to hive (as natrual bees do)
                self.current_move_pos = self.hive_entrance_pos
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                print(f"Bee {self.ID} is idle on property, now returning to hive.")
            else: # else move randomly
                moved_during_current_timestep = self.moveRandomly(property_map_data, property_config['max_x'], property_config['max_y'], occupiedPos)
        if moved_during_current_timestep:
            self.clogCount = 0 # if bee has done somtheing during current timestep, their inactivity counter returns to 0
        else: # Bee did not move or act
            self.clogCount += 1 # Increment stuck counter
            print(f"Bee {self.ID} did not move or decide. Stuck: {self.clogCount}. State: {self.state}, pos: {self.pos}, Target: {self.current_move_pos}")
        if self.clogCount > self.max_clogCount: # If bee is stuck for too long
            print(f"Bee {self.ID} STUCK in state {self.state} at {self.pos} for {self.clogCount} (>{self.max_clogCount}) steps. Target: {self.current_move_pos}. Resetting task.")
            if self.current_move_object and isinstance(self.current_move_object, Flower):
                   self.recently_emptied_flowers[self.current_move_object.ID] = current_timestep 
            if self.inhive:# Reset state based on bee's current environment
                self.state = 'IDLE_IN_HIVE' 
            else: 
                self.state = 'SEEKING_FLOWER' 
            self.current_move_pos = None # Clear current target
            self.current_move_object = None
            self.clogCount = 0 # Reset stuck counter

    def moveBee(self, mapData, maxX, maxY, occupied_cells, is_in_hive=False): # Private method for targeted movement
        """
        Moves the bee one step towards its current_move_pos, with collision avoidance.
        mapData:   terrain data (None if in hive)
        maxX, maxY:   boundaries of the current environment
        occupied_cells:   set of (x,y) tuples of cells occupied by other bees
        is_in_hive:   boolean, True if bee is moving within the hive
        Returns True if moved, False otherwise.
        """
        if self.current_move_pos is None or self.pos == self.current_move_pos: # If no target or already at target
            return True 
        originalPos = self.pos 
        dx = self.current_move_pos[0] - self.pos[0] # Difference in x axis
        dy = self.current_move_pos[1] - self.pos[1] # Difference in y aixs
        move_Xcomponenet = np.sign(dx) if dx != 0 else 0
        move_Ycomponent = np.sign(dy) if dy != 0 else 0
        preferred_next_steps = [] # List of preferred moves, ordered by preference
        if move_Xcomponenet != 0 or move_Ycomponent != 0: # Prefer diagonal move if applicable
            preferred_next_steps.append((self.pos[0] + move_Xcomponenet, self.pos[1] + move_Ycomponent))
        if move_Xcomponenet != 0 and move_Ycomponent != 0: # If diagonal was an option
            if move_Xcomponenet != 0: # Pure X move
                preferred_next_steps.append((self.pos[0] + move_Xcomponenet, self.pos[1]))
            if move_Ycomponent != 0: # Pure Y move
                preferred_next_steps.append((self.pos[0], self.pos[1] + move_Ycomponent))
        elif move_Xcomponenet !=0: # Only X movement needed, this is already in preferred_next_steps[0] if it exists
             pass
        elif move_Ycomponent !=0: # Only Y movement needed
             pass
        unique_preferred_steps = [] # Ensure no duplicate steps 
        seen_steps_set = set()
        for step_tuple in preferred_next_steps:
            if step_tuple not in seen_steps_set:
                unique_preferred_steps.append(step_tuple)
                seen_steps_set.add(step_tuple)
        ## Preferred first move
        for newX_float, newY_float in unique_preferred_steps:
            newX, newY = int(newX_float), int(newY_float) # Convert to int for grid indexing
            # Check boundaries
            if not (0 <= newX < maxX and 0 <= newY < maxY): continue
            # Check terrain obstacles (only if outside hive and mapData is provided)
            if not is_in_hive and mapData is not None and mapData[newX, newY] != 0: continue # 0 is passable terrain
            if (newX, newY) in occupied_cells: continue # Check for collision with other bees
            print(f"Bee {self.ID} moving from {self.pos} to {(newX, newY)} towards {self.current_move_pos}")
            self.pos = (newX, newY) # Valid move found
            return True 
        ## Jiggle method - whenever first preeferred move is not valid during next timestep, try to jiggle to a neighbouring cell. 
        jiggleMoves = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)] # Moore nighbouring cells
        random.shuffle(jiggleMoves) 
        for move_dx, move_dy in jiggleMoves:
            jiggle_x, jiggle_y = self.pos[0] + move_dx, self.pos[1] + move_dy    
            if (jiggle_x, jiggle_y) == originalPos : # Don't jiggle to the same spot
                continue
            if not (0 <= jiggle_x < maxX and 0 <= jiggle_y < maxY): continue # check boundaries for jiggle move
            if not is_in_hive and mapData is not None and mapData[jiggle_x, jiggle_y] != 0: continue # check for obstacles
            if (jiggle_x, jiggle_y) in occupied_cells: continue # check for collision with other bees   
            # print(f"Bee {self.ID} jiggled from {original_pos} to {(jiggle_x, jiggle_y)} (target was {self.current_move_pos})")
            self.pos = (jiggle_x, jiggle_y) # Valid jiggle move found
            return True 
        return False 

    def moveRandomly(self, mapData, maxX, maxY, occupied_cells): # Private method for random movement
        """
        Moves the bee one step randomly to an adjacent valid cell (von Neumann neighborhood). Used when bee is stuck or needs to make a idle move.
        """
        valid_random_moves = [(0,1), (1,0), (0,-1), (-1,0)] 
        random.shuffle(valid_random_moves) # Try in random order
        for move_dx, move_dy in valid_random_moves:
            newX = self.pos[0] + move_dx
            newY = self.pos[1] + move_dy
            if 0 <= newX < maxX and 0 <= newY < maxY: # Check boundaries
                is_passable_terrain = mapData is None or mapData[newX, newY] == 0
                is_occupied_by_other = (newX, newY) in occupied_cells # Check collision
                if is_passable_terrain and not is_occupied_by_other:
                    print(f"Bee {self.ID} making a random move from {self.pos} to {(newX, newY)}")
                    self.pos = (newX, newY)
                    return True 
        return False 
    
    def seekFlower(self, flowerList, currentTimeStep): # Private method to find a suitable flower
        """
        Finds the closest available flower that the bee hasn't recently emptied. To introduce variety to bee's movements. 
        flowers_list:   list of all Flower objects
        currentTimeStep:   current simulation time, for checking recently_emptied_flowers
        Returns a Flower object or None if no suitable flower is found.
        """
        toRemove = [fid for fid, ts in self.recently_emptied_flowers.items() if currentTimeStep - ts > self.empty_flower_avoiding_duration]  # Clear flowers from recently_emptied_flowers list if their empty_flower_avoiding_duration has passed
        for fid in toRemove:
            if fid in self.recently_emptied_flowers: 
                del self.recently_emptied_flowers[fid]
        potentialFlowers = [] # List of flowers that are available and not have been recently depleted
        for flower in flowerList:
            if flower.is_available_for_bees() and flower.ID not in self.recently_emptied_flowers:
                potentialFlowers.append(flower)
        if not potentialFlowers: # If no ideal candidates (all available flowers were recently emptied or none available)
            fallbackFlowers = [f for f in flowerList if f.is_available_for_bees()] # Consider any available flower
            if not fallbackFlowers:
                return None # No flowers available at all
            potentialFlowers = fallbackFlowers # Use fallback list
        closest_flower = None
        min_dist_sq = float('inf') # Using squared distance to avoid sqrt calculation
        random.shuffle(potentialFlowers) # Shuffle to vary choice among equally distant flowers over time
        for flower in potentialFlowers:
            dist_sq = (self.pos[0] - flower.get_pos()[0])**2 + \
                      (self.pos[1] - flower.get_pos()[1])**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_flower = flower
        return closest_flower
## (3) FRAMES
    def buildFrames(self, hiveData, hiveLayout): # 
        """
        Finds a random empty cell within the designated comb-building stripe to initialise a comb. 
        hiveData:   numpy array of the hive state
        """
        combWidth = hiveLayout.get('comb_stripe_width', 3) # width of the stripe of comb
        stripe_centerX = hiveLayout['max_x'] // 2
        startX = max(0, stripe_centerX - combWidth // 2) # start x of stripe
        endX = min(hiveLayout['max_x'], startX + combWidth) # End x of stripe
        possible_build_cells = []
        for y in range(hiveLayout['max_y']): 
            for x in range(startX, endX):
                if 0 <= x < hiveLayout['max_x'] and 0 <= y < hiveLayout['max_y']: # Bounds check
                    if hiveData[x, y, 0] == 0: # Layer 0 is comb status, 0 means no comb built yet
                        possible_build_cells.append((x, y))
        if possible_build_cells:
            return random.choice(possible_build_cells) # Return a random valid build cell
        return None 

    def depositNectar(self, hiveData, hiveLayout): 
        """
        Finds a built comb cell within the stripe that has space for nectar.
        Prefers cells with the least amount of nectar.
        hiveData:   numpy array of the hive state
        """
        combWidth = hiveLayout.get('comb_stripe_width', 3)
        stripe_center_x = hiveLayout['max_x'] // 2
        startX = max(0, stripe_center_x - combWidth // 2)
        endX = min(hiveLayout['max_x'], startX + combWidth)
        max_nectar_per_cell = hiveLayout.get('max_nectar_per_cell', 4)
        possibleCells = [] # Stores x, y pos of comb cells available to nectar deposits
        for y in range(hiveLayout['max_y']):
            for x in range(startX, endX): # Only search within the comb stripe
                if 0 <= x < hiveLayout['max_x'] and 0 <= y < hiveLayout['max_y']: # Bounds check
                    # Cell must be built (layer 0 is 1) and have less than max nectar (layer 1)
                    if hiveData[x, y, 0] == 1 and hiveData[x, y, 1] < max_nectar_per_cell:
                        possibleCells.append(((x, y), hiveData[x, y, 1]))
        if not possibleCells: # No suitable deposit cells found
            return None 
        possibleCells.sort(key=lambda item: item[1]) # sort by nectar level
        if possibleCells: 
            min_nectar_level = possibleCells[0][1] # Get the lowest nectar level among available cells
            least_filled_cells_pos = [cell[0] for cell in possibleCells if cell[1] == min_nectar_level] # Filter for all cells that have this minimum nectar level
            if least_filled_cells_pos:
                return random.choice(least_filled_cells_pos) # Choose randomly among the least filled combs
        return None

    def build(self, hive_data, hive_layout_config): 
        """Checks if there's any available units in the stripe to build comb or deposit nectar."""
        if self.buildFrames(hive_data, hive_layout_config) is not None:
            return True
        if self.depositNectar(hive_data, hive_layout_config) is not None:
            return True
        return False

    def get_pos(self):
        """Returns the current (x,y) position of the bee."""
        return self.pos

    def get_inhive(self):
        """Returns True if the bee is currently inside the hive, False otherwise."""
        return self.inhive