# Student Name: Thejana Kottawatta Hewage
# Student ID:   <put your ID here>
#
# beeworld.py - module with class definitions for simulation of bee colony
#
# Version information:
#     2024-04-07 : Initial Version released
#     2025-05-11 : Major revisions for file input, honey model, bee missions, and plotting.
#     2025-05-12 : Added nectar plot and improved bee flower selection logic.
#     2025-05-12 : Integrated Flower "DEAD" state and delayed regeneration.
#     2025-05-12 : Implemented bee collision avoidance and stuck resolution.
#     2025-05-12 : Refined stuck logic, flower regeneration, and entrance clogging.
#     2025-05-13 : Changed default internal hive entrance/exit to top-left.
#     2025-05-13 : Simplified internal hive entry/exit to use fixed points, removed random boundary search.
#
import random
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt

class Flower(): # Defines the state and behavior of flowers in the simulation
    def __init__(self, ID, pos, name, color, nectar_capacity=5, dead_duration=10):
        """
        Initialise Flower object
        ID: unique identifier for the flower
        pos: (x,y) tuple for the flower's position on the property
        name: string name of the flower type (e.g., "Rose")
        color: string color of the flower (e.g., "Red")
        nectar_capacity: maximum nectar units the flower can hold
        dead_duration: timesteps the flower stays dead after nectar depletion
        """
        self.ID = ID
        self.pos = pos # x, y position
        self.name = name
        self.color = color
        self.nectar_capacity = nectar_capacity
        self.current_nectar = nectar_capacity # Flower starts full of nectar
        self.state = 'ALIVE' # Initial state of the flower; States: 'ALIVE', 'DEAD'
        self.regeneration_cooldown = 0 # Countdown timer for when a DEAD flower can start refilling
        self.dead_duration = dead_duration # How long the flower stays dead
        self.is_refilling = False # True only when actively refilling from 0 after being DEAD

    def get_pos(self):
        """Returns the (x,y) position of the flower."""
        return self.pos

    def get_nectar(self):
        """Returns the current amount of nectar in the flower."""
        return self.current_nectar

    def take_nectar(self, amount=1):
        """
        Allows a bee to take nectar from the flower.
        amount: the amount of nectar the bee attempts to take
        Returns the amount of nectar actually taken.
        ## (Flower Nectar Depletion Logic)
        """
        taken = min(amount, self.current_nectar) # Cannot take more nectar than available
        self.current_nectar -= taken
        
        if self.current_nectar <= 0 and self.state == 'ALIVE':
            self.current_nectar = 0 # Clamp nectar at zero, prevent negative values
            self.state = 'DEAD' # Change state to DEAD if nectar is depleted
            self.regeneration_cooldown = self.dead_duration # Set cooldown before regeneration
            self.is_refilling = False 
            # print(f"Flower {self.ID} ({self.name}) is now DEAD.")
        elif self.current_nectar > 0: 
            self.is_refilling = False # If nectar is taken but not depleted, it's not in the special "refilling from dead" state
        return taken

    def regenerate_nectar(self, rate=1):
        """
        Regenerates nectar for the flower over time.
        rate: amount of nectar to regenerate per timestep
        ## (Flower Nectar Regeneration Logic)
        """
        if self.state == 'DEAD':
            if self.regeneration_cooldown > 0:
                self.regeneration_cooldown -= 1 # Countdown to becoming ALIVE again
            else: 
                self.state = 'ALIVE' # Flower comes back to life
                self.is_refilling = True # Enters a state of actively refilling its nectar from zero
                # print(f"Flower {self.ID} ({self.name}) is now ALIVE and starts refilling.")
        
        if self.state == 'ALIVE' and self.is_refilling: # Only refills if it just became ALIVE or is explicitly refilling
            if self.current_nectar < self.nectar_capacity:
                self.current_nectar = min(self.nectar_capacity, self.current_nectar + rate)
                if self.current_nectar == self.nectar_capacity:
                    self.is_refilling = False # Stop the special refilling state once full
                    # print(f"Flower {self.ID} ({self.name}) has refilled to capacity.")

    def is_available_for_targeting(self):
        """Returns True if the flower is alive and has nectar (not necessarily full)."""
        return self.state == 'ALIVE' and self.current_nectar > 0

