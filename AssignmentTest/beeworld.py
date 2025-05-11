# Student Name: <put your name here>
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information:
#     2024-04-07 : Initial Version released
#     2025-05-11 : Major revisions for file input, honey model, bee missions, and plotting.
#
import random
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt

# --- Flower Class ---
class Flower():
    def __init__(self, ID, pos, name, color, nectar_capacity=5):
        self.ID = ID
        self.pos = pos # (x,y)
        self.name = name
        self.color = color # This might be a string or a numerical value for plotting
        self.nectar_capacity = nectar_capacity
        self.current_nectar = nectar_capacity

    def get_pos(self):
        return self.pos

    def get_nectar(self):
        return self.current_nectar

    def take_nectar(self, amount=1):
        taken = min(amount, self.current_nectar)
        self.current_nectar -= taken
        return taken

    def regenerate_nectar(self, rate=1): # Simple regeneration
        if self.current_nectar < self.nectar_capacity:
            self.current_nectar = min(self.nectar_capacity, self.current_nectar + rate)

# --- Bee Class ---
class Bee():
    def __init__(self, ID, initial_pos, hive_entrance_property_pos, max_nectar_carry=1):
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
        self.path = [] # For potential A* pathfinding, not fully implemented here

    def step_change(self, property_map_data, flowers_list, hive_data, hive_layout_config, property_config):
        self.age += 1
        # print(f"DEBUG Bee {self.ID}: State={self.state}, Pos={self.pos}, Nectar={self.nectar_carried}, Target={self.current_target_pos}")

        # --- STATE MACHINE LOGIC ---
        if self.state == 'IDLE_IN_HIVE':
            if self.nectar_carried >= 1 and self._can_build_or_deposit(hive_data, hive_layout_config): # Prioritize using carried nectar
                comb_build_target = self._find_comb_to_build(hive_data, hive_layout_config)
                if comb_build_target:
                    self.current_target_pos = comb_build_target
                    self.state = 'MOVING_TO_COMB_BUILD_SITE'
                else: # No place to build, try depositing
                    comb_deposit_target = self._find_comb_to_deposit(hive_data, hive_layout_config)
                    if comb_deposit_target:
                        self.current_target_pos = comb_deposit_target
                        self.state = 'MOVING_TO_COMB_DEPOSIT_SITE'
                    else: # Can't build or deposit, try foraging if not full
                        if self.nectar_carried < self.max_nectar_carry:
                           self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                           self.state = 'MOVING_TO_HIVE_EXIT'
            elif self.nectar_carried < self.max_nectar_carry : # Forage for nectar
                self.current_target_pos = hive_layout_config['hive_exit_cell_inside']
                self.state = 'MOVING_TO_HIVE_EXIT'
            # else: full of nectar but nowhere to deposit/build, remain idle or add other logic


        elif self.state == 'MOVING_TO_HIVE_EXIT':
            if self.pos == self.current_target_pos:
                self.inhive = False
                self.pos = self.hive_entrance_property_pos
                self.state = 'SEEKING_FLOWER'
                self.current_target_pos = None
            else:
                self._move_towards_target(None, hive_layout_config['max_x'], hive_layout_config['max_y'], is_in_hive=True)

        elif self.state == 'SEEKING_FLOWER':
            self.current_target_object = self._find_closest_flower_with_nectar(flowers_list)
            if self.current_target_object:
                self.current_target_pos = self.current_target_object.get_pos()
                self.state = 'MOVING_TO_FLOWER'
            else:
                self.state = 'IDLE_ON_PROPERTY' # No flowers with nectar
                self.current_target_pos = None

        elif self.state == 'MOVING_TO_FLOWER':
            if self.current_target_object is None or self.current_target_object.get_nectar() == 0: # Target vanished or emptied
                self.state = 'SEEKING_FLOWER'
                self.current_target_pos = None
            elif self.pos == self.current_target_pos:
                self.state = 'COLLECTING_NECTAR'
            else:
                self._move_towards_target(property_map_data, property_config['max_x'], property_config['max_y'], is_in_hive=False)

        elif self.state == 'COLLECTING_NECTAR':
            if self.current_target_object and self.current_target_object.get_nectar() > 0 and self.nectar_carried < self.max_nectar_carry:
                amount_to_take = self.max_nectar_carry - self.nectar_carried
                taken = self.current_target_object.take_nectar(amount_to_take)
                self.nectar_carried += taken
            # Finished collecting if full or flower is empty
            if self.nectar_carried >= self.max_nectar_carry or not self.current_target_object or self.current_target_object.get_nectar() == 0:
                self.current_target_pos = self.hive_entrance_property_pos
                self.state = 'RETURNING_TO_HIVE_ENTRANCE'
                self.current_target_object = None # Clear flower target

        elif self.state == 'RETURNING_TO_HIVE_ENTRANCE':
            if self.pos == self.current_target_pos:
                self.inhive = True
                self.pos = hive_layout_config['hive_entry_cell_inside']
                self.state = 'IDLE_IN_HIVE' # Re-evaluate in hive
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
            # Check if still valid target (might have been built by another bee)
            if self.nectar_carried >= 1 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x, y, 0] == 0:
                hive_data[x, y, 0] = 1 # Mark comb_built status
                hive_data[x, y, 1] = 0 # Nectar level is 0 for new comb
                self.nectar_carried -= 1 # Cost to build
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
            # Check if still valid target
            if self.nectar_carried > 0 and 0 <= x < hive_layout_config['max_x'] and 0 <= y < hive_layout_config['max_y'] and hive_data[x,y,0] == 1: # Must be built
                can_deposit = hive_layout_config['max_nectar_per_cell'] - hive_data[x,y,1]
                deposited_amount = min(self.nectar_carried, can_deposit)
                if deposited_amount > 0:
                    hive_data[x,y,1] += deposited_amount
                    self.nectar_carried -= deposited_amount
                    print(f"Bee {self.ID} deposited {deposited_amount} nectar at {self.pos}. Cell now has {hive_data[x,y,1]}")
            self.state = 'IDLE_IN_HIVE'
            self.current_target_pos = None

        elif self.state == 'IDLE_ON_PROPERTY':
            # Wander or try to return to hive if stuck too long
            if self.age % 20 == 0 : # Every 20 steps, try returning if idle on property
                 self.current_target_pos = self.hive_entrance_property_pos
                 self.state = 'RETURNING_TO_HIVE_ENTRANCE'
            else: # Simple random move if truly idle on property (could be improved)
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

        # Prevent moving if already at target (dx=0, dy=0 means move=[0,0])
        if move == [0,0] and self.pos == self.current_target_pos:
            return


        newX = self.pos[0] + move[0]
        newY = self.pos[1] + move[1]

        if 0 <= newX < maxX and 0 <= newY < maxY:
            if not is_in_hive and map_data is not None:
                # Basic obstacle check: assume map_data > 0 might be an obstacle (e.g. water, tree)
                # Convention: 0 is passable, 1+ might be obstacles. Adjust as per your map1.csv.
                if map_data[newX, newY] != 0: # Assuming 0 is passable ground
                    # Try to move only in X or Y if diagonal is blocked (simple avoidance)
                    if move[0] != 0 and move[1] != 0: # Was a diagonal move
                        # Try X move only
                        if 0 <= self.pos[0] + move[0] < maxX and map_data[self.pos[0] + move[0], self.pos[1]] == 0:
                            self.pos = (self.pos[0] + move[0], self.pos[1])
                            return
                        # Try Y move only
                        elif 0 <= self.pos[1] + move[1] < maxY and map_data[self.pos[0], self.pos[1] + move[1]] == 0:
                             self.pos = (self.pos[0], self.pos[1] + move[1])
                             return
                    # else, cannot move
                    return # Blocked
            self.pos = (newX, newY)

    def _move_randomly(self, map_data, maxX, maxY):
        """A simple random move for IDLE_ON_PROPERTY state."""
        # validmoves = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,0)] # Moore neighborhood
        validmoves = [(0,1), (1,0), (0,-1), (-1,0)] # Von Neumann for simplicity
        chosen_move = random.choice(validmoves)
        newX = self.pos[0] + chosen_move[0]
        newY = self.pos[1] + chosen_move[1]

        if 0 <= newX < maxX and 0 <= newY < maxY:
            if map_data is not None and map_data[newX, newY] != 0: # Obstacle
                return
            self.pos = (newX, newY)


    def _find_closest_flower_with_nectar(self, flowers_list):
        closest_flower = None
        min_dist_sq = float('inf') # Use squared distance to avoid sqrt
        for flower in flowers_list:
            if flower.get_nectar() > 0:
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

        for y_idx in range(hive_layout_config['max_y']): # Build bottom-up preferred
            for x_idx in range(start_x, end_x):
                if hive_data[x_idx, y_idx, 0] == 0: # If comb cell not built
                    return (x_idx, y_idx)
        return None

    def _find_comb_to_deposit(self, hive_data, hive_layout_config):
        comb_width = hive_layout_config.get('comb_stripe_width', 3)
        stripe_center_x = hive_layout_config['max_x'] // 2
        start_x = max(0, stripe_center_x - comb_width // 2)
        end_x = min(hive_layout_config['max_x'], start_x + comb_width)
        max_nectar_per_cell = hive_layout_config.get('max_nectar_per_cell', 5)

        for y_idx in range(hive_layout_config['max_y']): # Fill bottom-up preferred
            for x_idx in range(start_x, end_x):
                if hive_data[x_idx, y_idx, 0] == 1 and hive_data[x_idx, y_idx, 1] < max_nectar_per_cell:
                    return (x_idx, y_idx)
        return None

    def _can_build_or_deposit(self, hive_data, hive_layout_config):
        """Checks if there's any valid spot to build or deposit."""
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
def load_map(filename):
    """
    Loads map data from a CSV file.
    Expected CSV format:
    Line 1: property_width,property_height,hive_entrance_x_on_property,hive_entrance_y_on_property
    Line 2 to (property_height + 1): Comma-separated integers for terrain grid (each line is a COLUMN of the map)
                                      (So, property_width values per line, for property_height lines)
                                      Convention: 0=passable, >0 may be obstacles.
    After terrain grid:
    FLOWER,id_str,x,y,name_str,color_str,nectar_capacity_int
    BARRIER,x,y,width,height,terrain_value_int (marks a rectangular area with terrain_value)
    """
    world_grid = None
    flowers = []
    property_config = {}

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        try:
            # Line 1: Config
            header = next(reader)
            prop_w, prop_h = int(header[0]), int(header[1])
            property_config['max_x'] = prop_w
            property_config['max_y'] = prop_h
            property_config['hive_position_on_property'] = (int(header[2]), int(header[3]))

            world_grid = np.zeros((prop_w, prop_h), dtype=int) # Default to passable terrain (0)

            # Lines for terrain grid (assuming each CSV row is a COLUMN of the map)
            # Transpose needed if CSV stores rows of the map.
            # The example implies CSV stores map column by column.
            # If CSV stores map visually (row by row):
            # for r_idx in range(prop_h):
            #    line = next(reader)
            #    values = [int(x) for x in line]
            #    world_grid[:, r_idx] = values[:prop_w] # if map is WxH and file shows map as W columns, H rows

            # Assuming CSV file rows represent *rows* of the visual map:
            # world_grid will be indexed grid[x,y]
            temp_terrain_rows = []
            for _ in range(prop_h): # Read H lines for the H rows of the map
                line_str = next(reader)
                temp_terrain_rows.append([int(val) for val in line_str])

            # Convert to numpy array and transpose if necessary to match (x,y) indexing
            # If temp_terrain_rows[row_idx][col_idx] = map at (col_idx, row_idx)
            # world_grid[col_idx, row_idx]
            terrain_array_from_file = np.array(temp_terrain_rows) # Shape (H, W)
            if terrain_array_from_file.shape == (prop_h, prop_w):
                 world_grid = terrain_array_from_file.T # Now shape (W, H) for grid[x,y] access
            else:
                raise ValueError(f"Terrain data shape mismatch. Expected ({prop_h},{prop_w}), got {terrain_array_from_file.shape}")


            # Process remaining lines for Flowers, Barriers, etc.
            for row_list in reader:
                if not row_list: continue
                obj_type = row_list[0].upper()
                if obj_type == "FLOWER":
                    _, f_id, f_x, f_y, f_name, f_color, f_nectar = row_list
                    flowers.append(Flower(f_id, (int(f_x), int(f_y)), f_name, f_color, int(f_nectar)))
                elif obj_type == "BARRIER": # Example: BARRIER,x,y,width,height,value
                    _, b_x, b_y, b_w, b_h, b_val = row_list
                    b_x, b_y, b_w, b_h, b_val = int(b_x), int(b_y), int(b_w), int(b_h), int(b_val)
                    world_grid[b_x : b_x + b_w, b_y : b_y + b_h] = b_val # Mark barrier cells
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
                key, value = row[0].strip(), row[1].strip()
                try:
                    if '.' in value: params[key] = float(value)
                    else: params[key] = int(value)
                except ValueError:
                    params[key] = value
    # Default values
    params.setdefault('num_bees', 5)
    params.setdefault('simlength', 100)
    params.setdefault('hive_width', 20) # Smaller default hive
    params.setdefault('hive_height', 15)
    params.setdefault('comb_stripe_width', 3)
    params.setdefault('max_nectar_per_cell', 5)
    params.setdefault('bee_max_nectar_carry', 1)
    params.setdefault('flower_regen_rate', 1) # How much nectar flowers regen per step

    # Define where bees exit/enter *within* the hive grid
    # Ensure these are derived after hive_width/height are set
    params.setdefault('hive_exit_cell_inside_x', params['hive_width'] // 2)
    params.setdefault('hive_exit_cell_inside_y', 0) # Bottom center
    params.setdefault('hive_entry_cell_inside_x', params['hive_width'] // 2)
    params.setdefault('hive_entry_cell_inside_y', 0) # Bottom center

    # Combine into tuples for easier use
    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])

    print(f"Loaded parameters: {params}")
    return params

# --- Plotting Functions ---
def plot_hive(hive_data, bees_in_hive, ax, hive_layout_config):
    # hive_data is (W, H, 2)
    hive_plot_array = np.full((hive_layout_config['max_x'], hive_layout_config['max_y']), 9.0) # Base color for outside stripe

    comb_width = hive_layout_config.get('comb_stripe_width', 3)
    stripe_center_x = hive_layout_config['max_x'] // 2
    start_x = max(0, stripe_center_x - comb_width // 2)
    end_x = min(hive_layout_config['max_x'], start_x + comb_width)

    # YlOrBr: 0 (lightest yellow) to 10 (darkest brown/red)
    # Mapping:
    # Empty Built Comb: color 0 (White/Lightest Yellow)
    # Nectar Level 1-5: colors 1-5 (Progressively darker/more intense yellow/orange)
    # Not Built (in stripe): color 8 (e.g. a light brown)
    # Outside Stripe: color 9 (e.g. a darker brown)
    for r_idx in range(hive_layout_config['max_x']):      # rows (x-coords)
        for c_idx in range(hive_layout_config['max_y']):  # columns (y-coords)
            is_in_stripe = (start_x <= r_idx < end_x)
            if is_in_stripe:
                if hive_data[r_idx, c_idx, 0] == 1: # Comb is built
                    nectar_level = hive_data[r_idx, c_idx, 1]
                    hive_plot_array[r_idx, c_idx] = min(nectar_level, 5) # Nectar level 0-5 maps to colors 0-5
                else: # Not built yet (within stripe)
                    hive_plot_array[r_idx, c_idx] = 8
            # else it remains 9 (outside stripe)

    ax.imshow(hive_plot_array.T, origin="lower", cmap='YlOrBr', vmin=0, vmax=9)

    xvalues = [b.get_pos()[0] for b in bees_in_hive if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in bees_in_hive if b.get_inhive()]
    ax.scatter(xvalues, yvalues, c='black', marker='o', s=30, label='Bees')
    ax.set_title('Bee Hive')
    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")
    ax.set_xlim(-0.5, hive_layout_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, hive_layout_config['max_y'] - 0.5)
    if bees_in_hive: ax.legend(loc='upper right')


def plot_property(property_map_data, flowers_list, bees_on_property, property_config, ax):
    ax.imshow(property_map_data.T, origin="lower", cmap='tab20', vmin=0, vmax=19) # Vmax depends on terrain types

    flower_x = [f.get_pos()[0] for f in flowers_list]
    flower_y = [f.get_pos()[1] for f in flowers_list]
    # Simple pink for all flowers, consider using f.color if defined meaningfully
    ax.scatter(flower_x, flower_y, c='magenta', marker='P', s=60, label='Flowers')

    hive_pos_prop = property_config['hive_position_on_property']
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='yellow', marker='s', s=120, edgecolors='black', label='Hive Entrance')

    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()]
    bee_y = [b.get_pos()[1] for b in bees_on_property if not b.get_inhive()]
    if bee_x: # Only plot if there are bees outside
      ax.scatter(bee_x, bee_y, c='black', marker='o', s=50, label='Bees')

    ax.set_title('Property')
    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")
    ax.set_xlim(-0.5, property_config['max_x'] - 0.5)
    ax.set_ylim(-0.5, property_config['max_y'] - 0.5)
    ax.legend(loc='upper right')

