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
#
import random
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt

# --- Flower Class ---
class Flower():
    def __init__(self, ID, pos, name, color, nectar_capacity=5, dead_duration=10): # Added dead_duration
        self.ID = ID
        self.pos = pos # (x,y)
        self.name = name
        self.color = color
        self.nectar_capacity = nectar_capacity
        self.current_nectar = nectar_capacity
        self.state = 'ALIVE' # States: 'ALIVE', 'DEAD'
        self.regeneration_cooldown = 0 # Timer for how long it stays dead or time until next regen tick
        self.dead_duration = dead_duration # Configurable time to stay dead

    def get_pos(self):
        return self.pos

    def get_nectar(self):
        return self.current_nectar

    def take_nectar(self, amount=1):
        taken = min(amount, self.current_nectar)
        self.current_nectar -= taken
        if self.current_nectar == 0 and self.state == 'ALIVE':
            self.state = 'DEAD'
            self.regeneration_cooldown = self.dead_duration
            # print(f"Flower {self.ID} ({self.name}) is now DEAD, cooldown for {self.dead_duration} steps.")
        return taken

    def regenerate_nectar(self, rate=1):
        if self.state == 'DEAD':
            if self.regeneration_cooldown > 0:
                self.regeneration_cooldown -= 1
            else: # Cooldown finished
                self.state = 'ALIVE'
                # print(f"Flower {self.ID} ({self.name}) is now ALIVE and can regenerate.")
                # Allow it to start regenerating in the same step if state becomes ALIVE
                if self.current_nectar < self.nectar_capacity: # Should be 0 at this point
                    self.current_nectar = min(self.nectar_capacity, self.current_nectar + rate)
                    # if self.current_nectar > 0:
                        # print(f"Flower {self.ID} ({self.name}) regenerated {rate} nectar, now has {self.current_nectar}.")
        elif self.state == 'ALIVE':
            if self.current_nectar < self.nectar_capacity:
                old_nectar = self.current_nectar
                self.current_nectar = min(self.nectar_capacity, self.current_nectar + rate)
                # if self.current_nectar > old_nectar:
                #    print(f"Flower {self.ID} ({self.name}) regenerated {self.current_nectar - old_nectar} nectar, now has {self.current_nectar}.")

    def is_available_for_targeting(self):
        """Returns True if the flower is alive and has nectar."""
        return self.state == 'ALIVE' and self.current_nectar > 0