# --- Bee Class ---
class Bee(): # Defines the state and complex behaviors for a worker bee
    def __init__(self, ID, initial_pos, hive_entrance_property_pos, max_nectar_carry=1, avoid_empty_duration=20, max_stuck_time=5):
        """
        Initialise Bee object
        ID: unique identifier for the bee
        initial_pos: (x,y) starting position of the bee (usually inside hive)
        hive_entrance_property_pos: (x,y) location of the hive entrance on the main property map
        max_nectar_carry: maximum nectar units the bee can carry
        avoid_empty_duration: timesteps a bee avoids a flower it just emptied
        max_stuck_time: timesteps a bee can be stuck before resetting its task
        """
        self.ID = ID
        self.pos = initial_pos 
        self.hive_entrance_property_pos = hive_entrance_property_pos # Main external rendezvous point for hive entry/exit
        self.age = 0 # Bee's age in timesteps
        self.inhive = True # Bee starts inside the hive
        self.state = 'IDLE_IN_HIVE' # Initial state of the bee's state machine
        self.nectar_carried = 0 # Current nectar carried by the bee
        self.max_nectar_carry = max_nectar_carry
        self.current_target_pos = None # (x,y) target position for movement
        self.current_target_object = None # Reference to a target object (e.g., a Flower)
        self.path = [] # Intended for pathfinding, currently not fully utilized in this move logic
        self.recently_emptied_flowers = {} # Tracks flowers this bee emptied: {flower_ID: timestep_emptied}
        self.avoid_empty_duration = avoid_empty_duration
        self.stuck_count = 0 # Counter for how many steps the bee hasn't moved or acted
        self.max_stuck_time = max_stuck_time

    # REMOVED _get_random_free_hive_boundary_cell method (as per version notes)

    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config, current_timestep, other_bees_details_list):
        """
        Update Bee object on each timestep based on its current state and environment.
        property_map_data: numpy array of the main property terrain
        flowers_list: list of Flower objects
        hive_data: numpy array representing the hive's internal state (combs, nectar)
        hive_layout_config: dictionary with hive dimensions and fixed points
        property_config: dictionary with property dimensions and hive location
        current_timestep: the current simulation time
        other_bees_details_list: list of dicts with info about other bees for collision avoidance
        ## (Bee State Machine and Action Logic)
        """
        self.age += 1
        moved_or_acted_this_step = False # Flag to track if bee performed a successful action or move
        previous_state = self.state # For debugging or complex state transitions if needed

        # Determine occupied cells in the bee's current environment (hive or property)
        occupied_cells_in_current_env = set()
        if self.inhive:
            occupied_cells_in_current_env = {info['pos'] for info in other_bees_details_list if info['inhive']}
        else:
            occupied_cells_in_current_env = {info['pos'] for info in other_bees_details_list if not info['inhive']}

        ## (State: IDLE_IN_HIVE) - Bee is in hive, deciding next action
        if self.state == 'IDLE_IN_HIVE':
            self.stuck_count = 0 # Reset stuck count as it's making a decision
            moved_or_acted_this_step = True # Considered an "action" (deciding)
            if self.nectar_carried >= 1 and self._can_build_or_deposit(hive_data, hive_layout_config):
                comb_build_target = self._find_comb_to_build(hive_data, hive_layout_config)
                if comb_build_target:
                    self.current_target_pos = comb_build_target
                    self.state = 'MOVING_TO_COMB_BUILD_SITE'
                    # print(f"Bee {self.ID} decided to build comb at {self.current_target_pos}.")
                else: # Cannot build, try to deposit
                    comb_deposit_target = self._find_comb_to_deposit(hive_data, hive_layout_config)
                    if comb_deposit_target:
                        self.current_target_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE'
                        # print(f"Bee {self.ID} decided to deposit nectar at {self.current_target_pos}.")
                    elif self.nectar_carried < self.max_nectar_carry: # Has nectar, but can't build/deposit, try to get more if not full
                        self.current_target_pos = hive_layout_config['hive_exit_cell_inside'] # Use fixed exit point
                        self.state = 'MOVING_TO_HIVE_EXIT'
                        # print(f"Bee {self.ID} has nectar, but no build/deposit site, heading to exit for more nectar.")
            elif self.nectar_carried < self.max_nectar_carry: # Has no nectar or not enough to build/deposit, and not full
                self.current_target_pos = hive_layout_config['hive_exit_cell_inside'] # Use fixed exit point
                self.state = 'MOVING_TO_HIVE_EXIT'
                # print(f"Bee {self.ID} needs more nectar, heading to hive exit.")
            # If bee is full of nectar and cannot build or deposit, it remains IDLE_IN_HIVE (stuck_count won't increment here due to moved_or_acted_this_step = True)
            # This implies the hive might be full or no buildable spots.

        ## (State: MOVING_TO_HIVE_EXIT) - Bee is inside hive, moving to the internal exit cell
        elif self.state == 'MOVING_TO_HIVE_EXIT':
            if self.pos == self.current_target_pos: # Bee has reached the internal exit cell
                external_exit_pos = self.hive_entrance_property_pos # Target the external hive entrance spot
                is_external_spot_occupied = False
                for other_bee_info in other_bees_details_list: # Check if external spot is clogged
                    if not other_bee_info['inhive'] and other_bee_info['pos'] == external_exit_pos:
                        is_external_spot_occupied = True
                        # print(f"Bee {self.ID} wants to exit, but external entrance {external_exit_pos} is occupied.")
                        break
                
                if is_external_spot_occupied: # External entrance is blocked
                    moved_or_acted_this_step = self._move_randomly(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env) # Jiggle inside
                else: # External entrance is clear
                    self.inhive = False # Bee is now outside
                    self.pos = external_exit_pos # Move to the external hive position
                    self.state = 'SEEKING_FLOWER'
                    self.current_target_pos = None
                    moved_or_acted_this_step = True
                    # print(f"Bee {self.ID} exited hive to {self.pos}, now seeking flower.")
            else: # Not yet at internal exit cell, keep moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        ## (State: SEEKING_FLOWER) - Bee is outside hive, looking for a suitable flower
        elif self.state == 'SEEKING_FLOWER':
            moved_or_acted_this_step = True # Decision process is an "action"
            self.current_target_object = self._find_closest_flower_with_nectar(flowers_list, current_timestep)
            if self.current_target_object:
                self.current_target_pos = self.current_target_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
                # print(f"Bee {self.ID} found flower {self.current_target_object.ID} at {self.current_target_pos}.")
            else: # No suitable flower found
                self.state = 'IDLE_ON_PROPERTY' # Wander around or return to hive
                self.current_target_pos = None
                # print(f"Bee {self.ID} found no suitable flowers, now idle on property.")

        ## (State: MOVING_TO_FLOWER) - Bee is moving towards a targeted flower
        elif self.state == 'MOVING_TO_FLOWER':
            if self.current_target_object is None or not self.current_target_object.is_available_for_targeting(): # Target flower became unavailable (e.g., emptied by another bee)
                if self.current_target_object: # If it had a target that's now gone/empty
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep # Remember this flower
                    # print(f"Bee {self.ID} target flower {self.current_target_object.ID} became unavailable, adding to recently emptied list.")
                self.state = 'SEEKING_FLOWER' # Go back to seeking a new flower
                self.current_target_pos = None
                self.current_target_object = None
                moved_or_acted_this_step = True # Re-evaluating is an action
            elif self.pos == self.current_target_pos: # Arrived at the flower
                self.state = 'COLLECTING_NECTAR'
                moved_or_acted_this_step = True
                # print(f"Bee {self.ID} arrived at flower {self.current_target_object.ID}.")
            else: # Not yet at flower, keep moving
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        ## (State: COLLECTING_NECTAR) - Bee is at a flower, collecting nectar
        elif self.state == 'COLLECTING_NECTAR':
            moved_or_acted_this_step = True # Collecting is an action
            if self.current_target_object and self.current_target_object.is_available_for_targeting() and self.nectar_carried < self.max_nectar_carry:
                amount_to_take = self.max_nectar_carry - self.nectar_carried
                taken = self.current_target_object.take_nectar(amount_to_take)
                self.nectar_carried += taken
                # print(f"Bee {self.ID} collected {taken} nectar from flower {self.current_target_object.ID}. Total carried: {self.nectar_carried}.")
            
            # Check if done collecting (full, or flower empty/gone)
            if self.nectar_carried >= self.max_nectar_carry or \
               not self.current_target_object or \
               (self.current_target_object and not self.current_target_object.is_available_for_targeting()):
                if self.current_target_object and not self.current_target_object.is_available_for_targeting(): 
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep # Remember if flower was emptied by this bee
                    # print(f"Bee {self.ID} emptied flower {self.current_target_object.ID}, adding to recently emptied list.")
                self.current_target_pos = self.hive_entrance_property_pos # Set target to hive entrance
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_target_object = None # No longer targeting the flower
                # print(f"Bee {self.ID} finished collecting, returning to hive entrance. Carried: {self.nectar_carried}.")

        ## (State: RETURNING_TO_HIVE_ENTRANCE) - Bee is outside, moving to the external hive entrance
        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE':
            if self.pos == self.current_target_pos: # Arrived at external hive entrance
                internal_entry_pos = hive_layout_config['hive_entry_cell_inside'] # Target the fixed internal entry point
                is_internal_entry_occupied = False
                for other_bee_info in other_bees_details_list: # Check if internal entry spot is clogged
                    if other_bee_info['inhive'] and other_bee_info['pos'] == internal_entry_pos:
                        is_internal_entry_occupied = True
                        # print(f"Bee {self.ID} wants to enter hive, but internal entry {internal_entry_pos} is occupied.")
                        break
                
                if is_internal_entry_occupied: # Internal entry is blocked
                    moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env) # Jiggle outside
                else: # Internal entry is clear
                    self.inhive = True # Bee is now inside
                    self.pos = internal_entry_pos # Move to the internal hive entry position
                    self.state = 'IDLE_IN_HIVE'
                    self.current_target_pos = None
                    moved_or_acted_this_step = True
                    # print(f"Bee {self.ID} entered hive at {self.pos}.")
            else: # Not yet at hive entrance, keep moving
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        ## (State: MOVING_TO_COMB_BUILD_SITE) - Bee is in hive, moving to a site to build comb
        elif self.state == 'MOVING_TO_COMB_BUILD_SITE':
            if self.pos == self.current_target_pos: # Arrived at build site
                self.state = 'BUILDING_COMB'
                moved_or_acted_this_step = True
                # print(f"Bee {self.ID} arrived at comb build site {self.pos}.")
            else: # Not yet at build site, keep moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        ## (State: BUILDING_COMB) - Bee is at site, building a new comb cell
        elif self.state == 'BUILDING_COMB':
            moved_or_acted_this_step = True # Building is an action
            x, y = self.pos
            # Check if cell is valid for building (within bounds, is empty comb space)
            if self.nectar_carried >= 1 and \
               0 <= x < hive_layout_config['max_x'] and \
               0 <= y < hive_layout_config['max_y'] and \
               hive_data[x, y, 0] == 0: # Layer 0 is comb status (0=empty, 1=built)
                hive_data[x, y, 0] = 1 # Mark comb as built
                hive_data[x, y, 1] = 0 # Initialize nectar in new comb to 0
                self.nectar_carried -= 1 # Cost 1 nectar to build comb
                print(f"Bee {self.ID} built comb at {self.pos}. Nectar left: {self.nectar_carried}")
            else:
                # print(f"Bee {self.ID} failed to build comb at {self.pos} (not enough nectar, or site invalid/occupied).")
                pass # Failed to build (e.g. another bee built there, or out of nectar)
            self.state = 'IDLE_IN_HIVE' # Return to idle to decide next action
            self.current_target_pos = None

        ## (State: MOVING_TO_COMB_DEPOSIT_SITE) - Bee is in hive, moving to a comb cell to deposit nectar
        elif self.state == 'MOVING_TO_COMB_DEPOSIT_SITE':
            if self.pos == self.current_target_pos: # Arrived at deposit site
                self.state = 'DEPOSITING_NECTAR'
                moved_or_acted_this_step = True
                # print(f"Bee {self.ID} arrived at nectar deposit site {self.pos}.")
            else: # Not yet at deposit site, keep moving
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        ## (State: DEPOSITING_NECTAR) - Bee is at comb, depositing nectar
        elif self.state == 'DEPOSITING_NECTAR':
            moved_or_acted_this_step = True # Depositing is an action
            x,y = self.pos
            # Check if cell is valid for depositing (within bounds, is built comb)
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
                # else:
                    # print(f"Bee {self.ID} at {self.pos} to deposit, but cell is full or bee has no nectar to deposit.")
            # else:
                # print(f"Bee {self.ID} failed to deposit at {self.pos} (no nectar, or site invalid/not comb).")
            self.state = 'IDLE_IN_HIVE' # Return to idle
            self.current_target_pos = None

        ## (State: IDLE_ON_PROPERTY) - Bee is outside, no flowers found, wandering or returning
        elif self.state == 'IDLE_ON_PROPERTY':
            moved_or_acted_this_step = True # Deciding or random move is an action
            if self.age % 10 == 0 : # Periodically, decide to return to hive if idle for too long
                self.current_target_pos = self.hive_entrance_property_pos
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                # print(f"Bee {self.ID} was idle on property, now returning to hive.")
            else: # Otherwise, move randomly
                moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env)
        
        ## (Stuck Logic) - Check if bee failed to move or act
        if moved_or_acted_this_step:
            self.stuck_count = 0 # Reset stuck counter if bee moved or acted
        else:
            self.stuck_count += 1 # Increment stuck counter
            # print(f"Bee {self.ID} did not move or act this step. Stuck count: {self.stuck_count}. State: {self.state}, Pos: {self.pos}, Target: {self.current_target_pos}")
        
        if self.stuck_count > self.max_stuck_time: # Bee is stuck for too long
            print(f"Bee {self.ID} STUCK in state {self.state} at {self.pos} for {self.stuck_count} (>{self.max_stuck_time}) steps. Target: {self.current_target_pos}. Resetting task.")
            if self.current_target_object and isinstance(self.current_target_object, Flower): # If was targeting a flower, mark it as recently emptied to avoid retargeting immediately
                   self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
            
            # Reset state based on location
            if self.inhive:
                self.state = 'IDLE_IN_HIVE' 
            else: 
                self.state = 'SEEKING_FLOWER' 
            
            self.current_target_pos = None # Clear current target
            self.current_target_object = None
            self.stuck_count = 0 # Reset stuck counter


    def _move_towards_target(self, map_data, maxX, maxY, occupied_cells, is_in_hive=False):
        """
        Moves the bee one step towards its current_target_pos.
        map_data: terrain data (None if in hive, property_map_data if outside)
        maxX, maxY: boundaries of the current environment (hive or property)
        occupied_cells: set of (x,y) tuples of cells occupied by other bees in the same environment
        is_in_hive: boolean, True if bee is moving within the hive, False if on property
        Returns True if moved, False otherwise.
        ## (Bee Movement and Collision Avoidance Logic)
        """
        if self.current_target_pos is None or self.pos == self.current_target_pos:
            return True # Already at target or no target, so "moved" successfully (or no move needed)

        original_pos = self.pos # Remember current position for stuck check
        dx = self.current_target_pos[0] - self.pos[0]
        dy = self.current_target_pos[1] - self.pos[1]

        # Determine primary and secondary move components (diagonal, then axial)
        move_x_component = np.sign(dx) if dx != 0 else 0
        move_y_component = np.sign(dy) if dy != 0 else 0
        
        preferred_next_steps = [] # List of preferred moves, ordered by preference
        if move_x_component != 0 or move_y_component != 0: # Prefer diagonal move if applicable
            preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1] + move_y_component))
        if move_x_component != 0 and move_y_component != 0: # If diagonal was preferred, also consider axial moves as alternatives
            if move_x_component != 0: # Pure X move
                preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1]))
            if move_y_component != 0: # Pure Y move
                preferred_next_steps.append((self.pos[0], self.pos[1] + move_y_component))
        
        # Ensure preferred steps are unique in case axial moves were the only option initially
        unique_preferred_steps = []
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
            
            self.pos = (newX, newY) # Valid move found
            return True 

        ## (Jiggle Logic) - If preferred moves are blocked, try to jiggle to a nearby free cell
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
            
            self.pos = (jiggle_x, jiggle_y) # Valid jiggle move found
            # print(f"Bee {self.ID} jiggled from {original_pos} to {self.pos} towards {self.current_target_pos}")
            return True 
        
        # print(f"Bee {self.ID} could not move from {original_pos} towards {self.current_target_pos}. Blocked.")
        return False # No move was possible

    def _move_randomly(self, map_data, maxX, maxY, occupied_cells):
        """
        Moves the bee one step randomly to an adjacent valid cell (von Neumann neighborhood).
        Used when bee is stuck or needs to make a non-targeted move (e.g., jiggle at entrance).
        Returns True if moved, False otherwise.
        """
        valid_moves_tuples = [(0,1), (1,0), (0,-1), (-1,0)] # N, E, S, W
        random.shuffle(valid_moves_tuples)
        for move_dx, move_dy in valid_moves_tuples:
            newX = self.pos[0] + move_dx
            newY = self.pos[1] + move_dy
            if 0 <= newX < maxX and 0 <= newY < maxY: # Check boundaries
                # Check terrain (passable if map_data is None (e.g. in hive) or cell value is 0)
                is_passable_terrain = map_data is None or map_data[newX, newY] == 0
                is_occupied_by_other = (newX, newY) in occupied_cells # Check collision
                if is_passable_terrain and not is_occupied_by_other:
                    self.pos = (newX, newY)
                    return True 
        return False # No random move was possible
    
    def _find_closest_flower_with_nectar(self, flowers_list, current_timestep):
        """
        Finds the closest available flower that the bee hasn't recently emptied.
        flowers_list: list of all Flower objects
        current_timestep: current simulation time, for checking recently_emptied_flowers
        Returns a Flower object or None if no suitable flower is found.
        ## (Flower Selection Logic)
        """
        # Clear flowers from recently_emptied_flowers list if their avoid_empty_duration has passed
        to_remove = [fid for fid, ts in self.recently_emptied_flowers.items() if current_timestep - ts > self.avoid_empty_duration]
        for fid in to_remove:
            if fid in self.recently_emptied_flowers: # Ensure key exists before deleting
                del self.recently_emptied_flowers[fid]

        candidate_flowers = [] # List of flowers that are available and not recently emptied
        for flower in flowers_list:
            if flower.is_available_for_targeting() and flower.ID not in self.recently_emptied_flowers:
                candidate_flowers.append(flower)
        
        if not candidate_flowers: # If no ideal candidates, consider any available flower (fallback)
            fallback_candidates = [f for f in flowers_list if f.is_available_for_targeting()]
            if not fallback_candidates:
                return None # No flowers available at all
            candidate_flowers = fallback_candidates # Use fallback list

        closest_flower = None
        min_dist_sq = float('inf') # Using squared distance to avoid sqrt
        random.shuffle(candidate_flowers) # Shuffle to vary choice among equally distant flowers
        for flower in candidate_flowers:
            dist_sq = (self.pos[0] - flower.get_pos()[0])**2 + \
                      (self.pos[1] - flower.get_pos()[1])**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_flower = flower
        return closest_flower

    def _find_comb_to_build(self, hive_data, hive_layout_config):
        """
        Finds a random empty cell within the designated comb-building stripe in the hive.
        hive_data: numpy array of the hive state
        hive_layout_config: dictionary with hive dimensions and comb stripe info
        Returns an (x,y) tuple for a build site, or None if no site is found.
        ## (Hive Comb Building Site Selection)
        """
        comb_width = hive_layout_config.get('comb_stripe_width', 3) # Width of the central building area
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2) # Start x-coordinate of the stripe
        end_x = min(hive_layout_config['max_x'], start_x + comb_width) # End x-coordinate
        
        possible_build_cells = []
        # Iterate only within the comb stripe for potential build locations
        for y_idx in range(hive_layout_config['max_y']): 
            for x_idx in range(start_x, end_x):
                # Check bounds just in case, though stripe calculation should be within hive_layout_config['max_x']
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']:
                    if hive_data[x_idx, y_idx, 0] == 0: # Layer 0, 0 means no comb built yet
                        possible_build_cells.append((x_idx, y_idx))
        if possible_build_cells:
            return random.choice(possible_build_cells) # Return a random valid build cell
        return None # No place to build

    def _find_comb_to_deposit(self, hive_data, hive_layout_config):
        """
        Finds a built comb cell within the stripe that has space for nectar.
        Prefers cells with the least amount of nectar.
        hive_data: numpy array of the hive state
        hive_layout_config: dictionary with hive/comb parameters
        Returns an (x,y) tuple for a deposit site, or None.
        ## (Hive Nectar Deposit Site Selection)
        """
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        max_nectar_per_cell = hive_layout_config.get('max_nectar_per_cell', 4)
        
        possible_cells = [] # Stores ((x,y), nectar_level)
        for y_idx in range(hive_layout_config['max_y']):
            for x_idx in range(start_x, end_x): # Only search within the comb stripe
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']:
                    # Cell must be built (layer 0 is 1) and have less than max nectar (layer 1)
                    if hive_data[x_idx, y_idx, 0] == 1 and hive_data[x_idx, y_idx, 1] < max_nectar_per_cell:
                        possible_cells.append(((x_idx, y_idx), hive_data[x_idx, y_idx, 1]))
        
        if not possible_cells:
            return None # No suitable deposit cells found
        
        possible_cells.sort(key=lambda item: item[1]) # Sort by nectar level, ascending
        
        if possible_cells: # Should always be true if not returned None above
            min_nectar_level = possible_cells[0][1] # Get the lowest nectar level among available cells
            # Filter for all cells that have this minimum nectar level
            least_filled_cells_coords = [cell[0] for cell in possible_cells if cell[1] == min_nectar_level]
            if least_filled_cells_coords:
                return random.choice(least_filled_cells_coords) # Choose randomly among the least filled cells
            
        return None # Should not be reached if possible_cells was populated, but as a fallback

    def _can_build_or_deposit(self, hive_data, hive_layout_config):
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

