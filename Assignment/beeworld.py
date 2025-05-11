# Student Name: <put your name here>
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information:
#     2024-04-07 : Initial Version released
#     2025-05-11 : Major revisions for file input, honey model, bee missions, and plotting.
#     2025-05-12 : Added nectar plot and improved bee flower selection logic.
#     2025-05-12 : Integrated Flower "DEAD" state and delayed regeneration.
#     2025-05-12 : Implemented bee collision avoidance and stuck resolution.
#     2025-05-12 : Refined stuck logic, flower regeneration, and entrance clogging.
#     2025-05-13 : Changed default internal hive entrance/exit to top-left.
#     2025-05-13 : Visual changes to property/hive plots and added configurable tree obstacles.
#
import random
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm # Added for custom colormap

# --- Helper Function for Parsing Coordinate Lists ---
def parse_coord_list_param(param_str_value, default_if_empty_or_error_str=""):
    coords = []
    if not param_str_value and default_if_empty_or_error_str:
        param_str_value = default_if_empty_or_error_str
    if not param_str_value:
        return coords

    parts = param_str_value.replace(" ", "").split(';')
    for part in parts:
        if part: 
            try:
                x_str, y_str = part.strip("()").split(',')
                coords.append((int(x_str), int(y_str)))
            except ValueError:
                print(f"Warning: Could not parse coordinate part '{part}' in '{param_str_value}'. Skipping.")
    return coords

# --- Flower Class ---
class Flower():
    def __init__(self, ID, pos, name, color_str_from_csv, nectar_capacity=5, dead_duration=10): # color_str_from_csv not directly used for self.color
        self.ID = ID
        self.pos = pos # (x,y)
        self.name = name
        # self.color = color_str_from_csv # Store original string if needed, but plot_color will be assigned
        self.plot_color = None # Will be assigned in load_map
        self.nectar_capacity = nectar_capacity
        self.current_nectar = nectar_capacity
        self.state = 'ALIVE' # States: 'ALIVE', 'DEAD'
        self.regeneration_cooldown = 0
        self.dead_duration = dead_duration
        self.is_refilling = False 

    def get_pos(self):
        return self.pos

    def get_nectar(self):
        return self.current_nectar

    def take_nectar(self, amount=1):
        taken = min(amount, self.current_nectar)
        self.current_nectar -= taken
        
        if self.current_nectar <= 0 and self.state == 'ALIVE':
            self.current_nectar = 0 
            self.state = 'DEAD'
            self.regeneration_cooldown = self.dead_duration
            self.is_refilling = False 
        elif self.current_nectar > 0: 
            self.is_refilling = False 
        return taken

    def regenerate_nectar(self, rate=1):
        if self.state == 'DEAD':
            if self.regeneration_cooldown > 0:
                self.regeneration_cooldown -= 1
            else: 
                self.state = 'ALIVE'
                self.is_refilling = True 
        
        if self.state == 'ALIVE' and self.is_refilling:
            if self.current_nectar < self.nectar_capacity:
                self.current_nectar = min(self.nectar_capacity, self.current_nectar + rate)
                if self.current_nectar == self.nectar_capacity:
                    self.is_refilling = False 

    def is_available_for_targeting(self):
        """Returns True if the flower is alive and has nectar.""" # Reverted to > 0 for better activity
        return self.state == 'ALIVE' and self.current_nectar > 0