# --- Main Simulation Logic ---
def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False):
    hiveX, hiveY = sim_params['hive_width'], sim_params['hive_height']
    hive_data = np.zeros((hiveX, hiveY, 2), dtype=int) # Layer 0: built_status, Layer 1: nectar_level
    hive_layout_config = {
        'max_x': hiveX, 'max_y': hiveY,
        'comb_stripe_width': sim_params['comb_stripe_width'],
        'max_nectar_per_cell': sim_params['max_nectar_per_cell'],
        'hive_exit_cell_inside': sim_params['hive_exit_cell_inside'],
        'hive_entry_cell_inside': sim_params['hive_entry_cell_inside']
    }

    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside']
    all_bees = [
        Bee(f"B{i+1}", initial_bee_pos_in_hive, property_config['hive_position_on_property'], sim_params['bee_max_nectar_carry'])
        for i in range(sim_params['num_bees'])
    ]

    # Initialize figure and axes for interactive mode outside the loop
    fig = None
    axes = None
    if interactive_mode:
        plt.ion()  # Turn on interactive mode
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    for t in range(sim_params['simlength']):
        print(f"\n--- Timestep {t+1}/{sim_params['simlength']} ---")

        

        for bee in all_bees:
            bee.step_change(property_map_data, flowers_list, hive_data, hive_layout_config, property_config)

        for flower in flowers_list:
            flower.regenerate_nectar(rate=sim_params.get('flower_regen_rate',1))

        if interactive_mode:
            if fig is None or axes is None: # Should not happen if initialized correctly
                fig, axes = plt.subplots(1, 2, figsize=(18, 7))
                plt.ion() # Ensure interactive mode is on

            axes[0].clear()  # Clear the hive subplot
            axes[1].clear()  # Clear the property subplot

            fig.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')

            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, axes[0], hive_layout_config)

            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes[1])

            fig.tight_layout(rect=[0, 0.03, 1, 0.95]) # Re-apply layout
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(0.01)  # Shorter pause can make animation smoother, adjust as needed

        elif t == sim_params['simlength'] - 1:  # Batch mode: only plot and save the last frame
            # Create a new figure specifically for saving in batch mode
            batch_fig, batch_axes = plt.subplots(1, 2, figsize=(18, 7))
            batch_fig.suptitle(f"Bee World - Final State - Timestep: {t+1}", fontsize=16, fontweight='bold')

            bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
            plot_hive(hive_data, bees_in_hive_list, batch_axes[0], hive_layout_config)

            bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
            plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, batch_axes[1])

            batch_fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig('beeworld_simulation_end.png')
            print("Saved final simulation state to beeworld_simulation_end.png")
            plt.close(batch_fig) # Close the figure specifically created for saving

    if interactive_mode and fig: # Check if fig (the persistent figure) was created
        print("Simulation finished. Close the plot window to exit.")
        plt.ioff()  # Turn off interactive mode
        plt.show()  # This will now block and keep the final frame visible
    elif not interactive_mode: # Batch mode already printed its message
        print("Batch simulation finished.")
    else: # Should not happen if interactive_mode is true and fig wasn't created
        print("Simulation finished (no plot shown).")


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
        world_data, flowers_data, property_conf = load_map(args.mapfile)
        sim_params = load_parameters(args.paramfile)
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