# --- File Loading Functions ---
def load_map(filename, sim_params): # Loads the property map, flower locations, and obstacles from a CSV file
    world_grid = None # Will hold the numpy array for terrain
    flowers = [] # List to store Flower objects
    property_config = {} # Dictionary for property dimensions and hive location
    prop_w_default, prop_h_default = 20, 15 # Default property width and height
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
            # If it happens after terrain grid, it might just mean no objects, which is fine.
        except ValueError as ve: # Catch errors from header parsing (int() conversion)
            print(f"Error converting critical data (header/terrain) in map file '{filename}': {ve}")
            raise
        except Exception as e: # Catch any other general errors during map loading
            print(f"General error loading map file '{filename}': {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            raise
            
    if world_grid is None: # Fallback if world_grid could not be initialized (e.g. file totally empty or critical error)
        print(f"Warning: World grid could not be initialized from {filename}. Using a default empty grid.")
        property_config.setdefault('max_x', prop_w_default)
        property_config.setdefault('max_y', prop_h_default)
        property_config.setdefault('hive_position_on_property', (hive_x_default, hive_y_default))
        world_grid = np.zeros((property_config['max_x'], property_config['max_y']), dtype=int) # Create a basic empty grid

    print(f"Loaded map: Dimensions ({property_config.get('max_x', 'N/A')}x{property_config.get('max_y', 'N/A')}), Hive Entrance @{property_config.get('hive_position_on_property', 'N/A')}, {len(flowers)} flowers.")
    return world_grid, flowers, property_config

def load_parameters(filename): # Loads simulation parameters from a CSV file
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
    
    ## (Default Simulation Parameters) - Set defaults for any parameters not found in the file
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
    params.setdefault('interactive_pause', 0.1) # Pause duration for interactive plotting
    params.setdefault('bee_max_stuck_time', 5)

    # Ensure hive dimensions are integers after potentially being loaded as float/str
    hive_w = int(params.get('hive_width', 10)) 
    hive_h = int(params.get('hive_height', 8))
    params['hive_width'] = hive_w
    params['hive_height'] = hive_h
    
    ## (Hive Internal Entry/Exit Points) - Define fixed points inside the hive for bees entering/exiting
    default_internal_x = 0 # Default x for internal hive points (e.g., left edge)
    default_internal_y = hive_h - 1 if hive_h > 0 else 0 # Default y (e.g., top edge, considering origin lower)

    # Allow overriding these fixed points via parameter file
    params['hive_exit_cell_inside_x'] = int(params.get('hive_exit_cell_inside_x', default_internal_x))
    params['hive_exit_cell_inside_y'] = int(params.get('hive_exit_cell_inside_y', default_internal_y))
    params['hive_entry_cell_inside_x'] = int(params.get('hive_entry_cell_inside_x', default_internal_x))
    params['hive_entry_cell_inside_y'] = int(params.get('hive_entry_cell_inside_y', default_internal_y))

    # Store as tuples for convenience
    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    print(f"Loaded parameters: {params}")
    return params

# --- Plotting Functions ---
def plot_hive(hive_data, bees_in_hive, ax, hive_layout_config): # Plots the state of the bee hive
    ax.clear() # Clear previous plot on this axis
    max_nectar_val = hive_layout_config.get('max_nectar_per_cell', 4) 

    ## (Hive Plot Visual Values) - Define values for different visual states in the plot
    val_unbuilt_in_stripe = max_nectar_val + 1 # Value for cells within comb stripe but not yet built
    val_outside_stripe = max_nectar_val + 2    # Value for cells outside the comb stripe (general hive background)
    
    # Initialize plot array with the "outside stripe" value
    hive_plot_array = np.full((hive_layout_config['max_x'], hive_layout_config['max_y']), float(val_outside_stripe)) 
    
    # Determine the boundaries of the central comb stripe
    comb_width = hive_layout_config.get('comb_stripe_width', 3)
    stripe_center_x = hive_layout_config['max_x'] // 2
    start_x = max(0, stripe_center_x - comb_width // 2)
    end_x = min(hive_layout_config['max_x'], start_x + comb_width)

    # Populate the plot array based on hive_data
    for r_idx in range(hive_layout_config['max_x']): # x-coordinate
        for c_idx in range(hive_layout_config['max_y']): # y-coordinate
            is_in_stripe = (start_x <= r_idx < end_x)
            if is_in_stripe:
                if hive_data[r_idx, c_idx, 0] == 1: # If comb is built (layer 0 = 1)
                    nectar_level = hive_data[r_idx, c_idx, 1] # Get nectar level (layer 1)
                    hive_plot_array[r_idx, c_idx] = nectar_level 
                else: # Comb not built in stripe
                    hive_plot_array[r_idx, c_idx] = float(val_unbuilt_in_stripe)
            # Cells outside stripe remain val_outside_stripe
            
    ## (Hive Plot Colormap Setup)
    num_nectar_shades = max_nectar_val + 1 # Number of shades for nectar levels (0 to max_nectar_val)
    try:
        # Attempt to get a colormap with enough distinct colors for nectar + unbuilt + outside_stripe
        base_cmap = plt.cm.get_cmap('Oranges', num_nectar_shades + 2) 
        colors = [base_cmap(i) for i in range(num_nectar_shades)] # Nectar shades (0 to max_nectar)
    except ValueError: # Fallback if 'Oranges' cannot generate that many distinct colors (e.g. if max_nectar_val is very high)
        base_cmap = plt.cm.get_cmap('Oranges') # Get base Oranges map
        # Manually create shades for nectar
        colors = [base_cmap(i / (num_nectar_shades -1 if num_nectar_shades >1 else 1) ) for i in range(num_nectar_shades)]

    colors.append((0.85, 0.85, 0.85, 1))  # Light grey for UnbuiltInStripe
    colors.append((0.6, 0.4, 0.2, 1))    # Darker brown for OutsideStripe (hive background)
    
    from matplotlib.colors import ListedColormap, BoundaryNorm # For custom discrete colormap
    custom_cmap = ListedColormap(colors)
    
    # Define boundaries for the discrete colors
    # e.g., for max_nectar=4 -> bounds are [0, 1, 2, 3, 4, 5, 6, 7]
    # nectar levels 0-4 map to colors[0]-colors[4]
    # val_unbuilt_in_stripe (5) maps to colors[5] (grey)
    # val_outside_stripe (6) maps to colors[6] (brown)
    bounds = list(np.arange(0, max_nectar_val + 3, 1)) 
    norm = BoundaryNorm(bounds, custom_cmap.N)

    ax.imshow(hive_plot_array.T, origin="lower", cmap=custom_cmap, norm=norm) # .T to match (x,y) interpretation
    
    # Plot bees that are currently in the hive
    xvalues = [b.get_pos()[0] for b in bees_in_hive if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in bees_in_hive if b.get_inhive()]
    if xvalues: # Only plot if there are bees in the hive
        ax.scatter(xvalues, yvalues, c='black', marker='h', s=40, label='Bees') # Hexagon marker for bees
    ax.set_title(f'Bee Hive (Nectar: 0-{max_nectar_val})')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, hive_layout_config['max_x'] - 0.5) # Set plot limits
    ax.set_ylim(-0.5, hive_layout_config['max_y'] - 0.5)
    if bees_in_hive: ax.legend(loc='upper right', fontsize='small') # Add legend if bees are plotted

def plot_property(property_map_data, flowers_list, bees_on_property, property_config, ax): # Plots the outdoor property
    ax.clear()
    ## (Property Terrain Plot) - Use 'tab20' as requested for general terrain
    ax.imshow(property_map_data.T, origin="lower", cmap='tab20', vmin=0, vmax=19) 
    
    ## (Flower Plotting)
    flower_x = [f.get_pos()[0] for f in flowers_list]
    flower_y = [f.get_pos()[1] for f in flowers_list]
    # Define a mapping from flower color names to matplotlib color strings
    flower_colors_map = {'Red': 'red', 'Blue': 'blue', 'Yellow': 'yellow', 
                         'Purple': 'purple', 'Pink': 'pink', 'White':'lightgray', 
                         'Orange':'orange', 'Green':'green'}
    flower_plot_colors = [] # List to hold the actual plot colors for each flower
    for f in flowers_list:
        if f.state == 'DEAD':
            flower_plot_colors.append('grey') # Dead flowers are grey
        else:
            flower_plot_colors.append(flower_colors_map.get(f.color, 'magenta')) # Use defined color or magenta as fallback
    
    if flower_x: # Only plot if there are flowers
        ax.scatter(flower_x, flower_y, c=flower_plot_colors, marker='P', s=80, label='Flowers', edgecolors='black', alpha=0.7) # 'P' for plus (filled) marker

    ## (Hive Entrance Plotting)
    hive_pos_prop = property_config['hive_position_on_property']
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='gold', marker='H', s=150, edgecolors='black', label='Hive Entrance') # Large 'H' marker for hive

    ## (Bee Plotting on Property)
    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()] # Bees that are outside
    bee_y = [b.get_pos()[1] for b in bees_on_property if not b.get_inhive()]
    if bee_x: # Only plot if there are bees on the property
        ax.scatter(bee_x, bee_y, c='black', marker='h', s=50, label='Bees')

    ax.set_title('Property')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, property_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, property_config['max_y'] - 0.5)
    handles, labels = ax.get_legend_handles_labels() # For managing legend
    if handles:
        ax.legend(loc='upper right', fontsize='small')