# --- Bee Class ---
class Bee():
    def __init__(self, ID, initial_pos, hive_entrance_property_pos, max_nectar_carry=1, avoid_empty_duration=20, max_stuck_time=5):
        self.ID = ID
        self.pos = initial_pos 
        self.hive_entrance_property_pos = hive_entrance_property_pos
        self.age = 0
        self.inhive = True 
        self.state = 'IDLE_IN_HIVE'
        self.nectar_carried = 0
        self.max_nectar_carry = max_nectar_carry
        self.current_target_pos = None
        self.current_target_object = None
        self.path = [] 
        self.recently_emptied_flowers = {} 
        self.avoid_empty_duration = avoid_empty_duration
        self.stuck_count = 0
        self.max_stuck_time = max_stuck_time


    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config, current_timestep, other_bees_details_list, tree_locations_set):
        self.age += 1
        moved_or_acted_this_step = False 
        previous_state = self.state # Store state before any changes this step

        # Derive occupied cells for current environment
        occupied_cells_in_current_env = set()
        if self.inhive:
            occupied_cells_in_current_env = {info['pos'] for info in other_bees_details_list if info['inhive']}
        else:
            occupied_property_bee_cells = {info['pos'] for info in other_bees_details_list if not info['inhive']}
            occupied_cells_in_current_env = occupied_property_bee_cells.union(tree_locations_set)


        if self.state == 'IDLE_IN_HIVE':
            # Decision phase: if it leads to a state change, it's an "action"
            action_decided = False
            if self.nectar_carried >= 1 and self._can_build_or_deposit(hive_data, hive_layout_config):
                comb_build_target = self._find_comb_to_build(hive_data, hive_layout_config)
                if comb_build_target:
                    self.current_target_pos = comb_build_target
                    self.state = 'MOVING_TO_COMB_BUILD_SITE'
                    action_decided = True
                else:
                    comb_deposit_target = self._find_comb_to_deposit(hive_data, hive_layout_config)
                    if comb_deposit_target:
                        self.current_target_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE'
                        action_decided = True
                    elif self.nectar_carried < self.max_nectar_carry: # Has some nectar, but can't build/deposit, wants to exit
                        self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                        self.state = 'MOVING_TO_HIVE_EXIT'
                        action_decided = True
            elif self.nectar_carried < self.max_nectar_carry: # Needs more nectar
                self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                self.state = 'MOVING_TO_HIVE_EXIT'
                action_decided = True
            
            moved_or_acted_this_step = action_decided # True if state changed due to decision

        elif self.state == 'MOVING_TO_HIVE_EXIT':
            if self.pos == self.current_target_pos: # Bee is at internal exit point
                external_exit_pos = self.hive_entrance_property_pos
                is_external_spot_occupied = False
                for other_bee_info in other_bees_details_list: # Check against bees OUTSIDE
                    if not other_bee_info['inhive'] and other_bee_info['pos'] == external_exit_pos:
                        is_external_spot_occupied = True
                        break
                
                if is_external_spot_occupied:
                    # Try to jiggle *inside the hive* if external exit is blocked
                    # print(f"Bee {self.ID} trying to exit, external spot {external_exit_pos} blocked. Jiggling inside.")
                    moved_or_acted_this_step = self._move_randomly(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env) # Pass in-hive occupied cells
                else: 
                    self.inhive = False
                    self.pos = external_exit_pos
                    self.state = 'SEEKING_FLOWER'
                    self.current_target_pos = None
                    moved_or_acted_this_step = True
            else: 
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'SEEKING_FLOWER':
            moved_or_acted_this_step = True 
            self.current_target_object = self._find_closest_flower_with_nectar(flowers_list, current_timestep)
            if self.current_target_object:
                self.current_target_pos = self.current_target_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
            else:
                self.state = 'IDLE_ON_PROPERTY'
                self.current_target_pos = None

        elif self.state == 'MOVING_TO_FLOWER':
            if self.current_target_object is None or not self.current_target_object.is_available_for_targeting():
                if self.current_target_object:
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
                self.state = 'SEEKING_FLOWER'
                self.current_target_pos = None
                self.current_target_object = None
                moved_or_acted_this_step = True
            elif self.pos == self.current_target_pos:
                self.state = 'COLLECTING_NECTAR'
                moved_or_acted_this_step = True
            else:
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        elif self.state == 'COLLECTING_NECTAR':
            moved_or_acted_this_step = True 
            if self.current_target_object and self.current_target_object.is_available_for_targeting() and self.nectar_carried < self.max_nectar_carry:
                amount_to_take = self.max_nectar_carry - self.nectar_carried
                taken = self.current_target_object.take_nectar(amount_to_take)
                self.nectar_carried += taken
            
            if self.nectar_carried >= self.max_nectar_carry or \
               not self.current_target_object or \
               (self.current_target_object and not self.current_target_object.is_available_for_targeting()):
                if self.current_target_object and not self.current_target_object.is_available_for_targeting(): 
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
                self.current_target_pos = self.hive_entrance_property_pos 
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_target_object = None

        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE':
            if self.pos == self.current_target_pos: 
                internal_entry_pos = hive_layout_config['hive_entry_cell_inside']
                is_internal_entry_occupied = False
                for other_bee_info in other_bees_details_list: 
                    if other_bee_info['inhive'] and other_bee_info['pos'] == internal_entry_pos:
                        is_internal_entry_occupied = True
                        break
                
                if is_internal_entry_occupied:
                    # print(f"Bee {self.ID} at {self.pos} cannot enter, internal spot {internal_entry_pos} blocked. Stepping aside on property.")
                    moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env)
                else: 
                    self.inhive = True
                    self.pos = internal_entry_pos
                    self.state = 'IDLE_IN_HIVE'
                    self.current_target_pos = None
                    moved_or_acted_this_step = True
            else: 
                moved_or_acted_this_step = self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env, is_in_hive=False)

        elif self.state == 'MOVING_TO_COMB_BUILD_SITE':
            if self.pos == self.current_target_pos:
                self.state = 'BUILDING_COMB'
                moved_or_acted_this_step = True
            else:
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'BUILDING_COMB':
            moved_or_acted_this_step = True 
            x, y = self.pos
            if self.nectar_carried >= 1 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x, y, 0] == 0:
                hive_data[x, y, 0] = 1
                hive_data[x, y, 1] = 0
                self.nectar_carried -= 1
                print(f"Bee {self.ID} built comb at {self.pos}")
            self.state = 'IDLE_IN_HIVE' 
            self.current_target_pos = None

        elif self.state == 'MOVING_TO_COMB_DEPOSIT_SITE':
            if self.pos == self.current_target_pos:
                self.state = 'DEPOSITING_NECTAR'
                moved_or_acted_this_step = True
            else:
                moved_or_acted_this_step = self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], occupied_cells_in_current_env, is_in_hive=True)

        elif self.state == 'DEPOSITING_NECTAR':
            moved_or_acted_this_step = True 
            x,y = self.pos
            if self.nectar_carried > 0 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x,y,0] == 1:
                max_nectar_in_cell = hive_layout_config.get('max_nectar_per_cell', 4)
                can_deposit = max_nectar_in_cell - hive_data[x,y,1]
                deposited_amount = min(self.nectar_carried, can_deposit)
                if deposited_amount > 0:
                    hive_data[x,y,1] += deposited_amount
                    self.nectar_carried -= deposited_amount
                    print(f"Bee {self.ID} deposited {deposited_amount} nectar at {self.pos}. Cell now has {hive_data[x,y,1]}")
            self.state = 'IDLE_IN_HIVE' 
            self.current_target_pos = None

        elif self.state == 'IDLE_ON_PROPERTY':
            moved_or_acted_this_step = True 
            if self.age % 10 == 0 : 
                 self.current_target_pos = self.hive_entrance_property_pos
                 self.state = 'RETURNING_TO_HIVE_ENTRANCE'
            else: 
                moved_or_acted_this_step = self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'], occupied_cells_in_current_env)
        
        # Manage stuck_count
        if moved_or_acted_this_step: # If any move or productive state change happened
            self.stuck_count = 0
        else: # No move was made and state didn't change to something inherently productive
            self.stuck_count += 1
        
        # Check for being stuck (if stuck_count gets too high and bee is in a state where it should be progressing)
        if self.stuck_count > self.max_stuck_time:
            # print(f"Bee {self.ID} STUCK_COUNT threshold reached in state {self.state} at {self.pos}. Resetting.")
            # Only reset if in a state that implies it's trying to achieve something specific by moving/acting
            # and not if it's an inherently 'waiting' or 'action-performing' state where stuck_count should have been reset.
            # The moved_or_acted_this_step flag should handle this better.
            print(f"Bee {self.ID} stuck in state {self.state} at {self.pos} for {self.stuck_count} (>{self.max_stuck_time}) steps. Target: {self.current_target_pos}. Resetting task.")
            if self.current_target_object and isinstance(self.current_target_object, Flower):
                 self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
            
            if self.inhive:
                self.state = 'IDLE_IN_HIVE' 
            else: 
                self.state = 'SEEKING_FLOWER' 
            
            self.current_target_pos = None
            self.current_target_object = None
            self.stuck_count = 0 # Reset after handling the stuck situation


    def _move_towards_target(self, map_data, maxX, maxY, occupied_cells, is_in_hive=False):
        if self.current_target_pos is None or self.pos == self.current_target_pos:
            return True 

        original_pos = self.pos
        dx = self.current_target_pos[0] - self.pos[0]
        dy = self.current_target_pos[1] - self.pos[1]

        move_x_component = np.sign(dx) if dx != 0 else 0
        move_y_component = np.sign(dy) if dy != 0 else 0
        
        preferred_next_steps = []
        if move_x_component != 0 or move_y_component != 0: 
            preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1] + move_y_component))
        if move_x_component != 0 and move_y_component != 0: 
            if move_x_component != 0:
                preferred_next_steps.append((self.pos[0] + move_x_component, self.pos[1]))
            if move_y_component != 0:
                preferred_next_steps.append((self.pos[0], self.pos[1] + move_y_component))
        
        unique_preferred_steps = []
        seen_steps_set = set()
        for step_tuple in preferred_next_steps:
            if step_tuple not in seen_steps_set:
                unique_preferred_steps.append(step_tuple)
                seen_steps_set.add(step_tuple)

        for newX_float, newY_float in unique_preferred_steps:
            newX, newY = int(newX_float), int(newY_float)
            if not (0 <= newX < maxX and 0 <= newY < maxY): continue
            # Use '2' as passable if that's the convention for green background
            # Assuming 0 is passable for general logic, or map_data handles obstacles with other non-zero values
            passable_terrain_value = 0 # Or 2, if 2 is defined as open grass in map data
            if not is_in_hive and map_data is not None and map_data[newX, newY] != passable_terrain_value: 
                # Check if it's a non-passable terrain type, specific value depends on map1.csv convention
                # If '2' is grass, then map_data[newX, newY] != 2 means obstacle.
                # The original prompt for plot used specific values for grass, water, rock.
                # Let's assume map_data != 0 is an obstacle for now, unless 0 is water etc.
                # This needs to align with map1.csv values. For now, assume 0 is open, >0 obstacle.
                if map_data[newX, newY] != 0: # Assuming 0 is open
                    continue 
            if (newX, newY) in occupied_cells: continue 
            
            self.pos = (newX, newY)
            return True 

        jiggle_moves = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)] 
        random.shuffle(jiggle_moves)
        for move_dx, move_dy in jiggle_moves:
            jiggle_x, jiggle_y = self.pos[0] + move_dx, self.pos[1] + move_dy
            
            if (jiggle_x, jiggle_y) == original_pos : 
                continue

            if not (0 <= jiggle_x < maxX and 0 <= jiggle_y < maxY): continue
            if not is_in_hive and map_data is not None and map_data[jiggle_x, jiggle_y] != 0: continue # Assuming 0 is open
            if (jiggle_x, jiggle_y) in occupied_cells: continue
            
            self.pos = (jiggle_x, jiggle_y)
            return True 
        
        return False

    def _move_randomly(self, map_data, maxX, maxY, occupied_cells):
        valid_moves_tuples = [(0,1), (1,0), (0,-1), (-1,0)] 
        random.shuffle(valid_moves_tuples)
        for move_dx, move_dy in valid_moves_tuples:
            newX = self.pos[0] + move_dx
            newY = self.pos[1] + move_dy
            if 0 <= newX < maxX and 0 <= newY < maxY:
                # Passable terrain_value assumption (e.g., 0 or 2 for grass)
                passable_terrain_value = 0 # Or 2, needs to match map_data convention
                is_passable_terrain = map_data is None or map_data[newX, newY] == passable_terrain_value
                if map_data is not None and map_data[newX, newY] != 0: # Assuming 0 is open
                    is_passable_terrain = False

                is_occupied_by_other = (newX, newY) in occupied_cells
                if is_passable_terrain and not is_occupied_by_other:
                    self.pos = (newX, newY)
                    return True 
        return False
    
    def _find_closest_flower_with_nectar(self, flowers_list, current_timestep):
        to_remove = [fid for fid, ts in self.recently_emptied_flowers.items() if current_timestep - ts > self.avoid_empty_duration]
        for fid in to_remove:
            if fid in self.recently_emptied_flowers:
                 del self.recently_emptied_flowers[fid]

        candidate_flowers = []
        for flower in flowers_list:
            if flower.is_available_for_targeting() and flower.ID not in self.recently_emptied_flowers:
                candidate_flowers.append(flower)
        
        if not candidate_flowers:
            fallback_candidates = [f for f in flowers_list if f.is_available_for_targeting()]
            if not fallback_candidates:
                return None
            candidate_flowers = fallback_candidates

        closest_flower = None
        min_dist_sq = float('inf')
        random.shuffle(candidate_flowers) 
        for flower in candidate_flowers:
            dist_sq = (self.pos[0] - flower.get_pos()[0])**2 + \
                      (self.pos[1] - flower.get_pos()[1])**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_flower = flower
        return closest_flower

    def _find_comb_to_build(self, hive_data, hive_layout_config):
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        
        possible_build_cells = []
        for y_idx in range(hive_layout_config['max_y']): 
            for x_idx in range(start_x, end_x):
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']:
                    if hive_data[x_idx, y_idx, 0] == 0:
                        possible_build_cells.append((x_idx, y_idx))
        if possible_build_cells:
            return random.choice(possible_build_cells) 
        return None

    def _find_comb_to_deposit(self, hive_data, hive_layout_config):
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        max_nectar_per_cell = hive_layout_config.get('max_nectar_per_cell', 4)
        
        possible_cells = []
        for y_idx in range(hive_layout_config['max_y']):
            for x_idx in range(start_x, end_x):
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']:
                    if hive_data[x_idx, y_idx, 0] == 1 and hive_data[x_idx, y_idx, 1] < max_nectar_per_cell:
                        possible_cells.append(((x_idx, y_idx), hive_data[x_idx, y_idx, 1]))
        
        if not possible_cells:
            return None
        
        possible_cells.sort(key=lambda item: item[1]) 
        
        if possible_cells:
            min_nectar_level = possible_cells[0][1]
            least_filled_cells_coords = [cell[0] for cell in possible_cells if cell[1] == min_nectar_level]
            if least_filled_cells_coords:
                return random.choice(least_filled_cells_coords) 
            
        return None


    def _can_build_or_deposit(self, hive_data, hive_layout_config):
        if self._find_comb_to_build(hive_data, hive_layout_config) is not None:
            return True
        if self._find_comb_to_deposit(hive_data, hive_layout_config) is not None:
            return True
        return False

    def get_pos(self):
        return self.pos

    def get_inhive(self):
        return self.inhive