# --- Bee Class ---
class Bee():
    def __init__(self, ID, initial_pos, hive_entrance_property_pos, max_nectar_carry=1, avoid_empty_duration=20):
        self.ID = ID
        self.pos = initial_pos # (x,y)
        self.hive_entrance_property_pos = hive_entrance_property_pos
        self.age = 0
        self.inhive = True # Starts in hive
        self.state = 'IDLE_IN_HIVE'
        # States: IDLE_IN_HIVE, MOVING_TO_HIVE_EXIT, SEEKING_FLOWER, MOVING_TO_FLOWER,
        #         COLLECTING_NECTAR, RETURNING_TO_HIVE_ENTRANCE, MOVING_TO_HIVE_ENTRY_POINT,
        #         BUILDING_COMB, MOVING_TO_COMB_BUILD_SITE,
        #         DEPOSITING_NECTAR, MOVING_TO_COMB_DEPOSIT_SITE, IDLE_ON_PROPERTY

        self.nectar_carried = 0
        self.max_nectar_carry = max_nectar_carry
        self.current_target_pos = None
        self.current_target_object = None
        self.path = []

        self.recently_emptied_flowers = {} # flower.ID: timestamp_when_it_was_found_empty
        self.avoid_empty_duration = avoid_empty_duration


    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config, current_timestep):
        self.age += 1
        # print(f"DEBUG Bee {self.ID}: State={self.state}, Pos={self.pos}, Nectar={self.nectar_carried}, Target={self.current_target_pos}, AvoidList: {self.recently_emptied_flowers}")

        if self.state == 'IDLE_IN_HIVE':
            if self.nectar_carried >= 1 and self._can_build_or_deposit(hive_data, hive_layout_config):
                comb_build_target = self._find_comb_to_build(hive_data, hive_layout_config)
                if comb_build_target:
                    self.current_target_pos = comb_build_target
                    self.state = 'MOVING_TO_COMB_BUILD_SITE'
                else:
                    comb_deposit_target = self._find_comb_to_deposit(hive_data, hive_layout_config)
                    if comb_deposit_target:
                        self.current_target_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE'
                    elif self.nectar_carried < self.max_nectar_carry:
                        self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                        self.state = 'MOVING_TO_HIVE_EXIT'
            elif self.nectar_carried < self.max_nectar_carry:
                self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                self.state = 'MOVING_TO_HIVE_EXIT'

        elif self.state == 'MOVING_TO_HIVE_EXIT':
            if self.pos == self.current_target_pos:
                self.inhive = False
                self.pos = self.hive_entrance_property_pos
                self.state = 'SEEKING_FLOWER'
                self.current_target_pos = None
            else:
                self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], is_in_hive=True)

        elif self.state == 'SEEKING_FLOWER':
            self.current_target_object = self._find_closest_flower_with_nectar(flowers_list, current_timestep)
            if self.current_target_object:
                self.current_target_pos = self.current_target_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
            else:
                self.state = 'IDLE_ON_PROPERTY'
                self.current_target_pos = None

        elif self.state == 'MOVING_TO_FLOWER':
            if self.current_target_object is None or not self.current_target_object.is_available_for_targeting(): # Check if target became invalid/empty/dead
                if self.current_target_object:
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
                self.state = 'SEEKING_FLOWER'
                self.current_target_pos = None
                self.current_target_object = None
            elif self.pos == self.current_target_pos:
                self.state = 'COLLECTING_NECTAR'
            else:
                self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], is_in_hive=False)

        elif self.state == 'COLLECTING_NECTAR':
            if self.current_target_object and self.current_target_object.is_available_for_targeting() and self.nectar_carried < self.max_nectar_carry:
                amount_to_take = self.max_nectar_carry - self.nectar_carried
                taken = self.current_target_object.take_nectar(amount_to_take) # take_nectar might set flower to DEAD
                self.nectar_carried += taken
            
            # Finished collecting if full, flower is empty/dead, or target object is gone
            if self.nectar_carried >= self.max_nectar_carry or \
               not self.current_target_object or \
               (self.current_target_object and not self.current_target_object.is_available_for_targeting()):
                if self.current_target_object and not self.current_target_object.is_available_for_targeting(): # Specifically if it became unavailable
                    self.recently_emptied_flowers[self.current_target_object.ID] = current_timestep
                self.current_target_pos = self.hive_entrance_property_pos
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_target_object = None

        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE':
            if self.pos == self.current_target_pos:
                self.inhive = True
                self.pos = hive_layout_config['hive_entry_cell_inside']
                self.state = 'IDLE_IN_HIVE'
                self.current_target_pos = None
            else:
                self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], is_in_hive=False)

        elif self.state == 'MOVING_TO_COMB_BUILD_SITE':
            if self.pos == self.current_target_pos:
                self.state = 'BUILDING_COMB'
            else:
                self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], is_in_hive=True)

        elif self.state == 'BUILDING_COMB':
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
            else:
                self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], is_in_hive=True)

        elif self.state == 'DEPOSITING_NECTAR':
            x,y = self.pos
            if self.nectar_carried > 0 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x,y,0] == 1:
                can_deposit = hive_layout_config['max_nectar_per_cell'] - hive_data[x,y,1]
                deposited_amount = min(self.nectar_carried, can_deposit)
                if deposited_amount > 0:
                    hive_data[x,y,1] += deposited_amount
                    self.nectar_carried -= deposited_amount
                    print(f"Bee {self.ID} deposited {deposited_amount} nectar at {self.pos}. Cell now has {hive_data[x,y,1]}")
            self.state = 'IDLE_IN_HIVE'
            self.current_target_pos = None

        elif self.state == 'IDLE_ON_PROPERTY':
            if self.age % 20 == 0 :
                 self.current_target_pos = self.hive_entrance_property_pos
                 self.state = 'RETURNING_TO_HIVE_ENTRANCE'
            else: # Simple random move if truly idle on property
                self._move_randomly(property_map_data, property_config['max_x'], property_config['max_y'])


    def _move_towards_target(self, map_data, maxX, maxY, is_in_hive=False):
        if self.current_target_pos is None:
            return

        dx = self.current_target_pos[0] - self.pos[0]
        dy = self.current_target_pos[1] - self.pos[1]
        move = [0,0]
        if dx > 0: move[0] = 1
        elif dx < 0: move[0] = -1
        if dy > 0: move[1] = 1
        elif dy < 0: move[1] = -1

        if move == [0,0] and self.pos == self.current_target_pos:
            return

        newX = self.pos[0] + move[0]
        newY = self.pos[1] + move[1]

        if 0 <= newX < maxX and 0 <= newY < maxY:
            if not is_in_hive and map_data is not None:
                if map_data[newX, newY] != 0: 
                    if move[0] != 0 and move[1] != 0: 
                        temp_newX_x_only = self.pos[0] + move[0]
                        temp_newY_y_only = self.pos[1] + move[1]
                        
                        can_move_x = False
                        if 0 <= temp_newX_x_only < maxX and map_data[temp_newX_x_only, self.pos[1]] == 0:
                            can_move_x = True
                        
                        can_move_y = False
                        if 0 <= temp_newY_y_only < maxY and map_data[self.pos[0], temp_newY_y_only] == 0:
                            can_move_y = True

                        if can_move_x and can_move_y: 
                            if random.choice([True, False]):
                                self.pos = (temp_newX_x_only, self.pos[1])
                            else:
                                self.pos = (self.pos[0], temp_newY_y_only)
                        elif can_move_x:
                            self.pos = (temp_newX_x_only, self.pos[1])
                        elif can_move_y:
                            self.pos = (self.pos[0], temp_newY_y_only)
                        return
                    else: 
                        return 
            self.pos = (newX, newY)

    def _move_randomly(self, map_data, maxX, maxY):
        validmoves = [(0,1), (1,0), (0,-1), (-1,0)]
        random.shuffle(validmoves)
        for move in validmoves:
            newX = self.pos[0] + move[0]
            newY = self.pos[1] + move[1]
            if 0 <= newX < maxX and 0 <= newY < maxY:
                if map_data is None or map_data[newX, newY] == 0:
                    self.pos = (newX, newY)
                    return
    
    def _find_closest_flower_with_nectar(self, flowers_list, current_timestep):
        to_remove = [fid for fid, ts in self.recently_emptied_flowers.items() if current_timestep - ts > self.avoid_empty_duration]
        for fid in to_remove:
            if fid in self.recently_emptied_flowers: # Check if key still exists before deleting
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
        for y_idx in range(hive_layout_config['max_y']):
            for x_idx in range(start_x, end_x):
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']: # Boundary check
                    if hive_data[x_idx, y_idx, 0] == 0:
                        return (x_idx, y_idx)
        return None

    def _find_comb_to_deposit(self, hive_data, hive_layout_config):
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        max_nectar_per_cell = hive_layout_config.get('max_nectar_per_cell', 5)
        for y_idx in range(hive_layout_config['max_y']):
            for x_idx in range(start_x, end_x):
                if 0 <= x_idx < hive_layout_config['max_x'] and 0 <= y_idx < hive_layout_config['max_y']: # Boundary check
                    if hive_data[x_idx, y_idx, 0] == 1 and hive_data[x_idx, y_idx, 1] < max_nectar_per_cell:
                        return (x_idx, y_idx)
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
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            prop_w, prop_h = int(header[0]), int(header[1])
            property_config['max_x'] = prop_w
            property_config['max_y'] = prop_h
            property_config['hive_position_on_property'] = (int(header[2]), int(header[3]))
            world_grid = np.zeros((prop_w, prop_h), dtype=int)
            
            temp_terrain_rows = []
            for _ in range(prop_h):
                line_str_list = next(reader) # Correctly use the variable that holds the list of strings
                temp_terrain_rows.append([int(val) for val in line_str_list])
            
            terrain_array_from_file = np.array(temp_terrain_rows)
            if terrain_array_from_file.shape == (prop_h, prop_w):
                 world_grid = terrain_array_from_file.T # Transpose to make grid[x,y]
            else:
                raise ValueError(f"Terrain data shape mismatch. Expected ({prop_h},{prop_w}), got {terrain_array_from_file.shape}")

            flower_dead_duration_val = sim_params.get('flower_dead_time', 10) # Get from sim_params

            for row_list in reader:
                if not row_list: continue
                obj_type = row_list[0].upper()
                if obj_type == "FLOWER":
                    if len(row_list) < 7:
                        print(f"Warning: Skipping malformed FLOWER line: {row_list}")
                        continue
                    _, f_id, f_x, f_y, f_name, f_color, f_nectar_str = row_list[0:7] # Ensure correct slicing
                    f_x, f_y, f_nectar = int(f_x), int(f_y), int(f_nectar_str)
                    flowers.append(Flower(f_id, (f_x, f_y), f_name, f_color, f_nectar, flower_dead_duration_val)) # Pass dead_duration
                elif obj_type == "BARRIER": 
                    if len(row_list) < 6:
                        print(f"Warning: Skipping malformed BARRIER line: {row_list}")
                        continue
                    _, b_x, b_y, b_w, b_h, b_val_str = row_list[0:6]
                    b_x, b_y, b_w, b_h, b_val = int(b_x), int(b_y), int(b_w), int(b_h), int(b_val_str)
                    world_grid[b_x : b_x + b_w, b_y : b_y + b_h] = b_val
                elif obj_type == "OBSTACLE": 
                     if len(row_list) < 5: # OBSTACLE,id,x,y,name
                        print(f"Warning: Skipping malformed OBSTACLE line: {row_list}")
                        continue
                     _, _, o_x, o_y, _ = row_list[0:5]
                     world_grid[int(o_x), int(o_y)] = 1 
                elif obj_type == "WATER": 
                     if len(row_list) < 5: # WATER,id,x,y,name
                        print(f"Warning: Skipping malformed WATER line: {row_list}")
                        continue
                     _, _, w_x, w_y, _ = row_list[0:5]
                     world_grid[int(w_x), int(w_y)] = 2
        except Exception as e:
            print(f"Error loading map file '{filename}': {e}")
            raise
    print(f"Loaded map: Dimensions ({property_config['max_x']}x{property_config['max_y']}), Hive Entrance @{property_config['hive_position_on_property']}, {len(flowers)} flowers.")
    return world_grid, flowers, property_config