def plot_flower_nectar(flowers_list, ax, default_max_nectar): # Creates a bar chart of nectar levels for each flower
    ax.clear()
    if not flowers_list: # Handle case with no flowers defined
        ax.set_title('Flower Nectar Levels')
        ax.text(0.5, 0.5, "No flowers defined", ha='center', va='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    flower_ids_names = [f"{f.ID}\n({f.name})" for f in flowers_list] # Labels for x-axis (ID and name)
    nectar_levels = [f.current_nectar for f in flowers_list] # Current nectar levels for y-axis
    
    # Determine the maximum capacity for scaling the y-axis of the bar chart
    max_cap = default_max_nectar 
    if flowers_list:
        all_capacities = [f.nectar_capacity for f in flowers_list if f.nectar_capacity is not None]
        if all_capacities:
            max_cap = max(all_capacities)
    if max_cap == 0: max_cap = 1 # Ensure y-axis has some height even if all capacities are 0

    # Bar colors depend on flower state
    bar_colors = ['mediumseagreen' if f.state == 'ALIVE' else 'lightcoral' for f in flowers_list]
    bars = ax.bar(flower_ids_names, nectar_levels, color=bar_colors)
    ax.set_ylabel('Nectar Units')
    ax.set_title('Flower Nectar Levels (Green=Alive, Red=Dead/Emptying)')
    ax.set_ylim(0, max_cap + 1) # Set y-limit slightly above max capacity
    ax.tick_params(axis='x', labelrotation=30, labelsize=8) # Rotate x-labels for readability

    ## (Bar Chart Text Annotations) - Add text above each bar showing "current/capacity"
    for bar_idx, bar in enumerate(bars):
        yval = bar.get_height() # Current nectar level
        text_offset = 0.05 * (max_cap + 1) if max_cap > 0 else 0.05 # Small offset for text
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + text_offset , 
                f'{yval}/{flowers_list[bar_idx].nectar_capacity}', # Text: "current/capacity"
                ha='center', va='bottom', fontsize=7)
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add a light grid for y-axis