# --- File Loading Functions ---
def load_map(filename, sim_params): # Added sim_params
    world_grid = None
    flowers = []
    property_config = {}
    prop_w_default, prop_h_default = 20, 15 
    hive_x_default, hive_y_default = prop_w_default // 2, prop_h_default // 2

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            prop_w = int(header[0].strip()) if len(header) > 0 and header[0].strip().isdigit() else prop_w_default
            prop_h = int(header[1].strip()) if len(header) > 1 and header[1].strip().isdigit() else prop_h_default
            hive_x = int(header[2].strip()) if len(header) > 2 and header[2].strip().isdigit() else hive_x_default
            hive_y = int(header[3].strip()) if len(header) > 3 and header[3].strip().isdigit() else hive_y_default
            
            property_config['max_x'] = prop_w
            property_config['max_y'] = prop_h
            property_config['hive_position_on_property'] = (hive_x, hive_y) 
            
            # Default to open ground (value 0)
            world_grid = np.full((prop_w, prop_h), 0, dtype=int) # CHANGED: Default to 0 for open
            
            # Read terrain grid if present, otherwise world_grid remains all 0s
            temp_terrain_rows = []
            for r_idx in range(prop_h): 
                try:
                    line_str_list = next(reader)
                except StopIteration: # Not enough lines for full terrain grid
                    print(f"Warning: Map file '{filename}' has fewer than {prop_h} terrain lines. Using default open ground for remaining.")
                    break 
                if len(line_str_list) < prop_w:
                    print(f"Warning: Terrain map line {r_idx+1} is shorter than width ({len(line_str_list)} vs {prop_w}). Padding with 0s.")
                    line_str_list.extend(['0'] * (prop_w - len(line_str_list)))
                elif len(line_str_list) > prop_w:
                    print(f"Warning: Terrain map line {r_idx+1} is longer than width ({len(line_str_list)} vs {prop_w}). Truncating.")
                    line_str_list = line_str_list[:prop_w]
                temp_terrain_rows.append([int(val.strip()) for val in line_str_list])
            
            if temp_terrain_rows: # If any terrain rows were read
                terrain_array_from_file = np.array(temp_terrain_rows) 
                if terrain_array_from_file.shape[0] == prop_h and terrain_array_from_file.shape[1] == prop_w : # Check if shape matches expected visual rows x cols
                    world_grid = terrain_array_from_file.T # Transpose for (x,y) indexing
                elif terrain_array_from_file.shape == (prop_w, prop_h) and prop_w == prop_h: # Ambiguous case for square maps
                     world_grid = terrain_array_from_file # Assume it's already (W,H) if square and matches (prop_w, prop_h)
                elif terrain_array_from_file.shape[0] > 0 : # If some rows were read but not full grid
                    print(f"Warning: Incomplete terrain grid in {filename}. Read {terrain_array_from_file.shape[0]} rows, expected {prop_h}.")
                    # Partial fill if necessary or rely on default initialized grid
                    # For now, if it's not full, we assume the default np.full above is preferred.
                    # To use partial:
                    # for r, row_data in enumerate(temp_terrain_rows):
                    #    for c, val in enumerate(row_data):
                    #        if c < prop_w: world_grid[c,r] = val


            flower_dead_duration_val = sim_params.get('flower_dead_time', 10)

            for row_list in reader: # Process remaining lines for objects
                if not row_list or not row_list[0].strip(): continue
                obj_type = row_list[0].strip().upper()
                try:
                    if obj_type == "FLOWER":
                        if len(row_list) < 7: 
                            print(f"Warning: Skipping malformed FLOWER line: {row_list}")
                            continue
                        # Flower: ID, X, Y, Name, Color (ignored), NectarCapacity
                        f_id, f_x_str, f_y_str, f_name, _, f_nectar_str = [s.strip() for s in row_list[1:7]]
                        f_x, f_y, f_nectar_capacity_from_csv = int(f_x_str), int(f_y_str), int(f_nectar_str)
                        flowers.append(Flower(f_id, (f_x, f_y), f_name, "AssignedLater", f_nectar_capacity_from_csv, flower_dead_duration_val))
                    elif obj_type == "BARRIER": 
                        if len(row_list) < 6:
                            print(f"Warning: Skipping malformed BARRIER line: {row_list}")
                            continue
                        # Barrier: type, x, y, w, h, val
                        _, b_x_str, b_y_str, b_w_str, b_h_str, b_val_str = [s.strip() for s in row_list[0:6]] 
                        b_x, b_y, b_w, b_h, b_val = int(b_x_str), int(b_y_str), int(b_w_str), int(b_h_str), int(b_val_str)
                        if 0 <= b_x < prop_w and 0 <= b_y < prop_h and \
                           b_x + b_w <= prop_w and b_y + b_h <= prop_h: 
                            world_grid[b_x : b_x + b_w, b_y : b_y + b_h] = b_val
                        else:
                            print(f"Warning: Barrier {row_list[1:]} out of bounds. Skipping.")
                    elif obj_type == "OBSTACLE": # For specific single-cell obstacles by keyword
                         if len(row_list) < 5: # OBSTACLE,id,x,y,name
                            print(f"Warning: Skipping malformed OBSTACLE line: {row_list}")
                            continue
                         o_id_str, o_x_str, o_y_str, o_name_str = [s.strip() for s in row_list[1:5]]
                         o_x, o_y = int(o_x_str), int(o_y_str)
                         if 0 <= o_x < prop_w and 0 <= o_y < prop_h:
                             world_grid[o_x, o_y] = 7 # Use 7 for gray obstacle
                         else:
                            print(f"Warning: Obstacle at ({o_x}, {o_y}) out of bounds. Skipping.")
                    elif obj_type == "WATER": # For specific single-cell water by keyword
                         if len(row_list) < 5: # WATER,id,x,y,name
                            print(f"Warning: Skipping malformed WATER line: {row_list}")
                            continue
                         w_id_str, w_x_str, w_y_str, w_name_str = [s.strip() for s in row_list[1:5]]
                         w_x, w_y = int(w_x_str), int(w_y_str)
                         if 0 <= w_x < prop_w and 0 <= w_y < prop_h:
                            world_grid[w_x, w_y] = 1 # Use 1 for blue water (tab20c[1] can be blueish)
                         else:
                            print(f"Warning: Water at ({w_x}, {w_y}) out of bounds. Skipping.")
                except ValueError as e:
                    print(f"Warning: Could not parse object line values in '{filename}': {row_list}. Error: {e}. Skipping.")
                except IndexError as e: 
                    print(f"Warning: Malformed object line (not enough elements) in '{filename}': {row_list}. Error: {e}. Skipping.")
        
        except StopIteration: # End of file reached
            if world_grid is None and not temp_terrain_rows : # Only an error if we didn't even read the header properly
                 print(f"Error: CSV file '{filename}' seems to be empty or missing header.")
                 raise ValueError(f"CSV file '{filename}' is empty or malformed.")
            # If StopIteration occurs after grid or during objects, it's potentially fine.
            print(f"Note: Reached end of CSV while parsing '{filename}'.")
        except ValueError as ve: 
            print(f"Error converting critical data (header/terrain) in map file '{filename}': {ve}")
            raise
        except Exception as e:
            print(f"General error loading map file '{filename}': {e}")
            import traceback
            traceback.print_exc()
            raise
            
    if world_grid is None: # Should be initialized by np.full earlier
        print(f"Critical Error: World grid was not initialized for {filename}.")
        # Fallback to ensure property_config has defaults if header parsing failed badly
        property_config.setdefault('max_x', prop_w_default)
        property_config.setdefault('max_y', prop_h_default)
        property_config.setdefault('hive_position_on_property', (hive_x_default, hive_y_default))
        world_grid = np.full((property_config['max_x'], property_config['max_y']), 0, dtype=int)


    # Assign plot colors to flowers AFTER all flowers are loaded
    predefined_plot_colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
                              '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', 
                              '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', 
                              '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9']
    random.shuffle(predefined_plot_colors)
    for i, flower_obj in enumerate(flowers):
        flower_obj.plot_color = predefined_plot_colors[i % len(predefined_plot_colors)]


    print(f"Loaded map: Dimensions ({property_config.get('max_x', 'N/A')}x{property_config.get('max_y', 'N/A')}), Hive Entrance @{property_config.get('hive_position_on_property', 'N/A')}, {len(flowers)} flowers.")
    return world_grid, flowers, property_config

