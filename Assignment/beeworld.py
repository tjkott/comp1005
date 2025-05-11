# Student Name: <put your name here>
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information:
#     2024-04-07 : Initial Version released
#     (Further versioning from the more complex script is omitted to match the simple example's style)
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
        rate:   amount of nectar to regenerate per timestep
        
        """
        if self.state == 'DEAD': 
            if self.regeneration_cooldown > 0:
                self.regeneration_cooldown -= 1 # Countdown the cooldown timer
            else: 
                self.state = 'ALIVE' # Flower gets "ALIVE" state once cooldown is finished. 
                self.is_refilling = True # Enters a state of actively refilling its nectar from 0. 
                print(f"Flower {self.ID} ({self.name}) is ALIVE and stated regeneration.")
        
        if self.state == 'ALIVE' and self.is_refilling: # Only regenregenerates rates if it just became ALIVE or is explicitly refilling
            if self.currentNectar < self.nectarCapacity:
                self.currentNectar = min(self.nectarCapacity, self.currentNectar + rate) 
                if self.currentNectar == self.nectarCapacity:
                    self.is_refilling = False # Stop the special refilling state once full
                    print(f"Flower {self.ID} ({self.name}) has regenerated to maximum.")

    def is_available_for_bees(self):
        """Returns True if the flower is alive and has nectar (not necessarily full). Used by bees to find targets."""
        return self.state == 'ALIVE' and self.currentNectar > 0

class Bee(): # Providing state and behaviour for worker bee in the simulation
    def __init__(self, ID, initial_pos, hive_entrance_property_pos, max_nectar_carry=1, avoid_empty_duration=20, max_stuck_time=5):
        """
        Initialise Bee object
        ID: identifier for the bee
        initial_pos: (x,y) starting position of the bee (usually inside hive)
        hive_entrance_property_pos: (x,y) location of the hive entrance on the main property map
        max_nectar_carry: maximum nectar units the bee can carry
        avoid_empty_duration: timesteps a bee avoids a flower it just emptied
        max_stuck_time: timesteps a bee can be stuck before resetting its task
        """
        self.ID = ID
        self.pos = initial_pos # Current (x,y) position of the bee
        self.hive_entrance_property_pos = hive_entrance_property_pos # Fixed external location of the hive
        self.age = 0 # Age of the bee in simulation timesteps
        self.inhive = True # Boolean: True if bee is inside the hive, False if on property
        self.state = 'IDLE_IN_HIVE' # Current behavioral state of the bee
        self.nectar_carried = 0 # Amount of nectar the bee is currently carrying
        self.max_nectar_carry = max_nectar_carry # Maximum nectar capacity for this bee
        self.current_target_pos = None # Target (x,y) coordinates for movement
        self.current_target_object = None # Reference to a target object (e.g., a Flower instance)
        self.path = [] # Path to target (not deeply used by current simple movement)
        self.recently_emptied_flowers = {} # Dict to remember flowers recently emptied by this bee {flower_ID: timestep}
        self.avoid_empty_duration = avoid_empty_duration # How long to avoid an emptied flower
        self.stuck_count = 0 # Counter for consecutive steps without moving or acting
        self.max_stuck_time = max_stuck_time # Threshold for being stuck

    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config, current_timestep, other_bees_details_list): # Main update logic for the bee each timestep
        """
        Update Bee object on each timestep based on its current state and environment.
        property_map_data:   numpy array of the main property terrain
        flowers_list:   list of Flower objects
        hive_data:   numpy array representing the hive's internal state (combs, nectar)
        hive_layout_config:   dictionary with hive dimensions and fixed points
        property_config:   dictionary with property dimensions and hive location
        current_timestep:   the current simulation time
        other_bees_details_list:   list of dicts with info about other bees for collision avoidance
        ## (c) Bee State Machine and Action Logic
        """
        self.age += 1 # Increment bee's age
        moved_or_acted_this_step = False # Flag to track if bee successfully moved or performed an action this step
        
        # Determine occupied cells in the bee's current environment (either hive or property) for collision avoidance
        occupied_cells_in_current_env = set()
        if self.inhive: # If bee is in the hive
            occupied_cells_in_current_env = {info['pos'] for info in other_bees_details_list if info['inhive']}
        else: # If bee is on the property
            occupied_cells_in_current_env = {info['pos'] for info in other_bees_details_list if not info['inhive']}

        # --- Bee State Machine ---
        if self.state == 'IDLE_IN_HIVE': # Bee is in the hive and needs to decide its next action
            self.stuck_count = 0 # Reset stuck count as it's making a decision
            moved_or_acted_this_step = True # Making a decision counts as an action
            if self.nectar_carried >= 1 and self._can_build_or_deposit(hive_data, hive_layout_config): # If bee has nectar and can build or deposit
                comb_build_target = self._find_comb_to_build(hive_data, hive_layout_config) # Try to find a place to build comb
                if comb_build_target: # If a build site is found
                    self.current_target_pos = comb_build_target
                    self.state = 'MOVING_TO_COMB_BUILD_SITE'
                    # print(f"Bee {self.ID} (in hive) decided to build comb at {self.current_target_pos}.")
                else: # No place to build, try to find a place to deposit nectar
                    comb_deposit_target = self._find_comb_to_deposit(hive_data, hive_layout_config)
                    if comb_deposit_target: # If a deposit site is found
                        self.current_target_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE'
                        # print(f"Bee {self.ID} (in hive) decided to deposit nectar at {self.current_target_pos}.")
                    elif self.nectar_carried < self.max_nectar_carry: # Has nectar, but can't build/deposit, not full, so go get more
                        self.current_target_pos = hive_layout_config['hive_exit_cell_inside'] # Target internal hive exit
                        self.state = 'MOVING_TO_HIVE_EXIT'
            elif self.nectar_carried < self.max_nectar_carry: # If bee doesn't have enough nectar to build/deposit, or has no nectar, and is not full
                self.current_target_pos = hive_layout_config['hive_exit_cell_inside'] # Target internal hive exit to go collect more
                self.state = 'MOVING_TO_HIVE_EXIT'
                # print(f"Bee {self.ID} (in hive) needs more nectar, heading to hive exit.")
        
        elif self.state == 'MOVING_TO_HIVE_EXIT': # Bee is moving towards the internal exit point of the hive
            if self.pos == self.current_target_pos: # If bee has reached the internal exit cell
                external_exit_pos = self.hive_entrance_property_pos # The actual hive entrance on the property map
                is_external_spot_occupied = False # Check if another bee is blocking the external entrance spot
                for other_bee_info in other_bees_details_list:
                    if not other_bee_info['inhive'] and other_bee_info['pos'] == external_exit_pos:
                        is_external_spot_occupied = True
                        break
                if is_external_spot_occupied: # If external spot is blocked
                    moved_or_acted_this_step = self._move_randomly(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env) # Jiggle inside near exit
                else: # External spot is clear, bee can exit
                    self.inhive = False # Bee is now outside the hive
                    self.pos = external_exit_pos # Update bee's position to the external hive entrance
                    self.state = 'SEEKING_FLOWER' # Change state to look for flowers
                    self.current_target_pos = None # Clear previous target
                    moved_or_acted_this_step = True
                    # print(f"Bee {self.ID} exited hive to {self.pos}, now seeking flower.")
            else: # Not yet at internal exit cell, continue moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'SEEKING_FLOWER': # Bee is on the property, looking for a flower
            moved_or_acted_this_step = True # Decision process is an "action"
            self.current_target_object = self._find_closest_flower_with_nectar(flowers_list, current_timestep) # Find a suitable flower
            if self.current_target_object: # If a flower is found
                self.current_target_pos = self.current_target_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
                # print(f"Bee {self.ID} (on property) found flower {self.current_target_object.ID} at {self.current_target_pos}.")
            else: # No suitable flower found
                self.state = 'IDLE_ON_PROPERTY' # Bee becomes idle on the property
                self.current_target_pos = None
                # print(f"Bee {self.ID} (on property) found no suitable flowers, now idle.")

        elif self.state == 'MOVING_TO_FLOWER': # Bee is moving towards a targeted flower
            if self.current_target_object is None or not self.current_target_object.is_available_for_bees(): # If target flower becomes unavailable
                if self.current_target_object: # If it had a target that's now gone/empty
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep # Remember this flower to avoid it for a while
                self.state = 'SEEKING_FLOWER' # Go back to seeking a new flower
                self.current_target_pos = None
                self.current_target_object = None
                moved_or_acted_this_step = True # Re-evaluating is an action
            elif self.pos == self.current_target_pos: # If bee arrived at the flower
                self.state = 'COLLECTING_NECTAR'
                moved_or_acted_this_step = True
                # print(f"Bee {self.ID} arrived at flower {self.current_target_object.ID}.")
            else: # Not yet at flower, continue moving
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        elif self.state == 'COLLECTING_NECTAR': # Bee is at a flower, collecting nectar
            moved_or_acted_this_step = True # Collecting is an action
            if self.current_target_object and self.current_target_object.is_available_for_bees() and self.nectar_carried < self.max_nectar_carry:
                amount_to_take = self.max_nectar_carry - self.nectar_carried # Try to take enough to fill up
                taken = self.current_target_object.take_nectar(amount_to_take) # Take nectar from flower
                self.nectar_carried += taken
                # if taken > 0: print(f"Bee {self.ID} collected {taken} nectar from flower {self.current_target_object.ID}. Total carried: {self.nectar_carried}.")
            
            # Check if done collecting (bee is full, or flower is empty/gone)
            if self.nectar_carried >= self.max_nectar_carry or \
               not self.current_target_object or \
               (self.current_target_object and not self.current_target_object.is_available_for_bees()):
                if self.current_target_object and not self.current_target_object.is_available_for_bees(): 
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep # Remember if flower was emptied
                self.current_target_pos = self.hive_entrance_property_pos # Set target to hive entrance
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_target_object = None # No longer targeting the flower
                # print(f"Bee {self.ID} finished collecting, returning to hive. Carried: {self.nectar_carried}.")

        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE': # Bee is returning to the hive entrance on property
            if self.pos == self.current_target_pos: # If bee arrived at the external hive entrance
                internal_entry_pos = hive_layout_config['hive_entry_cell_inside'] # Target the fixed internal entry point
                is_internal_entry_occupied = False # Check if another bee is blocking the internal entry spot
                for other_bee_info in other_bees_details_list: 
                    if other_bee_info['inhive'] and other_bee_info['pos'] == internal_entry_pos:
                        is_internal_entry_occupied = True
                        break
                if is_internal_entry_occupied: # If internal entry is blocked
                    moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env) # Jiggle outside entrance
                else: # Internal entry is clear
                    self.inhive = True # Bee is now inside the hive
                    self.pos = internal_entry_pos # Update bee's position to the internal hive entry
                    self.state = 'IDLE_IN_HIVE' # Bee becomes idle inside the hive
                    self.current_target_pos = None
                    moved_or_acted_this_step = True
                    # print(f"Bee {self.ID} entered hive at {self.pos}.")
            else: # Not yet at hive entrance, continue moving
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        elif self.state == 'MOVING_TO_COMB_BUILD_SITE': # Bee is in hive, moving to a site to build comb
            if self.pos == self.current_target_pos: # If arrived at build site
                self.state = 'BUILDING_COMB'
                moved_or_acted_this_step = True
            else: # Not yet at build site, continue moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'BUILDING_COMB': # Bee is at site, building a new comb cell
            moved_or_acted_this_step = True # Building is an action
            x, y = self.pos
            # Check if cell is valid for building
            if self.nectar_carried >= 1 and \
               0 <= x < hive_layout_config['max_x'] and \
               0 <= y < hive_layout_config['max_y'] and \
               hive_data[x, y, 0] == 0: # Layer 0 is comb status (0=empty, 1=built)
                hive_data[x, y, 0] = 1 # Mark comb as built
                hive_data[x, y, 1] = 0 # Initialize nectar in new comb to 0
                self.nectar_carried -= 1 # Cost 1 nectar to build comb
                print(f"Bee {self.ID} built comb at {self.pos}. Nectar left: {self.nectar_carried}")
            self.state = 'IDLE_IN_HIVE' # Return to idle to decide next action
            self.current_target_pos = None

        elif self.state == 'MOVING_TO_COMB_DEPOSIT_SITE': # Bee is in hive, moving to a comb cell to deposit nectar
            if self.pos == self.current_target_pos: # If arrived at deposit site
                self.state = 'DEPOSITING_NECTAR'
                moved_or_acted_this_step = True
            else: # Not yet at deposit site, continue moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'DEPOSITING_NECTAR': # Bee is at comb, depositing nectar
            moved_or_acted_this_step = True # Depositing is an action
            x,y = self.pos
            # Check if cell is valid for depositing
            if self.nectar_carried > 0 and \
               0 <= x < hive_layout_config['max_x'] and \
               0 <= y < hive_layout_config['max_y'] and \
               hive_data[x,y,0] == 1: # Cell must be built comb
                can_deposit = hive_layout_config['max_nectar_per_cell'] - hive_data[x,y,1] # Layer 1 is nectar amount
                deposited_amount = min(self.nectar_carried, can_deposit) # Deposit what it can
                if deposited_amount > 0:
                    hive_data[x,y,1] += deposited_amount
                    self.nectar_carried -= deposited_amount
                    print(f"Bee {self.ID} deposited {deposited_amount} nectar at {self.pos}. Cell now has {hive_data[x,y,1]}. Nectar left: {self.nectar_carried}")
            self.state = 'IDLE_IN_HIVE' # Return to idle
            self.current_target_pos = None

        elif self.state == 'IDLE_ON_PROPERTY': # Bee is outside, no flowers found, wandering or returning
            moved_or_acted_this_step = True # Deciding or random move is an action
            if self.age % 10 == 0 : # Periodically, decide to return to hive if idle for too long
                self.current_target_pos = self.hive_entrance_property_pos
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                # print(f"Bee {self.ID} was idle on property, now returning to hive.")
            else: # Otherwise, move randomly
                moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env)
        
        ## (d) Stuck Logic - Check if bee failed to move or act and reset if necessary
        if moved_or_acted_this_step:
            self.stuck_count = 0 # Reset stuck counter if bee moved or acted
        else: # Bee did not move or act
            self.stuck_count += 1 # Increment stuck counter
            # print(f"Bee {self.ID} did not move/act. Stuck: {self.stuck_count}. State: {self.state}, Pos: {self.pos}, Target: {self.current_target_pos}")
        
        if self.stuck_count > self.max_stuck_time: # If bee is stuck for too long
            print(f"Bee {self.ID} STUCK in state {self.state} at {self.pos} for {self.stuck_count} (>{self.max_stuck_time}) steps. Target: {self.current_target_pos}. Resetting task.")
            if self.current_target_object and isinstance(self.current_target_object, Flower): # If was targeting a flower
                   self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep # Mark it as recently emptied
            
            # Reset state based on location
            if self.inhive:
                self.state = 'IDLE_IN_HIVE' 
            else: 
                self.state = 'SEEKING_FLOWER' 
            
            self.current_target_pos = None # Clear current target
            self.current_target_object = None
            self.stuck_count = 0 # Reset stuck counter


    def _move_towards_target(self, map_data, maxX, maxY, occupied_cells, is_in_hive=False): # Private method for targeted movement
        """
        Moves the bee one step towards its current_target_pos, with collision avoidance.
        map_data:   terrain data (None if in hive)
        maxX, maxY:   boundaries of the current environment
        occupied_cells:   set of (x,y) tuples of cells occupied by other bees
        is_in_hive:   boolean, True if bee is moving within the hive
        Returns True if moved, False otherwise.
        ## (e) Bee Movement and Collision Avoidance Logic
        """
        if self.current_target_pos is None or self.pos == self.current_target_pos: # If no target or already at target
            return True 

        original_pos = self.pos # Remember current position
        dx = self.current_target_pos[0] - self.pos[0] # Difference in x
        dy = self.current_target_pos[1] - self.pos[1] # Difference in y

        # Determine primary and secondary move components (diagonal, then axial)
        move_x_component = np.sign(dx) if dx != 0 else 0
        move_y_component = np.sign(dy) if dy != 0 else 0
        
        preferred_next_steps = [] # List of preferred moves, ordered by preference
        if move_x_component != 0 or move_y_component != 0: # Prefer diagonal move if applicable
            preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1] + move_y_component))
        # If diagonal was preferred (or if only one axis movement is needed), also consider axial moves
        if move_x_component != 0 and move_y_component != 0: # If diagonal was an option
            if move_x_component != 0: # Pure X move
                preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1]))
            if move_y_component != 0: # Pure Y move
                preferred_next_steps.append((self.pos[0], self.pos[1] + move_y_component))
        elif move_x_component !=0: # Only X movement needed, this is already in preferred_next_steps[0] if it exists
             pass
        elif move_y_component !=0: # Only Y movement needed
             pass


        unique_preferred_steps = [] # Ensure no duplicate steps if axial was the only option
        seen_steps_set = set()
        for step_tuple in preferred_next_steps:
            if step_tuple not in seen_steps_set:
                unique_preferred_steps.append(step_tuple)
                seen_steps_set.add(step_tuple)

        # Try preferred moves first
        for newX_float, newY_float in unique_preferred_steps:
            newX, newY = int(newX_float), int(newY_float) # Convert to int for grid indexing
            # Check boundaries
            if not (0 <= newX < maxX and 0 <= newY < maxY): continue
            # Check terrain obstacles (only if outside hive and map_data is provided)
            if not is_in_hive and map_data is not None and map_data[newX, newY] != 0: continue # 0 is passable terrain
            # Check for collision with other bees
            if (newX, newY) in occupied_cells: continue 
            
            # print(f"Bee {self.ID} moving from {self.pos} to {(newX, newY)} towards {self.current_target_pos}")
            self.pos = (newX, newY) # Valid move found
            return True 

        ## Jiggle Logic - If preferred moves are blocked, try to jiggle to a nearby free cell
        jiggle_moves = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)] # All Moore neighborhood cells
        random.shuffle(jiggle_moves) # Try jiggle moves in random order
        for move_dx, move_dy in jiggle_moves:
            jiggle_x, jiggle_y = self.pos[0] + move_dx, self.pos[1] + move_dy
            
            if (jiggle_x, jiggle_y) == original_pos : # Don't jiggle to the same spot
                continue

            # Check boundaries for jiggle move
            if not (0 <= jiggle_x < maxX and 0 <= jiggle_y < maxY): continue
            # Check terrain for jiggle move
            if not is_in_hive and map_data is not None and map_data[jiggle_x, jiggle_y] != 0: continue
            # Check collision for jiggle move
            if (jiggle_x, jiggle_y) in occupied_cells: continue
            
            # print(f"Bee {self.ID} jiggled from {original_pos} to {(jiggle_x, jiggle_y)} (target was {self.current_target_pos})")
            self.pos = (jiggle_x, jiggle_y) # Valid jiggle move found
            return True 
        
        return False # No move was possible

    def _move_randomly(self, map_data, maxX, maxY, occupied_cells): # Private method for random movement
        """
        Moves the bee one step randomly to an adjacent valid cell (von Neumann neighborhood).
        Used when bee is stuck or needs to make a non-targeted move.
        Returns True if moved, False otherwise.
        """
        valid_moves_tuples = [(0,1), (1,0), (0,-1), (-1,0)] # N, E, S, W moves
        random.shuffle(valid_moves_tuples) # Try in random order
        for move_dx, move_dy in valid_moves_tuples:
            newX = self.pos[0] + move_dx
            newY = self.pos[1] + move_dy
            if 0 <= newX < maxX and 0 <= newY < maxY: # Check boundaries
                # Check terrain (passable if map_data is None (e.g. in hive) or cell value is 0)
                is_passable_terrain = map_data is None or map_data[newX, newY] == 0
                is_occupied_by_other = (newX, newY) in occupied_cells # Check collision
                if is_passable_terrain and not is_occupied_by_other:
                    # print(f"Bee {self.ID} moving randomly from {self.pos} to {(newX, newY)}")
                    self.pos = (newX, newY)
                    return True 
        return False # No random move was possible
    
    def _find_closest_flower_with_nectar(self, flowers_list, current_timestep): # Private method to find a suitable flower
        """
        Finds the closest available flower that the bee hasn't recently emptied.
        flowers_list:   list of all Flower objects
        current_timestep:   current simulation time, for checking recently_emptied_flowers
        Returns a Flower object or None if no suitable flower is found.
        ## (f) Flower Selection Logic - with avoidance of recently emptied flowers
        """
        # Clear flowers from recently_emptied_flowers list if their avoid_empty_duration has passed
        to_remove = [fid for fid, ts in self.recently_emptied_flowers.items() if current_timestep - ts > self.avoid_empty_duration]
        for fid in to_remove:
            if fid in self.recently_emptied_flowers: # Ensure key exists before deleting
                del self.recently_emptied_flowers[fid]

        candidate_flowers = [] # List of flowers that are available and not recently emptied
        for flower in flowers_list:
            if flower.is_available_for_bees() and flower.ID not in self.recently_emptied_flowers:
                candidate_flowers.append(flower)
        
        if not candidate_flowers: # If no ideal candidates (all available flowers were recently emptied or none available)
            fallback_candidates = [f for f in flowers_list if f.is_available_for_bees()] # Consider any available flower
            if not fallback_candidates:
                return None # No flowers available at all
            candidate_flowers = fallback_candidates # Use fallback list

        closest_flower = None
        min_dist_sq = float('inf') # Using squared distance to avoid sqrt calculation
        random.shuffle(candidate_flowers) # Shuffle to vary choice among equally distant flowers over time
        for flower in candidate_flowers:
            dist_sq = (self.pos[0] - flower.get_pos()[0])**2 + \
                      (self.pos[1] - flower.get_pos()[1])**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_flower = flower
        return closest_flower

    def _find_comb_to_build(self, hive_data, hive_layout_config): # Private method to find a build site
        """
        Finds a random empty cell within the designated comb-building stripe in the hive.
        hive_data:   numpy array of the hive state
        hive_layout_config:   dictionary with hive dimensions and comb stripe info
        Returns an (x,y) tuple for a build site, or None if no site is found.
        ## (g) Hive Comb Building Site Selection in Stripe
        """
        comb_width = hive_layout_config.get('comb_stripe_width', 3) # Width of the central building area
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2) # Start x-coordinate of the stripe
        end_x = min(hive_layout_config['max_x'], start_x + comb_width) # End x-coordinate
        
        possible_build_cells = []
        # Iterate only within the comb stripe for potential build locations
        for y_idx in range(hive_layout_config['max_y']): 
            for x_idx in range(start_x, end_x):
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']: # Bounds check
                    if hive_data[x_idx, y_idx, 0] == 0: # Layer 0 is comb status, 0 means no comb built yet
                        possible_build_cells.append((x_idx, y_idx))
        if possible_build_cells:
            return random.choice(possible_build_cells) # Return a random valid build cell
        return None # No place to build

    def _find_comb_to_deposit(self, hive_data, hive_layout_config): # Private method to find a deposit site
        """
        Finds a built comb cell within the stripe that has space for nectar.
        Prefers cells with the least amount of nectar.
        hive_data:   numpy array of the hive state
        hive_layout_config:   dictionary with hive/comb parameters
        Returns an (x,y) tuple for a deposit site, or None.
        ## (h) Hive Nectar Deposit Site Selection - preferring least filled
        """
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        max_nectar_per_cell = hive_layout_config.get('max_nectar_per_cell', 4)
        
        possible_cells = [] # Stores ((x,y), nectar_level)
        for y_idx in range(hive_layout_config['max_y']):
            for x_idx in range(start_x, end_x): # Only search within the comb stripe
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']: # Bounds check
                    # Cell must be built (layer 0 is 1) and have less than max nectar (layer 1)
                    if hive_data[x_idx, y_idx, 0] == 1 and hive_data[x_idx, y_idx, 1] < max_nectar_per_cell:
                        possible_cells.append(((x_idx, y_idx), hive_data[x_idx, y_idx, 1]))
        
        if not possible_cells: # No suitable deposit cells found
            return None 
        
        possible_cells.sort(key=lambda item: item[1]) # Sort by nectar level, ascending
        
        if possible_cells: 
            min_nectar_level = possible_cells[0][1] # Get the lowest nectar level among available cells
            # Filter for all cells that have this minimum nectar level
            least_filled_cells_coords = [cell[0] for cell in possible_cells if cell[1] == min_nectar_level]
            if least_filled_cells_coords:
                return random.choice(least_filled_cells_coords) # Choose randomly among the least filled cells
        return None

    def _can_build_or_deposit(self, hive_data, hive_layout_config): # Helper to check if build/deposit is possible
        """Checks if there's any available site to build comb or deposit nectar."""
        if self._find_comb_to_build(hive_data, hive_layout_config) is not None:
            return True
        if self._find_comb_to_deposit(hive_data, hive_layout_config) is not None:
            return True
        return False

    def get_pos(self):
        """Returns the current (x,y) position of the bee."""
        return self.pos

    def get_inhive(self):
        """Returns True if the bee is currently inside the hive, False otherwise."""
        return self.inhive