# --- Main Simulation Logic ---
def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False): # Main function to run the bee simulation
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
    
    ## (Initial Bee Positioning)
    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside'] # Bees start at the designated internal entry point
    # Sanity check for initial bee position within hive boundaries
    if not (0 <= initial_bee_pos_in_hive[0] < hiveX and 0 <= initial_bee_pos_in_hive[1] < hiveY):
        print(f"Warning: Initial bee position {initial_bee_pos_in_hive} is outside hive dimensions {hiveX}x{hiveY}. Resetting.")
        # Fallback: place at (0,0) or center if possible
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

    fig_interactive = None # Figure object for interactive plotting
    axes_dict_interactive = None # Dictionary of axes for interactive subplots

    if interactive_mode: # Setup for interactive plotting
        plt.ion() # Turn on interactive mode for matplotlib
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

        ## (Interactive Plotting Update)
        if interactive_mode:
            # Check if plot window was closed by user, recreate if necessary
            if fig_interactive is None or not plt.fignum_exists(fig_interactive.number): 
                print("Interactive plot window was closed, re-creating.")
                fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10))
                axes_dict_interactive = {'hive': axes_array_interactive[0,0], 
                                         'property': axes_array_interactive[0,1], 
                                         'nectar': axes_array_interactive[1,0]}
                axes_array_interactive[1,1].axis('off')
                plt.ion() # Ensure interactive mode is on

            # Clear previous contents of each subplot
            axes_dict_interactive['hive'].clear()
            axes_dict_interactive['property'].clear()
            axes_dict_interactive['nectar'].clear()
            
            fig_interactive.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')

            # Plot hive state
            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, axes_dict_interactive['hive'], hive_layout_config)

            # Plot property state
            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes_dict_interactive['property'])
            
            # Plot flower nectar levels
            plot_flower_nectar(flowers_list, axes_dict_interactive['nectar'], sim_params.get('flower_nectar_capacity_default', 5))

            fig_interactive.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust layout to prevent title overlap
            fig_interactive.canvas.draw() # Redraw the canvas
            fig_interactive.canvas.flush_events() # Process GUI events
            try:
                pause_duration = float(sim_params.get('interactive_pause', 0.1))
            except ValueError: # Handle if pause duration in params is not a valid float
                pause_duration = 0.1 
            plt.pause(pause_duration) # Pause to allow plot to be visible

        ## (Batch Mode End-of-Simulation Plotting)
        elif t == sim_params['simlength'] - 1: # If in batch mode and it's the last timestep
            batch_fig, batch_axes_array = plt.subplots(2, 2, figsize=(16, 10))
            current_batch_axes = {'hive': batch_axes_array[0,0], 
                                  'property': batch_axes_array[0,1], 
                                  'nectar': batch_axes_array[1,0]}
            batch_axes_array[1,1].axis('off') # Turn off unused subplot
            batch_fig.suptitle(f"Bee World - Final State - Timestep: {t+1}", fontsize=16, fontweight='bold')
            
            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, current_batch_axes['hive'], hive_layout_config)
            
            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, current_batch_axes['property'])
            
            plot_flower_nectar(flowers_list, current_batch_axes['nectar'], sim_params.get('flower_nectar_capacity_default', 5))
            
            batch_fig.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig('beeworld_simulation_end.png') # Save the final plot to a file
            print("Saved final simulation state to beeworld_simulation_end.png")
            plt.close(batch_fig) # Close the figure to free memory

    # After simulation loop finishes
    if interactive_mode and fig_interactive and plt.fignum_exists(fig_interactive.number):
        print("Simulation finished. Close the plot window to exit.")
        plt.ioff() # Turn off interactive mode
        plt.show() # Keep the final plot window open until user closes it
    elif not interactive_mode:
        print("Batch simulation finished.")
    else: # Interactive mode was on, but window might have been closed early
        print("Simulation finished (no plot shown or plot was closed).")