def load_parameters(filename):
    params = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                key = row[0].strip()
                value_str = row[1].strip()
                if '#' in value_str:
                    value_str = value_str.split('#', 1)[0].strip()
                
                try:
                    if value_str.lower() == 'true': params[key] = True
                    elif value_str.lower() == 'false': params[key] = False
                    elif '.' in value_str and value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
                        params[key] = float(value_str)
                    elif value_str.lstrip('-').isdigit(): 
                        params[key] = int(value_str)
                    else:
                        params[key] = value_str
                except ValueError:
                    params[key] = value_str 
    params.setdefault('num_bees', 5)
    params.setdefault('simlength', 100)
    params.setdefault('hive_width', 10) 
    params.setdefault('hive_height', 8)  
    params.setdefault('comb_stripe_width', 3)
    params.setdefault('max_nectar_per_cell', 4) 
    params.setdefault('bee_max_nectar_carry', 1)
    params.setdefault('flower_regen_rate', 1)
    params.setdefault('bee_avoid_empty_duration', 20)
    params.setdefault('flower_nectar_capacity_default', 5) 
    params.setdefault('flower_dead_time', 10)
    params.setdefault('interactive_pause', 0.1)
    params.setdefault('bee_max_stuck_time', 5)
    params.setdefault('tree_locations', "") # For new tree parameter

    hive_w = int(params.get('hive_width', 10)) 
    hive_h = int(params.get('hive_height', 8))
    params['hive_width'] = hive_w
    params['hive_height'] = hive_h
    
    default_internal_x = 0
    default_internal_y = hive_h - 1 if hive_h > 0 else 0

    params['hive_exit_cell_inside_x'] = int(params.get('hive_exit_cell_inside_x', default_internal_x))
    params['hive_exit_cell_inside_y'] = int(params.get('hive_exit_cell_inside_y', default_internal_y))
    params['hive_entry_cell_inside_x'] = int(params.get('hive_entry_cell_inside_x', default_internal_x))
    params['hive_entry_cell_inside_y'] = int(params.get('hive_entry_cell_inside_y', default_internal_y))

    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    
    # Parse tree_locations
    params['tree_locations_list'] = parse_coord_list_param(str(params.get('tree_locations', "")), "")


    print(f"Loaded parameters: {params}")
    return params