# --- Batch Mode File Loading Functions ---
def load_map(filename, sim_params): # Loads the property map, flower locations, and obstacles from a CSV file FOR BATCH MODE
    world_grid = None # Will hold the numpy array for terrain
    flowers = [] # List to store Flower objects
    property_config = {} # Dictionary for property dimensions and hive location
    prop_w_default, prop_h_default = 20, 15 # Default property width and height if not in file
    hive_x_default, hive_y_default = prop_w_default // 2, prop_h_default // 2 # Default hive entrance on property

    with open(filename, 'r') as f: # Open the map file for reading
        reader = csv.reader(f)
        try:
            ## (Map File Header Parsing)
            header = next(reader) # First line: property_width, property_height, hive_x_on_property, hive_y_on_property
            prop_w = int(header[0].strip()) if len(header) > 0 and header[0].strip().isdigit() else prop_w_default
            prop_h = int(header[1].strip()) if len(header) > 1 and header[1].strip().isdigit() else prop_h_default
            hive_x = int(header[2].strip()) if len(header) > 2 and header[2].strip().isdigit() else hive_x_default
            hive_y = int(header[3].strip()) if len(header) > 3 and header[3].strip().isdigit() else hive_y_default
            
            property_config['max_x'] = prop_w
            property_config['max_y'] = prop_h
            property_config['hive_position_on_property'] = (hive_x, hive_y) 
            
            ## (Map Terrain Grid Parsing)
            temp_terrain_rows = [] # To store rows of terrain data before converting to numpy array
            for r_idx in range(prop_h): # Read 'prop_h' lines for the terrain grid
                line_str_list = next(reader)
                # Handle lines that are too short or too long for the defined property width
                if len(line_str_list) < prop_w:
                    print(f"Warning: Terrain map line {r_idx+1} is shorter than width ({len(line_str_list)} vs {prop_w}). Padding with 0s (passable terrain).")
                    line_str_list.extend(['0'] * (prop_w - len(line_str_list)))
                elif len(line_str_list) > prop_w:
                    print(f"Warning: Terrain map line {r_idx+1} is longer than width ({len(line_str_list)} vs {prop_w}). Truncating.")
                    line_str_list = line_str_list[:prop_w]
                temp_terrain_rows.append([int(val.strip()) for val in line_str_list]) # Convert terrain values to int
            
            terrain_array_from_file = np.array(temp_terrain_rows) 
            if terrain_array_from_file.shape == (prop_h, prop_w): # Check if shape matches expected (rows, cols)
                world_grid = terrain_array_from_file.T # Transpose because file is (row,col) but numpy imshow often expects (x,y)
            else:
                raise ValueError(f"Terrain data shape error. Expected ({prop_h},{prop_w}) for file rows, derived shape {terrain_array_from_file.shape} before transpose.")

            flower_dead_duration_val = sim_params.get('flower_dead_time', 10) # Get from params or use default

            ## (Map Object Parsing - Flowers, Barriers, Obstacles, Water)
            for row_list in reader: # Read remaining lines for objects
                if not row_list or not row_list[0].strip(): continue # Skip empty or malformed lines
                obj_type = row_list[0].strip().upper() # First element is object type
                try:
                    if obj_type == "FLOWER":
                        if len(row_list) < 7: 
                            print(f"Warning: Skipping malformed FLOWER line: {row_list}")
                            continue
                        # FLOWER, ID, X, Y, Name, Color, NectarCapacity
                        f_id, f_x_str, f_y_str, f_name, f_color, f_nectar_str = [s.strip() for s in row_list[1:7]]
                        f_x, f_y, f_nectar_capacity_from_csv = int(f_x_str), int(f_y_str), int(f_nectar_str)
                        flowers.append(Flower(f_id, (f_x, f_y), f_name, f_color, f_nectar_capacity_from_csv, flower_dead_duration_val))
                    elif obj_type == "BARRIER": 
                        if len(row_list) < 6:
                            print(f"Warning: Skipping malformed BARRIER line: {row_list}")
                            continue
                        # BARRIER, X, Y, Width, Height, Value (terrain type for barrier)
                        _, b_x_str, b_y_str, b_w_str, b_h_str, b_val_str = [s.strip() for s in row_list[0:6]] # obj_type is row_list[0]
                        b_x, b_y, b_w, b_h, b_val = int(b_x_str), int(b_y_str), int(b_w_str), int(b_h_str), int(b_val_str)
                        # Ensure barrier is within property bounds before applying to world_grid
                        if 0 <= b_x < prop_w and 0 <= b_y < prop_h and \
                           b_x + b_w <= prop_w and b_y + b_h <= prop_h: 
                            world_grid[b_x : b_x + b_w, b_y : b_y + b_h] = b_val # Apply barrier to the grid
                        else:
                            print(f"Warning: Barrier at {row_list[1:5]} with width/height extends out of bounds. Skipping.")
                    elif obj_type == "OBSTACLE": # Single-cell obstacle
                        if len(row_list) < 5:
                            print(f"Warning: Skipping malformed OBSTACLE line: {row_list}")
                            continue
                        # OBSTACLE, ID, X, Y, Name
                        o_id_str, o_x_str, o_y_str, o_name_str = [s.strip() for s in row_list[1:5]]
                        o_x, o_y = int(o_x_str), int(o_y_str)
                        if 0 <= o_x < prop_w and 0 <= o_y < prop_h:
                            world_grid[o_x, o_y] = 1 # Typically, 1 is a generic obstacle value
                        else:
                            print(f"Warning: Obstacle at ({o_x}, {o_y}) out of bounds. Skipping.")
                    elif obj_type == "WATER": # Single-cell water feature
                        if len(row_list) < 5:
                            print(f"Warning: Skipping malformed WATER line: {row_list}")
                            continue
                        # WATER, ID, X, Y, Name
                        w_id_str, w_x_str, w_y_str, w_name_str = [s.strip() for s in row_list[1:5]]
                        w_x, w_y = int(w_x_str), int(w_y_str)
                        if 0 <= w_x < prop_w and 0 <= w_y < prop_h:
                            world_grid[w_x, w_y] = 2 # Typically, 2 is a water terrain value
                        else:
                            print(f"Warning: Water at ({w_x}, {w_y}) out of bounds. Skipping.")
                except ValueError as e: # Catch errors during conversion of object data (e.g., int())
                    print(f"Warning: Could not parse object line values in '{filename}': {row_list}. Error: {e}. Skipping.")
                except IndexError as e: # Catch errors if a line doesn't have enough elements
                    print(f"Warning: Malformed object line (not enough elements) in '{filename}': {row_list}. Error: {e}. Skipping.")
        except StopIteration: # Reached end of file unexpectedly (e.g., during terrain grid reading)
            if world_grid is None: 
                print(f"Error: CSV file '{filename}' seems to be missing header or complete terrain data.")
                raise ValueError(f"CSV file '{filename}' ended prematurely or is malformed for terrain grid setup.")
        except ValueError as ve: # Catch errors from header parsing (int() conversion)
            print(f"Error converting critical data (header/terrain) in map file '{filename}': {ve}")
            raise
        except Exception as e: # Catch any other general errors during map loading
            print(f"General error loading map file '{filename}': {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            raise
            
    if world_grid is None: # Fallback if world_grid could not be initialized
        print(f"Warning: World grid could not be initialized from {filename}. Using a default empty grid.")
        property_config.setdefault('max_x', prop_w_default)
        property_config.setdefault('max_y', prop_h_default)
        property_config.setdefault('hive_position_on_property', (hive_x_default, hive_y_default))
        world_grid = np.zeros((property_config['max_x'], property_config['max_y']), dtype=int) # Create a basic empty grid

    print(f"Loaded map (batch): Dimensions ({property_config.get('max_x', 'N/A')}x{property_config.get('max_y', 'N/A')}), Hive Entrance @{property_config.get('hive_position_on_property', 'N/A')}, {len(flowers)} flowers.")
    return world_grid, flowers, property_config

def load_parameters(filename): # Loads simulation parameters from a CSV file FOR BATCH MODE
    params = {} # Dictionary to store parameters
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader: # Each row is expected to be: ParameterName, Value
            if len(row) == 2:
                key = row[0].strip()
                value_str = row[1].strip()
                if '#' in value_str: # Allow comments in the value column after a '#'
                    value_str = value_str.split('#', 1)[0].strip()
                
                try: # Attempt to convert value to appropriate type (bool, float, int, or keep as str)
                    if value_str.lower() == 'true': params[key] = True
                    elif value_str.lower() == 'false': params[key] = False
                    elif '.' in value_str and value_str.replace('.', '', 1).replace('-', '', 1).isdigit(): # Check for float
                        params[key] = float(value_str)
                    elif value_str.lstrip('-').isdigit(): # Check for int (handles negative numbers)
                        params[key] = int(value_str)
                    else: # Default to string if no other type matches
                        params[key] = value_str
                except ValueError: # If conversion fails, keep as string
                    params[key] = value_str 
    
    ## (Default Simulation Parameters for Batch Mode - used if not present in paramfile)
    params.setdefault('num_bees', 5)
    params.setdefault('simlength', 100)
    params.setdefault('hive_width', 10) 
    params.setdefault('hive_height', 8)  
    params.setdefault('comb_stripe_width', 3)
    params.setdefault('max_nectar_per_cell', 4) # Max nectar a single hive comb cell can hold
    params.setdefault('bee_max_nectar_carry', 1)
    params.setdefault('flower_regen_rate', 1)
    params.setdefault('bee_avoid_empty_duration', 20)
    params.setdefault('flower_nectar_capacity_default', 5) 
    params.setdefault('flower_dead_time', 10)
    params.setdefault('interactive_pause', 0.1) # Pause duration for interactive plotting (if mode was different)
    params.setdefault('bee_max_stuck_time', 5)

    # Ensure hive dimensions are integers after potentially being loaded as float/str
    hive_w = int(params.get('hive_width', 10)) 
    hive_h = int(params.get('hive_height', 8))
    params['hive_width'] = hive_w
    params['hive_height'] = hive_h
    
    ## (Hive Internal Entry/Exit Points from Batch File)
    default_internal_x = 0 # Default x for internal hive points (e.g., left edge)
    default_internal_y = hive_h - 1 if hive_h > 0 else 0 # Default y (e.g., top edge)

    params['hive_exit_cell_inside_x'] = int(params.get('hive_exit_cell_inside_x', default_internal_x))
    params['hive_exit_cell_inside_y'] = int(params.get('hive_exit_cell_inside_y', default_internal_y))
    params['hive_entry_cell_inside_x'] = int(params.get('hive_entry_cell_inside_x', default_internal_x))
    params['hive_entry_cell_inside_y'] = int(params.get('hive_entry_cell_inside_y', default_internal_y))

    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    print(f"Loaded parameters (batch): {params}")
    return params

# --- Interactive Mode Setup Functions ---
def get_interactive_parameters(): # Prompts user for parameters in INTERACTIVE MODE
    """
    Gets simulation parameters from user input for interactive mode.
    Returns a dictionary of parameters.
    """
    params = {} # dictionary to store parameters
    print("\n--- Interactive Simulation Parameter Setup ---")
    
    def get_int_input(prompt_text, default_value): # Helper function to get validated integer input
        while True:
            try:
                val_str = input(f"{prompt_text} (default: {default_value}): ")
                if not val_str: # User pressed Enter for default
                    return default_value
                val_int = int(val_str)
                # Example of specific validation (can be expanded)
                if "bees" in prompt_text.lower() and val_int <=0: 
                    print("Number of bees must be positive.")
                    continue
                if ("length" in prompt_text.lower() or "width" in prompt_text.lower() or "height" in prompt_text.lower()) and val_int <=0:
                    print("Dimension/length must be positive.")
                    continue
                return val_int
            except ValueError:
                print("Invalid input. Please enter an integer.")

    params['num_bees'] = get_int_input("Number of bees", 5)
    params['simlength'] = get_int_input("Simulation length (timesteps)", 100)
    params['hive_width'] = get_int_input("Hive width", 10)
    params['hive_height'] = get_int_input("Hive height", 8)
    params['bee_max_nectar_carry'] = get_int_input("Bee max nectar carry", 1)
    
    ## (Default some less critical params for interactive mode to simplify input for user)
    params['comb_stripe_width'] = 3 # Default comb stripe width
    params['max_nectar_per_cell'] = 4 # Default max nectar per hive cell
    params['flower_regen_rate'] = 1 # Default flower nectar regeneration rate
    params['bee_avoid_empty_duration'] = 20 # Default duration bee avoids emptied flower
    params['flower_nectar_capacity_default'] = 5 # Default nectar capacity for randomly generated flowers
    params['flower_dead_time'] = 10 # Default time a flower stays dead
    params['interactive_pause'] = 0.1 # Default pause for interactive plotting
    params['bee_max_stuck_time'] = 5 # Default max time a bee can be stuck

    hive_w = params['hive_width'] 
    hive_h = params['hive_height']
    # For interactive mode, internal hive points can be fixed or derived
    default_internal_x = 0 # e.g. top-left corner for entry/exit
    default_internal_y = hive_h - 1 if hive_h > 0 else 0 
    
    params['hive_exit_cell_inside_x'] = default_internal_x
    params['hive_exit_cell_inside_y'] = default_internal_y
    params['hive_entry_cell_inside_x'] = default_internal_x
    params['hive_entry_cell_inside_y'] = default_internal_y
    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    
    print(f"Interactive parameters set: {params}")
    return params

def generate_interactive_environment(sim_params): # Generates property, flowers, obstacles for INTERACTIVE MODE
    """
    Generates property grid, flower list, and property configuration randomly based on user inputs/defaults.
    sim_params:  dictionary of simulation parameters (some may be used for defaults here)
    Returns world_data (numpy array), flowers_list, property_config (dictionary).
    """
    print("\n--- Interactive Environment Generation ---")
    property_config = {} # dictionary for property settings
    flowers_list = []    # list to hold Flower objects

    # Get property dimensions from user
    while True:
        try:
            prop_w_str = input(f"Enter property width (e.g., 30, default: 30): ")
            prop_w = int(prop_w_str) if prop_w_str else 30
            prop_h_str = input(f"Enter property height (e.g., 20, default: 20): ")
            prop_h = int(prop_h_str) if prop_h_str else 20
            if prop_w > 0 and prop_h > 0: break
            else: print("Dimensions must be positive integers.")
        except ValueError: print("Invalid input for dimensions. Please enter integers.")
    
    property_config['max_x'] = prop_w
    property_config['max_y'] = prop_h
    
    # Hive position on property - can be set to center or randomized
    hive_x_prop = prop_w // 2
    hive_y_prop = prop_h // 2
    property_config['hive_position_on_property'] = (hive_x_prop, hive_y_prop)
    
    world_data = np.zeros((prop_w, prop_h), dtype=int) # Initialize property as empty passable terrain (value 0)

    ## (Random Flower Generation for Interactive Mode)
    while True:
        try:
            num_flowers_str = input(f"Enter number of flowers (e.g., 15, default: 15): ")
            num_flowers = int(num_flowers_str) if num_flowers_str else 15
            if num_flowers >= 0: break
            else: print("Number of flowers cannot be negative.")
        except ValueError: print("Invalid input for number of flowers. Please enter an integer.")

    flower_names_pool = ["Rose", "Tulip", "Daisy", "Lilly", "Orchid", "Poppy", "Sunflower", "Lavender"]
    flower_colors_pool = ['Red', 'Blue', 'Yellow', 'Purple', 'Pink', 'White', 'Orange']
    default_nectar_cap = sim_params.get('flower_nectar_capacity_default', 5) # from sim_params
    default_dead_time = sim_params.get('flower_dead_time', 10)      # from sim_params

    for i in range(num_flowers):
        f_id = f"Flower_Int{i+1}" # Unique ID for interactively generated flower
        f_x = random.randint(0, prop_w - 1) # Random x position
        f_y = random.randint(0, prop_h - 1) # Random y position
        # Simple check to avoid placing flower directly on hive entrance
        while (f_x, f_y) == property_config['hive_position_on_property']:
            f_x = random.randint(0, prop_w - 1)
            f_y = random.randint(0, prop_h - 1)
        f_name = random.choice(flower_names_pool)
        f_color = random.choice(flower_colors_pool)
        # Nectar capacity can be slightly randomized around the default
        f_nectar_capacity = max(1, default_nectar_cap + random.randint(-int(default_nectar_cap/2), int(default_nectar_cap/2))) 
        flowers_list.append(Flower(f_id, (f_x, f_y), f_name, f_color, f_nectar_capacity, default_dead_time))
    print(f"Generated {len(flowers_list)} flowers randomly on the property.")

    ## (Random Obstacle Generation for Interactive Mode)
    while True:
        try:
            num_obstacles_str = input(f"Enter number of rectangular obstacles (e.g., 3, default: 3): ")
            num_obstacles = int(num_obstacles_str) if num_obstacles_str else 3
            if num_obstacles >= 0: break
            else: print("Number of obstacles cannot be negative.")
        except ValueError: print("Invalid input for number of obstacles. Please enter an integer.")

    for i in range(num_obstacles):
        # Define obstacle properties (simple rectangles here)
        obs_w = random.randint(1, max(1, prop_w // 8)) # Obstacle width, ensure it's at least 1
        obs_h = random.randint(1, max(1, prop_h // 8)) # Obstacle height, ensure it's at least 1
        obs_x = random.randint(0, prop_w - obs_w)    # Ensure obstacle starts within bounds
        obs_y = random.randint(0, prop_h - obs_h)    # Ensure obstacle starts within bounds
        
        # Avoid placing obstacle directly over hive entrance (simple check for center of obstacle)
        hive_center_in_obstacle = (obs_x <= hive_x_prop < obs_x + obs_w) and \
                                  (obs_y <= hive_y_prop < obs_y + obs_h)
        if not hive_center_in_obstacle:
            world_data[obs_x : obs_x + obs_w, obs_y : obs_y + obs_h] = 1 # Mark cells as obstacle (value 1)
        # else: print(f"Skipped placing obstacle {i+1} over hive entrance.")
    print(f"Generated {num_obstacles} rectangular obstacles randomly on the property.")
    
    print(f"Generated interactive environment: Dimensions ({prop_w}x{prop_h}), Hive @{property_config['hive_position_on_property']}")
    return world_data, flowers_list, property_config

# --- Plotting Functions (Largely Unchanged from previous complex version) ---
def plot_hive(hive, blist, ax, hive_layout_config): #ax is a single axes which you can draw your subplot.
    ax.clear() # Clear previous plot content from the axis
    max_nectar_val = hive_layout_config.get('max_nectar_per_cell', 4) # Max nectar for color scaling

    val_unbuilt_in_stripe = max_nectar_val + 1 # Value for cells in stripe but not built
    val_outside_stripe = max_nectar_val + 2    # Value for cells outside comb stripe (background)
    
    hive_plot_array = np.full((hive_layout_config['max_x'], hive_layout_config['max_y']), float(val_outside_stripe)) 
    
    comb_width = hive_layout_config.get('comb_stripe_width', 3)
    stripe_center_x = hive_layout_config['max_x'] // 2
    start_x = max(0, stripe_center_x - comb_width // 2)
    end_x = min(hive_layout_config['max_x'], start_x + comb_width)

    for r_idx in range(hive_layout_config['max_x']): # Iterate through hive cells
        for c_idx in range(hive_layout_config['max_y']):
            is_in_stripe = (start_x <= r_idx < end_x) # Check if cell is in the comb stripe
            if is_in_stripe:
                if hive[r_idx, c_idx, 0] == 1: # If comb is built
                    nectar_level = hive[r_idx, c_idx, 1] 
                    hive_plot_array[r_idx, c_idx] = nectar_level 
                else: # Comb not built in stripe
                    hive_plot_array[r_idx, c_idx] = float(val_unbuilt_in_stripe)
            
    num_nectar_shades = max_nectar_val + 1 
    try:
        base_cmap = plt.get_cmap('Oranges', num_nectar_shades + 2) # Colormap for nectar + states
        colors = [base_cmap(i) for i in range(num_nectar_shades)] 
    except ValueError: 
        base_cmap = plt.get_cmap('Oranges')
        colors = [base_cmap(i / (num_nectar_shades -1 if num_nectar_shades >1 else 1) ) for i in range(num_nectar_shades)]
    colors.append((0.85, 0.85, 0.85, 1))  # Light grey for UnbuiltInStripe
    colors.append((0.6, 0.4, 0.2, 1))    # Darker brown for OutsideStripe (hive background)
    
    from matplotlib.colors import ListedColormap, BoundaryNorm # For custom discrete colormap
    custom_cmap = ListedColormap(colors)
    bounds = list(np.arange(0, max_nectar_val + 3, 1)) 
    norm = BoundaryNorm(bounds, custom_cmap.N)

    ax.imshow(hive_plot_array.T, origin="lower", cmap=custom_cmap, norm=norm) # Transpose for (x,y)
    
    # x and y positions of the bees in hive.
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()] # list of x coordinates only if inhive = True
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    if xvalues: # Only plot if there are bees in the hive
        ax.scatter(xvalues, yvalues, c='black', marker='h', s=40, label='Bees')
    ax.set_title(f'Bee Hive')
    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")
    ax.set_xlim(-0.5, hive_layout_config['max_x'] - 0.5) # Set plot limits
    ax.set_ylim(-0.5, hive_layout_config['max_y'] - 0.5)
    if xvalues: ax.legend(loc='upper right', fontsize='small') # Add legend if bees were actually plotted

def plot_property(property_map_data, flowers_list, bees_on_property, property_config, ax): # Plots the outdoor property map
    ax.clear()
    ## (i) Plotted with the tab20 colourmap for terrain.
    ax.imshow(property_map_data.T, origin="lower", cmap='tab20', vmin=0, vmax=19)  
    
    flower_x = [f.get_pos()[0] for f in flowers_list]
    flower_y = [f.get_pos()[1] for f in flowers_list]
    flower_colors_map = {'Red': 'red', 'Blue': 'blue', 'Yellow': 'yellow', 'Purple': 'purple', 'Pink': 'pink', 'White':'lightgray', 'Orange':'orange', 'Green':'green'}
    flower_plot_colors = []
    for f in flowers_list:
        if f.state == 'DEAD':
            flower_plot_colors.append('grey') # Dead flowers are grey
        else:
            flower_plot_colors.append(flower_colors_map.get(f.colour, 'magenta')) # Use defined color or magenta
    
    if flower_x: # Only plot if there are flowers
        ax.scatter(flower_x, flower_y, c=flower_plot_colors, marker='P', s=80, label='Flowers', edgecolors='black', alpha=0.7)

    hive_pos_prop = property_config['hive_position_on_property'] # Get hive location on property
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='gold', marker='H', s=150, edgecolors='black', label='Hive Entrance') # Plot hive entrance
    
    # Plot bees that are currently on the property
    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()]
    bee_y = [b.get_pos()[1] for b in bees_on_property if not b.get_inhive()]
    if bee_x: # Only plot if there are bees on property
      ax.scatter(bee_x, bee_y, c='black', marker='h', s=50, label='Bees')

    ax.set_title('Property')
    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")
    ax.set_xlim(-0.5, property_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, property_config['max_y'] - 0.5)
    handles, labels = ax.get_legend_handles_labels() # For managing legend
    if handles: # Add legend if there are items to show
        ax.legend(loc='upper right', fontsize='small')

def plot_flower_nectar(flowers_list, ax, default_max_nectar): # Creates a bar chart of nectar levels for each flower
    ax.clear()
    if not flowers_list: # Handle case with no flowers
        ax.set_title('Flower Nectar Levels')
        ax.text(0.5, 0.5, "No flowers defined", ha='center', va='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    flower_ids_names = [f"{f.ID}\n({f.name})" for f in flowers_list] # Labels for x-axis
    nectar_levels = [f.currentNectar for f in flowers_list] # Current nectar levels for bars
    
    max_cap = default_max_nectar # Determine the y-axis limit for the bar chart
    if flowers_list:
        all_capacities = [f.nectarCapacity for f in flowers_list if f.nectarCapacity is not None]
        if all_capacities:
            max_cap = max(all_capacities)
    if max_cap == 0: max_cap = 1 # Ensure y-axis has some height

    bar_colors = ['mediumseagreen' if f.state == 'ALIVE' else 'lightcoral' for f in flowers_list] # Color bars by flower state
    bars = ax.bar(flower_ids_names, nectar_levels, color=bar_colors)
    ax.set_ylabel('Nectar Units')
    ax.set_title('Flower Nectar Levels')
    ax.set_ylim(0, max_cap + 1) # Set y-limit
    ax.tick_params(axis='x', labelrotation=30, labelsize=8) # Rotate x-labels for readability

    ## Add text above each bar showing "current/capacity"
    for bar_idx, bar in enumerate(bars):
        yval = bar.get_height() # Current nectar level
        text_offset = 0.05 * (max_cap + 1) if max_cap > 0 else 0.05 # Small offset for text
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + text_offset , 
                f'{yval}/{flowers_list[bar_idx].nectarCapacity}', 
                ha='center', va='bottom', fontsize=7)
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add a light grid for y-axis

# --- Main Simulation Logic ---
# --- Main Simulation Logic ---
def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False): # Main function to run the bee simulation steps
    hiveX, hiveY = sim_params['hive_width'], sim_params['hive_height'] # Get hive dimensions from parameters
    max_nectar_in_comb = sim_params.get('max_nectar_per_cell', 4)
    # Initialize hive data: 3D numpy array (x, y, [comb_status, nectar_amount])
    hive_data = np.zeros((hiveX, hiveY, 2), dtype=int)
    # Configuration for hive layout, passed to bees and plotting functions
    hive_layout_config = {
        'max_x': hiveX, 'max_y': hiveY,
        'comb_stripe_width': sim_params['comb_stripe_width'],
        'max_nectar_per_cell': max_nectar_in_comb,
        'hive_exit_cell_inside': sim_params['hive_exit_cell_inside'],
        'hive_entry_cell_inside': sim_params['hive_entry_cell_inside']
    }

    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside'] # Bees start at the designated internal entry point
    # Sanity check for initial bee position within hive boundaries
    if not (0 <= initial_bee_pos_in_hive[0] < hiveX and 0 <= initial_bee_pos_in_hive[1] < hiveY):
        print(f"Warning: Initial bee position {initial_bee_pos_in_hive} is outside hive dimensions {hiveX}x{hiveY}. Resetting.")
        initial_bee_pos_in_hive = (min(hiveX-1,0) if hiveX > 0 else 0, min(hiveY-1,0) if hiveY > 0 else 0)
        if hiveX > 0 and hiveY > 0: initial_bee_pos_in_hive = (hiveX//2, hiveY//2) # Prefer center if hive has size

    ## (Bee Initialization) - Create bee objects
    all_bees = [
        Bee(f"B{i+1}", initial_bee_pos_in_hive, property_config['hive_position_on_property'],
            sim_params['bee_max_nectar_carry'],
            sim_params.get('bee_avoid_empty_duration', 20),
            sim_params.get('bee_max_stuck_time', 5))
        for i in range(sim_params['num_bees']) # Create the specified number of bees
    ]

    ## (Unconditional Matplotlib Interactive Setup for Step-by-Step Plotting)
    # This setup now happens regardless of the 'interactive_mode' flag's value,
    # as step-by-step plotting is desired for all runs.
    print("Setting up Matplotlib for step-by-step plotting...")
    plt.ion() # Turn on interactive mode for Matplotlib
    fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10)) # Create 2x2 grid of subplots
    axes_dict_interactive = {'hive': axes_array_interactive[0,0],
                             'property': axes_array_interactive[0,1],
                             'nectar': axes_array_interactive[1,0]}
    axes_array_interactive[1,1].axis('off') # Turn off the unused 4th subplot

    ## (Main Simulation Loop)
    for t in range(sim_params['simlength']): # Loop for each timestep of the simulation
        print(f"\n--- Timestep {t+1}/{sim_params['simlength']} ---") # Log current timestep

        random.shuffle(all_bees) # Shuffle bee order each timestep to vary update priority

        # Update each bee
        for i, current_bee_obj in enumerate(all_bees):
            # Gather information about other bees for collision avoidance
            other_bees_details = []
            for j, other_b in enumerate(all_bees):
                if i != j: # Don't include the current bee in its own "other bees" list
                    other_bees_details.append({
                        'pos': other_b.get_pos(),
                        'state': other_b.state,
                        'id': other_b.ID,
                        'inhive': other_b.get_inhive()
                    })

            # Call the bee's main update method
            current_bee_obj.step_change(
                property_map_data,
                flowers_list,
                hive_data,
                hive_layout_config,
                property_config,
                t, # Current timestep
                other_bees_details
            )

        # Update flowers (nectar regeneration)
        for flower in flowers_list:
            flower.regenerate_nectar(rate=sim_params.get('flower_regen_rate',1))

        # --- This entire block below is for step-by-step plotting and occurs every timestep ---
        # Previous 'if interactive_mode:' condition around this block is removed.

        # Check if plot window was closed by user or not initialized, recreate if necessary.
        if fig_interactive is None or not plt.fignum_exists(fig_interactive.number):
            print("Plot window was closed or not initialized, re-creating for step-by-step display.")
            plt.ion() 
            fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10))
            axes_dict_interactive = {'hive': axes_array_interactive[0,0],
                                     'property': axes_array_interactive[0,1],
                                     'nectar': axes_array_interactive[1,0]}
            axes_array_interactive[1,1].axis('off')

        # Clear previous contents of each subplot before drawing the new state
        axes_dict_interactive['hive'].clear()
        axes_dict_interactive['property'].clear()
        axes_dict_interactive['nectar'].clear()

        # Set the super title for the entire figure for the current timestep
        fig_interactive.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')

        bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
        plot_hive(hive_data, bees_in_hive_list, axes_dict_interactive['hive'], hive_layout_config)

        bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
        plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes_dict_interactive['property'])

        plot_flower_nectar(flowers_list, axes_dict_interactive['nectar'], sim_params.get('flower_nectar_capacity_default', 5))

        fig_interactive.tight_layout(rect=[0, 0, 1, 0.96])
        fig_interactive.canvas.draw()
        fig_interactive.canvas.flush_events()

        try:
            pause_duration = float(sim_params.get('interactive_pause', 0.1))
        except ValueError:
            pause_duration = 0.1
        plt.pause(pause_duration)
        # --- End of step-by-step plotting block for the current timestep ---

    # --- After the main simulation loop finishes ---

    # If the simulation was started by loading files (original "batch mode" intent),
    # save the final state of the interactive figure.
    # The 'interactive_mode' flag here refers to how the simulation was SET UP.
    if not interactive_mode and fig_interactive and plt.fignum_exists(fig_interactive.number):
        print("Saving final state of file-input based simulation to beeworld_simulation_end.png")
        try:
            plt.figure(fig_interactive.number) # Ensure the interactive figure is the current figure
            plt.savefig('beeworld_simulation_end.png')
        except Exception as e:
            print(f"Error saving final plot: {e}")

    # Handle the display of the plot window at the end of the simulation
    if fig_interactive and plt.fignum_exists(fig_interactive.number):
        print("Simulation finished. Close the plot window to exit.")
        if not interactive_mode: # If it was a run started from files
             # Message about saving has already been printed if successful
             pass
        plt.ioff() # Turn off Matplotlib's interactive mode
        plt.show() # Keep the plot window open until the user closes it manually
    else:
        # This case might be hit if simlength was 0 or plotting failed to initialize
        print("Simulation finished (no plot to display or plot was closed/failed to initialize).")
        if not interactive_mode: # If it was a "batch setup" run
             print("(Check for 'beeworld_simulation_end.png' if simulation ran to completion and saving was intended and successful)")