# --- Argument Parsing and Main Execution ---
def main(): # Main function to parse arguments and start the simulation
    parser = argparse.ArgumentParser(description="Bee World Simulation") # Setup argument parser
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode (step-by-step plotting)")
    parser.add_argument("-f", "--mapfile", type=str, default="map1.csv",
                        help="Path to the CSV file defining the property map (default: map1.csv)")
    parser.add_argument("-p", "--paramfile", type=str, default="para1.csv",
                        help="Path to the CSV file defining simulation parameters (default: para1.csv)")
    args = parser.parse_args() # Parse command-line arguments

    try:
        sim_params = load_parameters(args.paramfile) # Load simulation parameters
        world_data, flowers_data, property_conf = load_map(args.mapfile, sim_params) # Load map and flower data
    except FileNotFoundError as e:
        print(f"Error: Required file not found. {e}")
        print("Please ensure map and parameter files exist at the specified paths or in the current directory if using defaults.")
        return # Exit if essential files are missing
    except Exception as e: # Catch any other errors during setup
        print(f"An error occurred during setup: {e}")
        import traceback
        traceback.print_exc() 
        return

    if args.interactive:
        print(f"Running in INTERACTIVE mode with map: {args.mapfile} and params: {args.paramfile}")
    else:
        print(f"Running in BATCH mode with map: {args.mapfile} and params: {args.paramfile}")

    # Run the simulation with loaded configurations
    run_simulation(sim_params, world_data, flowers_data, property_conf, interactive_mode=args.interactive)

if __name__ == "__main__": # Standard Python entry point
    main()