# --- Plotting Functions ---
def plot_hive(hive_data, bees_in_hive, ax, hive_layout_config):
    ax.clear()
    max_nectar_val = hive_layout_config.get('max_nectar_per_cell', 4) 

    val_unbuilt_in_stripe = max_nectar_val + 1
    val_outside_stripe = max_nectar_val + 2
    
    hive_plot_array = np.full((hive_layout_config['max_x'], hive_layout_config['max_y']), float(val_outside_stripe)) 
    
    comb_width = hive_layout_config.get('comb_stripe_width', 3)
    stripe_center_x = hive_layout_config['max_x'] // 2
    start_x = max(0, stripe_center_x - comb_width // 2)
    end_x = min(hive_layout_config['max_x'], start_x + comb_width)

    for r_idx in range(hive_layout_config['max_x']):
        for c_idx in range(hive_layout_config['max_y']):
            is_in_stripe = (start_x <= r_idx < end_x)
            if is_in_stripe:
                if hive_data[r_idx, c_idx, 0] == 1: 
                    nectar_level = hive_data[r_idx, c_idx, 1] 
                    hive_plot_array[r_idx, c_idx] = nectar_level 
                else: 
                    hive_plot_array[r_idx, c_idx] = float(val_unbuilt_in_stripe)
            
    num_nectar_shades = max_nectar_val + 1 
    # Ensure enough colors for the colormap segments
    try:
        base_cmap = plt.cm.get_cmap('Oranges', num_nectar_shades + 10) # Request more segments for better gradient
        colors = [base_cmap(i * (1.0 / (num_nectar_shades -1 ))) for i in range(num_nectar_shades)]
    except Exception: # Fallback if above fails (e.g. num_nectar_shades is 1)
        base_cmap = plt.cm.get_cmap('Oranges')
        colors = [base_cmap(i / (num_nectar_shades -1 if num_nectar_shades >1 else 1) ) for i in range(num_nectar_shades)]


    colors.append((0.85, 0.85, 0.85, 1))  # Light grey for UnbuiltInStripe
    colors.append((0.6, 0.4, 0.2, 1))  # Darker brown for OutsideStripe (background)
    
    custom_cmap = ListedColormap(colors)
    bounds = list(np.arange(0, max_nectar_val + 3, 1))                                                 
    norm = BoundaryNorm(bounds, custom_cmap.N)

    ax.imshow(hive_plot_array.T, origin="lower", cmap=custom_cmap, norm=norm)
    
    xvalues = [b.get_pos()[0] for b in bees_in_hive if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in bees_in_hive if b.get_inhive()]
    if xvalues:
        ax.scatter(xvalues, yvalues, c='black', marker='h', s=40, label='Bees')
    ax.set_title(f'Bee Hive (Nectar: 0-{max_nectar_val})')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, hive_layout_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, hive_layout_config['max_y'] - 0.5)
    if bees_in_hive: ax.legend(loc='upper right', fontsize='small')