def load_parameters(filename):
    params = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                key = row[0].strip()
                value_str = row[1].strip()
                if '#' in value_str: # Remove comments from value string
                    value_str = value_str.split('#', 1)[0].strip()
                
                try:
                    if '.' in value_str and value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
                        params[key] = float(value_str)
                    elif value_str.lstrip('-').isdigit():
                        params[key] = int(value_str)
                    else:
                        params[key] = value_str
                except ValueError:
                    params[key] = value_str
    params.setdefault('num_bees', 5)
    params.setdefault('simlength', 100)
    params.setdefault('hive_width', 20)
    params.setdefault('hive_height', 15)
    params.setdefault('comb_stripe_width', 3)
    params.setdefault('max_nectar_per_cell', 5)
    params.setdefault('bee_max_nectar_carry', 1)
    params.setdefault('flower_regen_rate', 1)
    params.setdefault('bee_avoid_empty_duration', 20)
    params.setdefault('flower_nectar_capacity_default', 5)
    params.setdefault('flower_dead_time', 10) # Duration flower stays dead
    params.setdefault('interactive_pause', 0.1)


    params['hive_exit_cell_inside_x'] = params.get('hive_exit_cell_inside_x', params['hive_width'] // 2)
    params['hive_exit_cell_inside_y'] = params.get('hive_exit_cell_inside_y', 0)
    params['hive_entry_cell_inside_x'] = params.get('hive_entry_cell_inside_x', params['hive_width'] // 2)
    params['hive_entry_cell_inside_y'] = params.get('hive_entry_cell_inside_y', 0)

    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    print(f"Loaded parameters: {params}")
    return params

# --- Plotting Functions ---
def plot_hive(hive_data, bees_in_hive, ax, hive_layout_config):
    ax.clear()
    hive_plot_array = np.full((hive_layout_config['max_x'], hive_layout_config['max_y']), 9.0)
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
                    hive_plot_array[r_idx, c_idx] = min(nectar_level, 5) 
                else:
                    hive_plot_array[r_idx, c_idx] = 8 
    ax.imshow(hive_plot_array.T, origin="lower", cmap='YlOrBr', vmin=0, vmax=9)
    xvalues = [b.get_pos()[0] for b in bees_in_hive if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in bees_in_hive if b.get_inhive()]
    if xvalues:
        ax.scatter(xvalues, yvalues, c='black', marker='h', s=40, label='Bees')
    ax.set_title('Bee Hive')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, hive_layout_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, hive_layout_config['max_y'] - 0.5)
    if bees_in_hive: ax.legend(loc='upper right', fontsize='small')

def plot_property(property_map_data, flowers_list, bees_on_property, property_config, ax):
    ax.clear()
    ax.imshow(property_map_data.T, origin="lower", cmap='tab20c', vmin=0, vmax=19)
    
    flower_x = [f.get_pos()[0] for f in flowers_list]
    flower_y = [f.get_pos()[1] for f in flowers_list]
    flower_colors_map = {'Red': 'red', 'Blue': 'blue', 'Yellow': 'yellow', 'Purple': 'purple', 'Pink': 'pink', 'White':'lightgray', 'Orange':'orange', 'Green':'green'}
    flower_plot_colors = []
    for f in flowers_list:
        if f.state == 'DEAD':
            flower_plot_colors.append('grey') # Show dead flowers as grey
        else:
            flower_plot_colors.append(flower_colors_map.get(f.color, 'magenta'))
    
    if flower_x:
        ax.scatter(flower_x, flower_y, c=flower_plot_colors, marker='P', s=80, label='Flowers', edgecolors='black', alpha=0.7)

    hive_pos_prop = property_config['hive_position_on_property']
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='gold', marker='H', s=150, edgecolors='black', label='Hive Entrance')

    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()]
    bee_y = [b.get_pos()[1] for b in bees_on_property if not b.get_inhive()]
    if bee_x:
      ax.scatter(bee_x, bee_y, c='black', marker='h', s=50, label='Bees')

    ax.set_title('Property')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xlim(-0.5, property_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, property_config['max_y'] - 0.5)
    if flower_x or bee_x : ax.legend(loc='upper right', fontsize='small')

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
    
    max_cap = 0
    if flowers_list:
        max_cap = max(f.nectar_capacity for f in flowers_list) if any(f.nectar_capacity for f in flowers_list) else default_max_nectar
    if max_cap == 0: max_cap = 1

    bar_colors = ['mediumseagreen' if f.state == 'ALIVE' else 'lightcoral' for f in flowers_list]
    bars = ax.bar(flower_ids_names, nectar_levels, color=bar_colors)
    ax.set_ylabel('Nectar Units')
    ax.set_title('Flower Nectar Levels (Green=Alive, Red=Dead)')
    ax.set_ylim(0, max_cap + 1)
    ax.tick_params(axis='x', labelrotation=30, labelsize=8)

    for bar_idx, bar in enumerate(bars):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02 * max_cap,
                f'{yval}/{flowers_list[bar_idx].nectar_capacity}', 
                ha='center', va='bottom', fontsize=7)
    ax.grid(axis='y', linestyle='--', alpha=0.7)