# --- Argument Parsing and Main Execution ---
def main(): # Main function to parse arguments and start the simulation
    parser = argparse.ArgumentParser(description="Bee World Simulation") # Setup argument parser
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode (user inputs for parameters, random environment, step-by-step plotting)")
    parser.add_argument("-f", "--mapfile", type=str, default="map1.csv",
                        help="Path to CSV for property map (BATCH MODE ONLY, default: map1.csv)")
    parser.add_argument("-p", "--paramfile", type=str, default="para1.csv",
                        help="Path to CSV for simulation parameters (BATCH MODE ONLY, default: para1.csv)")
    args = parser.parse_args() # Parse command-line arguments

    sim_params = None       # Initialize to None
    world_data = None       # Initialize to None
    flowers_data = None     # Initialize to None
    property_conf = None    # Initialize to None

    if args.interactive: # If interactive flag is set
        ## (Interactive Mode Setup) - Get parameters from user and generate environment randomly
        print(f"Running in INTERACTIVE mode: User inputs for parameters, random environment generation, step-by-step plotting.")
        try:
            sim_params = get_interactive_parameters() # Call new function for user parameter input
            world_data, flowers_data, property_conf = generate_interactive_environment(sim_params) # Call new function for random environment
        except Exception as e:
            print(f"An error occurred during interactive setup: {e}")
            import traceback
            traceback.print_exc() 
            return # Exit if setup fails
    else: # Default is Batch Mode
        ## (Batch Mode Setup) - Load parameters and map from files
        print(f"Running in BATCH mode with map: {args.mapfile} and params: {args.paramfile}")
        try:
            sim_params = load_parameters(args.paramfile) # Load parameters from file
            world_data, flowers_data, property_conf = load_map(args.mapfile, sim_params) # Load map from file
        except FileNotFoundError as e:
            print(f"Error: Required file not found for batch mode. {e}")
            print("Please ensure map and parameter files exist at specified paths or use defaults.")
            return # Exit if essential files are missing
        except Exception as e: # Catch any other errors during batch setup
            print(f"An error occurred during batch setup: {e}")
            import traceback
            traceback.print_exc() 
            return
    
    # Ensure essential data is loaded/generated before trying to run the simulation
    if sim_params and world_data is not None and flowers_data is not None and property_conf:
        run_simulation(sim_params, world_data, flowers_data, property_conf, interactive_mode=args.interactive)
    else:
        print("Critical error: Simulation setup failed (parameters or environment not loaded/generated). Cannot run simulation.")

if __name__ == "__main__": # Standard Python entry point, ensures main() is called when script is run
    main()