def plot_property(property_map_data, flowers_list, bees_on_property, property_config, ax, tree_locations): # Added tree_locations
    ax.clear()
    
    # Define property terrain color mapping
    # 0: Open/Passable (Green)
    # 1: Water (Blue)
    # 7: Obstacle/Rock (Gray)
    # Other values: from tab20c or default
    
    # Create a custom colormap for property
    # Colors based on tab20c, but we explicitly set some
    prop_cmap_colors = plt.cm.get_cmap('tab20c', 20) 
    prop_colors_list = prop_cmap_colors(np.arange(prop_cmap_colors.N)).tolist()
    
    # Assuming property_map_data uses 0 for open/passable ground which should be green
    prop_colors_list[0] = [0.6, 0.9, 0.6, 1.0]  # Light Green for value 0 (open ground)
    prop_colors_list[1] = [0.2, 0.5, 0.8, 1.0]  # Blue for value 1 (Water, was 0 before)
    prop_colors_list[2] = [0.6, 0.9, 0.6, 1.0]  # Green for value 2 (Open Grass)
    # Value 7 for rock/gray obstacle
    if len(prop_colors_list) > 7:
        prop_colors_list[7] = [0.5, 0.5, 0.5, 1.0]  # Gray for value 7 (Rock Obstacle)
    # For Water from CSV (value 1) vs general obstacles from CSV (value 7)
    # Ensure map1.csv uses these values if defined by keywords, or in grid:
    # Passable = 0 (will be light green)
    # Water = 1 (will be blue)
    # Rocks/Generic Obstacles = 7 (will be gray)

    custom_prop_cmap = ListedColormap(prop_colors_list)
    
    ax.imshow(property_map_data.T, origin="lower", cmap=custom_prop_cmap, vmin=0, vmax=19) # Use the custom map
    ax.set_facecolor('lightgreen') # Fallback background for areas outside map_data if not covering fully

    flower_x = [f.get_pos()[0] for f in flowers_list]
    flower_y = [f.get_pos()[1] for f in flowers_list]
    
    flower_plot_colors = []
    for f in flowers_list:
        if f.state == 'DEAD':
            flower_plot_colors.append('dimgray') # Darker grey for dead flowers
        else:
            flower_plot_colors.append(f.plot_color if f.plot_color else 'magenta') # Use assigned plot_color
    
    if flower_x:
        ax.scatter(flower_x, flower_y, c=flower_plot_colors, marker='P', s=80, label='Flowers', edgecolors='black', alpha=0.9, zorder=10)

    hive_pos_prop = property_config['hive_position_on_property']
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='gold', marker='H', s=150, edgecolors='black', label='Hive Entrance', zorder=10)

    if tree_locations: # tree_locations is a set of (x,y) tuples
        tree_x_coords = [tx for tx, ty in tree_locations]
        tree_y_coords = [ty for tx, ty in tree_locations]
        if tree_x_coords:
            ax.scatter(tree_x_coords, tree_y_coords, c='#556B2F', marker='^', s=160, label='Trees (Param)', edgecolors='black', zorder=5)


    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()]
    bee_y = [b.get_pos()[1] for b in bees_on_property if not b.get_inhive()]
    if bee_x:
      ax.scatter(bee_x, bee_y, c='black', marker='h', s=50, label='Bees', zorder=15)

    ax.set_title('Property')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, property_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, property_config['max_y'] - 0.5)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc='upper right', fontsize='small')