# --- Main Simulation Logic ---
def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False):
    hiveX, hiveY = sim_params['hive_width'], sim_params['hive_height']
    hive_data = np.zeros((hiveX, hiveY, 2), dtype=int)
    hive_layout_config = {
        'max_x': hiveX, 'max_y': hiveY,
        'comb_stripe_width': sim_params['comb_stripe_width'],
        'max_nectar_per_cell': sim_params['max_nectar_per_cell'],
        'hive_exit_cell_inside': sim_params['hive_exit_cell_inside'],
        'hive_entry_cell_inside': sim_params['hive_entry_cell_inside']
    }

    # Set dead_duration for each flower from sim_params AFTER Flower objects are created by load_map
    # This is now handled by passing sim_params to load_map and then to Flower constructor

    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside']
    all_bees = [
        Bee(f"B{i+1}", initial_bee_pos_in_hive, property_config['hive_position_on_property'], 
            sim_params['bee_max_nectar_carry'], sim_params.get('bee_avoid_empty_duration', 20))
        for i in range(sim_params['num_bees'])
    ]

    fig = None
    axes_dict = None 
    current_figure_interactive = None # Use this to manage the figure in interactive mode

    if interactive_mode:
        plt.ion()
        current_figure_interactive, axes_array = plt.subplots(2, 2, figsize=(16, 10))
        axes_dict = {'hive': axes_array[0,0], 'property': axes_array[0,1], 'nectar': axes_array[1,0]}
        axes_array[1,1].axis('off')

    for t in range(sim_params['simlength']):
        print(f"\n--- Timestep {t+1}/{sim_params['simlength']} ---")

        for bee in all_bees:
            bee.step_change(property_map_data, flowers_list, hive_data, hive_layout_config, property_config, t)

        for flower in flowers_list:
            flower.regenerate_nectar(rate=sim_params.get('flower_regen_rate',1))

        if interactive_mode:
            if current_figure_interactive is None or not plt.fignum_exists(current_figure_interactive.number): # Recreate if closed
                current_figure_interactive, axes_array = plt.subplots(2, 2, figsize=(16, 10))
                axes_dict = {'hive': axes_array[0,0], 'property': axes_array[0,1], 'nectar': axes_array[1,0]}
                axes_array[1,1].axis('off')
                plt.ion() # Ensure interactive mode is on for the new figure

            axes_dict['hive'].clear()
            axes_dict['property'].clear()
            axes_dict['nectar'].clear()
            
            current_figure_interactive.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')

            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, axes_dict['hive'], hive_layout_config)

            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes_dict['property'])
            
            plot_flower_nectar(flowers_list, axes_dict['nectar'], sim_params.get('flower_nectar_capacity_default', 5))

            current_figure_interactive.tight_layout(rect=[0, 0, 1, 0.96])
            current_figure_interactive.canvas.draw()
            current_figure_interactive.canvas.flush_events()
            plt.pause(float(sim_params.get('interactive_pause', 0.1))) # Ensure pause value is float

        elif t == sim_params['simlength'] - 1:
            batch_fig, batch_axes_array = plt.subplots(2, 2, figsize=(16, 10))
            current_batch_axes = {'hive': batch_axes_array[0,0], 'property': batch_axes_array[0,1], 'nectar': batch_axes_array[1,0]}
            batch_axes_array[1,1].axis('off')
            batch_fig.suptitle(f"Bee World - Final State - Timestep: {t+1}", fontsize=16, fontweight='bold')
            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, current_batch_axes['hive'], hive_layout_config)
            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, current_batch_axes['property'])
            plot_flower_nectar(flowers_list, current_batch_axes['nectar'], sim_params.get('flower_nectar_capacity_default', 5))
            batch_fig.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig('beeworld_simulation_end.png')
            print("Saved final simulation state to beeworld_simulation_end.png")
            plt.close(batch_fig)

    if interactive_mode and current_figure_interactive and plt.fignum_exists(current_figure_interactive.number):
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
        sim_params = load_parameters(args.paramfile) # Load params first
        world_data, flowers_data, property_conf = load_map(args.mapfile, sim_params) # Pass sim_params to load_map
    except FileNotFoundError as e:
        print(f"Error: Required file not found. {e}")
        print("Please ensure map and parameter files exist at the specified paths or in the current directory if using defaults.")
        return
    except Exception as e:
        print(f"An error occurred during setup: {e}")
        return

    if args.interactive:
        print(f"Running in INTERACTIVE mode with map: {args.mapfile} and params: {args.paramfile}")
    else:
        print(f"Running in BATCH mode with map: {args.mapfile} and params: {args.paramfile}")

    run_simulation(sim_params, world_data, flowers_data, property_conf, interactive_mode=args.interactive)

if __name__ == "__main__":
    main()