def plot_flower_nectar(flowers_list, ax, default_max_nectar):
    ax.clear()
    if not flowers_list:
        ax.set_title('Flower Nectar Levels')
        ax.text(0.5, 0.5, "No flowers defined", ha='center', va='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    flower_ids_names = [f"{f.ID}\n({f.name})" for f in flowers_list]
    nectar_levels = [f.current_nectar for f in flowers_list]
    
    max_cap = default_max_nectar 
    if flowers_list:
        all_capacities = [f.nectar_capacity for f in flowers_list if f.nectar_capacity is not None]
        if all_capacities:
            max_cap = max(all_capacities)
    if max_cap == 0: max_cap = 1

    bar_colors = ['mediumseagreen' if f.state == 'ALIVE' else 'lightcoral' for f in flowers_list]
    bars = ax.bar(flower_ids_names, nectar_levels, color=bar_colors)
    ax.set_ylabel('Nectar Units')
    ax.set_title('Flower Nectar Levels (Green=Alive, Red=Dead)')
    ax.set_ylim(0, max_cap + 1)
    ax.tick_params(axis='x', labelrotation=30, labelsize=8) 

    for bar_idx, bar in enumerate(bars):
        yval = bar.get_height()
        text_offset = 0.05 * (max_cap + 1) if max_cap > 0 else 0.05
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + text_offset , 
                f'{yval}/{flowers_list[bar_idx].nectar_capacity}', 
                ha='center', va='bottom', fontsize=7)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

# --- Main Simulation Logic ---
def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False):
    hiveX, hiveY = sim_params['hive_width'], sim_params['hive_height']
    max_nectar_in_comb = sim_params.get('max_nectar_per_cell', 4) 
    hive_data = np.zeros((hiveX, hiveY, 2), dtype=int)
    hive_layout_config = {
        'max_x': hiveX, 'max_y': hiveY,
        'comb_stripe_width': sim_params['comb_stripe_width'],
        'max_nectar_per_cell': max_nectar_in_comb, 
        'hive_exit_cell_inside': sim_params['hive_exit_cell_inside'], 
        'hive_entry_cell_inside': sim_params['hive_entry_cell_inside'] 
    }
    
    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside']
    if not (0 <= initial_bee_pos_in_hive[0] < hiveX and 0 <= initial_bee_pos_in_hive[1] < hiveY):
        print(f"Warning: Initial bee position {initial_bee_pos_in_hive} is outside hive dimensions {hiveX}x{hiveY}. Resetting to center or (0,0).")
        if hiveX > 0 and hiveY > 0: 
            initial_bee_pos_in_hive = (min(hiveX-1, hiveX//2) , min(hiveY-1, hiveY//2))
        else: # Should not happen if hive_width/height are > 0
            initial_bee_pos_in_hive = (0,0)


    all_bees = [
        Bee(f"B{i+1}", initial_bee_pos_in_hive, property_config['hive_position_on_property'], 
            sim_params['bee_max_nectar_carry'], 
            sim_params.get('bee_avoid_empty_duration', 20),
            sim_params.get('bee_max_stuck_time', 5))
        for i in range(sim_params['num_bees'])
    ]

    tree_locs_set = set(sim_params.get('tree_locations_list', [])) # Get tree locations

    fig_interactive = None 
    axes_dict_interactive = None 

    if interactive_mode:
        plt.ion()
        fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10))
        axes_dict_interactive = {'hive': axes_array_interactive[0,0], 
                                 'property': axes_array_interactive[0,1], 
                                 'nectar': axes_array_interactive[1,0]}
        axes_array_interactive[1,1].axis('off')

    for t in range(sim_params['simlength']):
        print(f"\n--- Timestep {t+1}/{sim_params['simlength']} ---")

        random.shuffle(all_bees) 

        for i, current_bee_obj in enumerate(all_bees):
            other_bees_details = [] 
            for j, other_b in enumerate(all_bees):
                if i != j:
                    other_bees_details.append({
                        'pos': other_b.get_pos(), 
                        'state': other_b.state, 
                        'id': other_b.ID,
                        'inhive': other_b.get_inhive()
                    })
            
            current_bee_obj.step_change(
                property_map_data, 
                flowers_list, 
                hive_data, 
                hive_layout_config, 
                property_config, 
                t, 
                other_bees_details,
                tree_locs_set # Pass tree locations
            )

        for flower in flowers_list:
            flower.regenerate_nectar(rate=sim_params.get('flower_regen_rate',1))

        if interactive_mode:
            if fig_interactive is None or not plt.fignum_exists(fig_interactive.number): 
                fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10))
                axes_dict_interactive = {'hive': axes_array_interactive[0,0], 
                                         'property': axes_array_interactive[0,1], 
                                         'nectar': axes_array_interactive[1,0]}
                axes_array_interactive[1,1].axis('off')
                plt.ion()

            axes_dict_interactive['hive'].clear()
            axes_dict_interactive['property'].clear()
            axes_dict_interactive['nectar'].clear()
            
            fig_interactive.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')

            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, axes_dict_interactive['hive'], hive_layout_config)

            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes_dict_interactive['property'], tree_locs_set) # Pass trees
            
            plot_flower_nectar(flowers_list, axes_dict_interactive['nectar'], sim_params.get('flower_nectar_capacity_default', 5))

            fig_interactive.tight_layout(rect=[0, 0, 1, 0.96])
            fig_interactive.canvas.draw()
            fig_interactive.canvas.flush_events()
            try:
                pause_duration = float(sim_params.get('interactive_pause', 0.1))
            except ValueError:
                pause_duration = 0.1 
            plt.pause(pause_duration)


        elif t == sim_params['simlength'] - 1: # Batch mode, save final frame
            batch_fig, batch_axes_array = plt.subplots(2, 2, figsize=(16, 10))
            current_batch_axes = {'hive': batch_axes_array[0,0], 
                                  'property': batch_axes_array[0,1], 
                                  'nectar': batch_axes_array[1,0]}
            batch_axes_array[1,1].axis('off')
            batch_fig.suptitle(f"Bee World - Final State - Timestep: {t+1}", fontsize=16, fontweight='bold')
            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, current_batch_axes['hive'], hive_layout_config)
            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, current_batch_axes['property'], tree_locs_set) # Pass trees
            plot_flower_nectar(flowers_list, current_batch_axes['nectar'], sim_params.get('flower_nectar_capacity_default', 5))
            batch_fig.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig('beeworld_simulation_end.png')
            print("Saved final simulation state to beeworld_simulation_end.png")
            plt.close(batch_fig)

    if interactive_mode and fig_interactive and plt.fignum_exists(fig_interactive.number):
        print("Simulation finished. Close the plot window to exit.")
        plt.ioff()
        plt.show()
    elif not interactive_mode:
        print("Batch simulation finished.")
    else:
        print("Simulation finished (no plot shown or plot was closed).")

# --- Argument Parsing and Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Bee World Simulation")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode (step-by-step plotting)")
    parser.add_argument("-f", "--mapfile", type=str, default="map1.csv",
                        help="Path to the CSV file defining the property map (default: map1.csv)")
    parser.add_argument("-p", "--paramfile", type=str, default="para1.csv",
                        help="Path to the CSV file defining simulation parameters (default: para1.csv)")
    args = parser.parse_args()

    try:
        sim_params = load_parameters(args.paramfile)
        # Ensure sim_params is passed to load_map for flower_dead_duration and tree_locations
        world_data, flowers_data, property_conf = load_map(args.mapfile, sim_params) 
    except FileNotFoundError as e:
        print(f"Error: Required file not found. {e}")
        print("Please ensure map and parameter files exist at the specified paths or in the current directory if using defaults.")
        return
    except Exception as e:
        print(f"An error occurred during setup: {e}")
        import traceback
        traceback.print_exc() 
        return

    if args.interactive:
        print(f"Running in INTERACTIVE mode with map: {args.mapfile} and params: {args.paramfile}")
    else:
        print(f"Running in BATCH mode with map: {args.mapfile} and params: {args.paramfile}")

    run_simulation(sim_params, world_data, flowers_data, property_conf, interactive_mode=args.interactive)

if __name__ == "__main__":
    main()