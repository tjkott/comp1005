# Student Name: Thejana Kottawatta Hewage
# Student ID:   22307822
#
# beeworld.py - running the simulations in interactive/batch mode
#     12/05/2024 : Initial version released
#     05/04/2025 : Major revisions for file input, comb (honey) model, bee states, and plotting.
#     08/04/2025 : Added nectar plot and improved flower selection logic.
#     09/04/2025 : Integrated Flower "DEAD" state and delayed regeneration to allow more variety in meme movement across the property plot. 
#     11/04/2025 : Implemented bee collision avoidance and stuck resolution.
#     11/04/2025 : Refined slow logic, hive entrance clogging and flower regeneration. 
#     12/05/2024: Final version uploaded

import random
import argparse 
import csv      
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm 

from buzzness import Flower, Bee 

# (5) User interface
# Batch Mode
def loadMap(filename, sim_params): # Loads the property map, flower locations, and obstacles from a CSV file FOR BATCH MODE
    world_grid = None # Will hold the numpy array for terrain
    flowers = [] # List to store Flower objects
    property_config = {}
    property_w_default, property_h_default = 20, 15 # Default property width and height if not in file
    hive_x_default, hive_y_default = property_w_default // 2, property_h_default // 2 # Default hive entrance on property
    with open(filename, 'r') as f: # Open  map1.csv file for reading
        reader = csv.reader(f)
        try:
            header = next(reader) # First line: property_width, property_height, hive_x_on_property, hive_y_on_property
            propertyWidth = int(header[0].strip()) if len(header) > 0 and header[0].strip().isdigit() else property_w_default
            propertyHeight = int(header[1].strip()) if len(header) > 1 and header[1].strip().isdigit() else property_h_default
            hive_x = int(header[2].strip()) if len(header) > 2 and header[2].strip().isdigit() else hive_x_default
            hive_y = int(header[3].strip()) if len(header) > 3 and header[3].strip().isdigit() else hive_y_default
            property_config['max_x'] = propertyWidth
            property_config['max_y'] = propertyHeight
            property_config['hive_position_on_property'] = (hive_x, hive_y) 
            ## (Map Terrain Grid Parsing)
            terrainRows = [] # To store rows of terrain data before converting to numpy array
            for row in range(propertyHeight): # REad property lines
                line_str_list = next(reader)
                if len(line_str_list) < propertyWidth:
                    print(f"Warning: Terrain map line {row+1} is shorter than width ({len(line_str_list)} vs {propertyWidth}). Padding with 0s (passable terrain).")
                    line_str_list.extend(['0'] * (propertyWidth - len(line_str_list)))
                elif len(line_str_list) > propertyWidth:
                    print(f"Warning: Terrain map line {row+1} is longer than width ({len(line_str_list)} vs {propertyWidth}). Truncating.")
                    line_str_list = line_str_list[:propertyWidth]
                terrainRows.append([int(val.strip()) for val in line_str_list]) # Convert terrain values to int
            terrain_array_from_file = np.array(terrainRows) 
            if terrain_array_from_file.shape == (propertyHeight, propertyWidth): # Check if shape matches expected (rows, cols)
                world_grid = terrain_array_from_file.T # Transpose because file is (row,col) but numpy imshow often expects (x,y)
            else:
                raise ValueError(f"Terrain data shape error. Expected ({propertyHeight},{propertyWidth}) for file rows, derived shape {terrain_array_from_file.shape} before transpose.")
            flower_dead_duration_val = sim_params.get('flower_dead_time', 10) # Get from params or use default
            ## (Map Object Parsing - Flowers, Barriers, Obstacles, Water)
            for rowList in reader: # Read remaining lines for objects
                if not rowList or not rowList[0].strip(): continue # Skip empty or malformed lines
                obj_type = rowList[0].strip().upper() # First element is object type
                try:
                    if obj_type == "FLOWER":
                        if len(rowList) < 7: 
                            print(f"Skipping invalid flower line: {rowList}")
                            continue
                        # FLOWER, ID, X, Y, Name, Color, NectarCapacity
                        f_id, f_x_str, f_y_str, f_name, f_color, f_nectar_str = [s.strip() for s in rowList[1:7]]
                        f_x, f_y, f_nectar_capacity_from_csv = int(f_x_str), int(f_y_str), int(f_nectar_str)
                        flowers.append(Flower(f_id, (f_x, f_y), f_name, f_color, f_nectar_capacity_from_csv, flower_dead_duration_val))
                    elif obj_type == "BARRIER": 
                        if len(rowList) < 6:
                            print(f"Skipping invalid BARRIER line: {rowList}")
                            continue
                        _, b_x_str, b_y_str, b_w_str, b_h_str, b_val_str = [s.strip() for s in rowList[0:6]] # BARRIER, x, y coords, Width, Height, terrain types value
                        b_x, b_y, b_w, b_h, b_val = int(b_x_str), int(b_y_str), int(b_w_str), int(b_h_str), int(b_val_str)
                        # Ensure barrier is within property bounds before applying to world_grid
                        if 0 <= b_x < propertyWidth and 0 <= b_y < propertyHeight and b_x + b_w <= propertyWidth and b_y + b_h <= propertyHeight: 
                            world_grid[b_x : b_x + b_w, b_y : b_y + b_h] = b_val # Apply barrier to the grid
                        else:
                            print(f"Warning: Barrier at {rowList[1:5]} with width/height extends out of bounds. Skipping.")
                    elif obj_type == "OBSTACLE": # Single-cell obstacle
                        if len(rowList) < 5:
                            print(f"Warning: Skipping malformed OBSTACLE line: {rowList}")
                            continue
                        # OBSTACLE, ID, X, Y, Name
                        o_id_str, o_x_str, o_y_str, o_name_str = [s.strip() for s in rowList[1:5]]
                        o_x, o_y = int(o_x_str), int(o_y_str)
                        if 0 <= o_x < propertyWidth and 0 <= o_y < propertyHeight:
                            world_grid[o_x, o_y] = 1 # Typically, 1 is a generic obstacle value
                        else:
                            print(f"Warning: Obstacle at ({o_x}, {o_y}) out of bounds. Skipping.")
                    elif obj_type == "WATER": # Single-cell water feature
                        if len(rowList) < 5:
                            print(f"Warning: Skipping malformed WATER line: {rowList}")
                            continue
                        # WATER, ID, X, Y, Name
                        w_id_str, w_x_str, w_y_str, w_name_str = [s.strip() for s in rowList[1:5]]
                        w_x, w_y = int(w_x_str), int(w_y_str)
                        if 0 <= w_x < propertyWidth and 0 <= w_y < propertyHeight:
                            world_grid[w_x, w_y] = 2 # Typically, 2 is a water terrain value
                        else:
                            print(f"Warning: Water at ({w_x}, {w_y}) out of bounds. Skipping.")
                except ValueError as e: # Catch errors during conversion of object data (e.g., int())
                    print(f"Warning: Could not parse object line values in '{filename}': {rowList}. Error: {e}. Skipping.")
                except IndexError as e: # Catch errors if a line doesn't have enough elements
                    print(f"Warning: Malformed object line (not enough elements) in '{filename}': {rowList}. Error: {e}. Skipping.")
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
    if world_grid is None: #
        print(f"Warning: World grid could not be initialized from {filename}. Using a default empty grid.")
        property_config.setdefault('max_x', property_w_default)
        property_config.setdefault('max_y', property_h_default)
        property_config.setdefault('hive_position_on_property', (hive_x_default, hive_y_default))
        world_grid = np.zeros((property_config['max_x'], property_config['max_y']), dtype=int) # Create a basic empty grid
    return world_grid, flowers, property_config

def loadParameters(filename): # Loads simulation parameters from a CSV file FOR BATCH MODE
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
    ## Default Simulation Parameters for batch mode - used only if issues with param1.csv file
    params.setdefault('num_bees', 5)
    params.setdefault('simlength', 100)
    params.setdefault('hive_width', 10) 
    params.setdefault('hive_height', 8)  
    params.setdefault('comb_stripe_width', 3)
    params.setdefault('max_nectar_per_cell', 4) # Max nectar a single hive comb cell can hold
    params.setdefault('bee_max_nectarCarry', 1)
    params.setdefault('flower_regen_rate', 1)
    params.setdefault('bee_empty_flower_avoiding_duration', 20)
    params.setdefault('flower_nectar_capacity_default', 5) 
    params.setdefault('flower_dead_time', 10)
    params.setdefault('interactive_pause', 0.1) # Pause duration for interactive plotting (if mode was different)
    params.setdefault('bee_max_clogCount', 5)
    # Ensure hive dimensions are integers after potentially being loaded as float/str
    hiveW = int(params.get('hive_width', 10)) 
    hiveH = int(params.get('hive_height', 8))
    params['hive_width'] = hiveW
    params['hive_height'] = hiveH
    ## (Hive Internal Entry/Exit Points from Batch File)
    default_internal_x = 0 # Default x for internal hive points (e.g., left edge)
    default_internal_y = hiveH - 1 if hiveH > 0 else 0 # Default y (e.g., top edge)
    params['hive_exit_cell_inside_x'] = int(params.get('hive_exit_cell_inside_x', default_internal_x))
    params['hive_exit_cell_inside_y'] = int(params.get('hive_exit_cell_inside_y', default_internal_y))
    params['hive_entry_cell_inside_x'] = int(params.get('hive_entry_cell_inside_x', default_internal_x))
    params['hive_entry_cell_inside_y'] = int(params.get('hive_entry_cell_inside_y', default_internal_y))
    params['hive_exit_cell_inside'] = (params['hive_exit_cell_inside_x'], params['hive_exit_cell_inside_y'])
    params['hive_entry_cell_inside'] = (params['hive_entry_cell_inside_x'], params['hive_entry_cell_inside_y'])
    print(f"Loaded parameters (batch): {params}")
    return params

# Interactive mode
def loadInteractiveParameters(): # Prompts user for parameters in INTERACTIVE MODE
    """
    Gets simulation parameters from user input for interactive mode.
    Returns a dictionary of parameters.
    """
    params = {} # dictionary to store parameters
    print("\nInteractive Simulation Parameter Setup")
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
    params['bee_max_nectarCarry'] = get_int_input("Bee max nectar carry", 1)
    params['comb_stripe_width'] = 3 # Default comb stripe width
    params['max_nectar_per_cell'] = 4 # Default max nectar per hive cell
    params['flower_regen_rate'] = 1 # Default flower nectar regeneration rate
    params['bee_empty_flower_avoiding_duration'] = 20 # Default duration bee avoids emptied flower
    params['flower_nectar_capacity_default'] = 5 # Default nectar capacity for randomly generated flowers
    params['flower_dead_time'] = 10 # Default time a flower stays dead
    params['interactive_pause'] = 0.1 # Default pause for interactive plotting
    params['bee_max_clogCount'] = 5 # Default max time a bee can be clogged/stuck
    hive_w = params['hive_width'] 
    hive_h = params['hive_height']
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

def generateInteractiveMap(sim_params): # Generates property, flowers, obstacles for INTERACTIVE MODE
    """
    Generates property grid, flower list, and property configuration randomly based on user inputs/defaults.
    sim_params:  dictionary of simulation parameters (some may be used for defaults here)
    """
    print("\nInteractive Mode Map Generation")
    property_config = {} # dictionary for property settings
    flowers_list = []    # list to hold Flower objects
    while True: #input from user
        try:
            prop_w_str = input(f"Enter property width (e.g., 30, default: 30): ")
            propertyW = int(prop_w_str) if prop_w_str else 30
            prop_h_str = input(f"Enter property height (e.g., 20, default: 20): ")
            propertyH = int(prop_h_str) if prop_h_str else 20
            if propertyW > 0 and propertyH > 0: break
            else: print("Dimensions must be positive integers.")
        except ValueError: print("Invalid input for dimensions. Please enter integers.")
    property_config['max_x'] = propertyW
    property_config['max_y'] = propertyH
    hive_x_prop = propertyW // 2 # Hive position on property - can be set to center or randomized
    hive_y_prop = propertyH // 2
    property_config['hive_position_on_property'] = (hive_x_prop, hive_y_prop)
    world_data = np.zeros((propertyW, propertyH), dtype=int) # Initialize property as empty passable terrain (value 0
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
        f_id = f"Flower_Int{i+1}" #  ID for input generated flower
        f_x = random.randint(0, propertyW - 1) 
        f_y = random.randint(0, propertyH - 1) 
        while (f_x, f_y) == property_config['hive_position_on_property']: #avoid plotting a flower directly on hive entrance
            f_x = random.randint(0, propertyW - 1)
            f_y = random.randint(0, propertyH - 1)
        f_name = random.choice(flower_names_pool)
        f_color = random.choice(flower_colors_pool)
        # Nectar capacity can be slightly randomized around the default
        f_nectar_capacity = max(1, default_nectar_cap + random.randint(-int(default_nectar_cap/2), int(default_nectar_cap/2))) 
        flowers_list.append(Flower(f_id, (f_x, f_y), f_name, f_color, f_nectar_capacity, default_dead_time))
    print(f"Generated {len(flowers_list)} flowers randomly on the property.")
    while True:
        try:
            num_obstacles_str = input(f"Enter number of rectangular obstacles (e.g., 3, default: 3): ")
            num_obstacles = int(num_obstacles_str) if num_obstacles_str else 3
            if num_obstacles >= 0: break
            else: print("Number of obstacles cannot be negative.")
        except ValueError: print("Invalid input for number of obstacles. Please enter an integer.")
    for i in range(num_obstacles): # obstacle properties
        obs_w = random.randint(1, max(1, propertyW // 8)) # Obstacle width, minimum = 1
        obs_h = random.randint(1, max(1, propertyH // 8)) 
        obs_x = random.randint(0, propertyW - obs_w) # Ensure obstacle spawns within bounds
        obs_y = random.randint(0, propertyH - obs_h)
        # Avoid placing obstacle directly over hive entrance (simple check for center of obstacle)
        hive_center_in_obstacle = (obs_x <= hive_x_prop < obs_x + obs_w) and (obs_y <= hive_y_prop < obs_y + obs_h)
        if not hive_center_in_obstacle:
            world_data[obs_x : obs_x + obs_w, obs_y : obs_y + obs_h] = 1 # Mark cells as obstacle (value 1)
    print(f"Generated {num_obstacles} rectangular obstacles randomly on the property.")   
    print(f"Generated interactive environment: \n Dimensions: ({propertyW}x{propertyH})")
    return world_data, flowers_list, property_config

def plot_hive(hive, blist, ax, hiveLayout):
    ax.clear() # Clear previous plot content from the axis
    max_nectar_val = hiveLayout.get('max_nectar_per_cell', 4) # Max nectar for color scaling
    val_not_yet_built_in_stripe = max_nectar_val + 1 # Value for cells in stripe but not built
    val_outside_stripe = max_nectar_val + 2    # Value for cells outside comb stripe (background)
    hive_plot_array = np.full((hiveLayout['max_x'], hiveLayout['max_y']), float(val_outside_stripe)) 
    comb_width = hiveLayout.get('comb_stripe_width', 3)
    stripe_center_x = hiveLayout['max_x'] // 2
    start_x = max(0, stripe_center_x - comb_width // 2)
    end_x = min(hiveLayout['max_x'], start_x + comb_width)
    for r_idx in range(hiveLayout['max_x']): # Iterate through hive cells
        for c_idx in range(hiveLayout['max_y']):
            is_in_stripe = (start_x <= r_idx < end_x) # Check if cell is in the comb stripe
            if is_in_stripe:
                if hive[r_idx, c_idx, 0] == 1: # If comb is built
                    nectar_level = hive[r_idx, c_idx, 1] 
                    hive_plot_array[r_idx, c_idx] = nectar_level 
                else: # Comb not built in stripe
                    hive_plot_array[r_idx, c_idx] = float(val_not_yet_built_in_stripe)
    num_nectar_shades = max_nectar_val + 1 
    try:
        base_cmap = plt.get_cmap('Oranges', num_nectar_shades + 2) # Colormap for nectar + states
        colors = [base_cmap(i) for i in range(num_nectar_shades)] 
    except ValueError: 
        base_cmap = plt.get_cmap('Oranges')
        colors = [base_cmap(i / (num_nectar_shades -1 if num_nectar_shades >1 else 1) ) for i in range(num_nectar_shades)]
    colors.append((0.85, 0.85, 0.85, 1)) 
    colors.append((0.6, 0.4, 0.2, 1))    # Darker brown for OutsideStripe (hive background)
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
    ax.set_xlim(-0.5, hiveLayout['max_x'] - 0.5) # Set plot limits
    ax.set_ylim(-0.5, hiveLayout['max_y'] - 0.5)
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
            flower_plot_colors.append('grey') # dead flowers are grey
        else:
            flower_plot_colors.append(flower_colors_map.get(f.colour, 'magenta')) # Use defined color or magenta
    if flower_x: # Only plot if there are flowers
        ax.scatter(flower_x, flower_y, c=flower_plot_colors, marker='P', s=80, label='Flowers', edgecolors='black', alpha=0.7)
    hive_pos_prop = property_config['hive_position_on_property'] # Get hive location on property
    ax.scatter(hive_pos_prop[0], hive_pos_prop[1], c='gold', marker='H', s=150, edgecolors='black', label='Hive Entrance') # Plot hive entrance
    bee_x = [b.get_pos()[0] for b in bees_on_property if not b.get_inhive()] # Plot initial positions of bees outside the hive
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

def plot_flowerNectar(flowers_list, ax, default_max_nectar): # Creates a bar chart of nectar levels for each flower
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
    for barX, bar in enumerate(bars):
        yval = bar.get_height() # Current nectar level
        text_offset = 0.05 * (max_cap + 1) if max_cap > 0 else 0.05 # Small offset for text
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + text_offset , 
                f'{yval}/{flowers_list[barX].nectarCapacity}', 
                ha='center', va='bottom', fontsize=7)
    ax.grid(axis='y', linestyle='--', alpha=0.7) # Add a light grid for y-axis

def run_simulation(sim_params, property_map_data, flowers_list, property_config, interactive_mode=False): # Main function to run the bee simulation steps
    hiveX, hiveY = sim_params['hive_width'], sim_params['hive_height'] # Get hive dimensions from parameters
    max_nectar_in_comb = sim_params.get('max_nectar_per_cell', 4)
    # Initialize hive data: 3D numpy array (x, y, [comb_status, nectar_amount])
    hive_data = np.zeros((hiveX, hiveY, 2), dtype=int)
    # Configuration for hive layout, passed to bees and plotting functions
    hive_layout_config = {'max_x': hiveX, 'max_y': hiveY,
        'comb_stripe_width': sim_params['comb_stripe_width'],
        'max_nectar_per_cell': max_nectar_in_comb,
        'hive_exit_cell_inside': sim_params['hive_exit_cell_inside'],
        'hive_entry_cell_inside': sim_params['hive_entry_cell_inside']}
    initial_bee_pos_in_hive = hive_layout_config['hive_entry_cell_inside'] # Bees start at the designated internal entry point
    if not (0 <= initial_bee_pos_in_hive[0] < hiveX and 0 <= initial_bee_pos_in_hive[1] < hiveY):
        print(f"Warning: Initial bee position {initial_bee_pos_in_hive} is outside hive dimensions {hiveX}x{hiveY}. Resetting.")
        initial_bee_pos_in_hive = (min(hiveX-1,0) if hiveX > 0 else 0, min(hiveY-1,0) if hiveY > 0 else 0)
        if hiveX > 0 and hiveY > 0: initial_bee_pos_in_hive = (hiveX//2, hiveY//2) # Prefer center if hive has size
    all_bees = [Bee(f"B{i+1}", initial_bee_pos_in_hive, property_config['hive_position_on_property'],
            sim_params['bee_max_nectarCarry'],
            sim_params.get('bee_empty_flower_avoiding_duration', 20),
            sim_params.get('bee_max_clogCount', 5))
        for i in range(sim_params['num_bees'])]
    plt.ion() # Turn on interactive mode for Matplotlib
    fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10)) # Create 2x2 grid of subplots
    axes_dict_interactive = {'hive': axes_array_interactive[0,0],'property': axes_array_interactive[0,1],'nectar': axes_array_interactive[1,0]}
    axes_array_interactive[1,1].axis('off') # Turn off the unused 4th subplot
    for t in range(sim_params['simlength']): ## Main for loop for the simulation
        print(f"\n--- Timestep {t+1}/{sim_params['simlength']} ---") # Log current timestep
        random.shuffle(all_bees) # Shuffle bee order each timestep to vary update priority
        for i, current_bee_obj in enumerate(all_bees):
            # Gather information about other bees for collision avoidance
            other_bees_details = []
            for j, other_b in enumerate(all_bees):
                if i != j: # Don't include the current bee in its own "other bees" list
                    other_bees_details.append({'pos': other_b.get_pos(), 'state': other_b.state,'id': other_b.ID,'inhive': other_b.get_inhive()})
            current_bee_obj.step_change(property_map_data, flowers_list, hive_data, hive_layout_config,property_config,t,other_bees_details)
        for flower in flowers_list:
            flower.regenerate_nectar(rate=sim_params.get('flower_regen_rate',1))
        if fig_interactive is None or not plt.fignum_exists(fig_interactive.number):
            print("Plot window was closed or not initialized, re-creating for step-by-step display.")
            plt.ion() 
            fig_interactive, axes_array_interactive = plt.subplots(2, 2, figsize=(16, 10))
            axes_dict_interactive = {'hive': axes_array_interactive[0,0], 'property': axes_array_interactive[0,1],'nectar': axes_array_interactive[1,0]}
            axes_array_interactive[1,1].axis('off')
        axes_dict_interactive['hive'].clear()
        axes_dict_interactive['property'].clear()
        axes_dict_interactive['nectar'].clear()
        # Set suptitle
        fig_interactive.suptitle(f"Bee World - Timestep: {t+1}/{sim_params['simlength']}", fontsize=16, fontweight='bold')
        bees_in_hive_list = [b for b in all_bees if b.get_inhive()]
        plot_hive(hive_data, bees_in_hive_list, axes_dict_interactive['hive'], hive_layout_config)
        bees_on_property_list = [b for b in all_bees if not b.get_inhive()]
        plot_property(property_map_data, flowers_list, bees_on_property_list, property_config, axes_dict_interactive['property'])
        plot_flowerNectar(flowers_list, axes_dict_interactive['nectar'], sim_params.get('flower_nectar_capacity_default', 5))
        fig_interactive.tight_layout(rect=[0, 0, 1, 0.96])
        fig_interactive.canvas.draw()
        fig_interactive.canvas.flush_events()
        try:
            pause_duration = float(sim_params.get('interactive_pause', 0.1))
        except ValueError:
            pause_duration = 0.1
        plt.pause(pause_duration)
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
             pass
        plt.ioff()
        plt.show() # Keep the plot window open until the user closes it manually
    else:
        print("Simulation finished!")
        if not interactive_mode: 
             print("(Check for 'beeworld_simulation_end.png' if simulation ran to completion for final result")

def main(): # Main function to parse arguments and begin the simulation
    parser = argparse.ArgumentParser(description="Bee World Simulation") # Setup argument parser
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode.")
    parser.add_argument("-f", "--mapfile", type=str, default="map1.csv", help="Path to CSV for property map")
    parser.add_argument("-p", "--paramfile", type=str, default="para1.csv", help="Path to CSV for simulation parameters")
    args = parser.parse_args() 
    sim_params = None 
    world_data = None       
    flowers_data = None     
    property_conf = None    
    # Error handling
    if args.interactive: 
        print(f"Running in INTERACTIVE mode: User inputs for parameters, random environment generation, step-by-step plotting.") ## Interactive - get parameters from user and generate environment randomly
        try:
            sim_params = loadInteractiveParameters() # Call new function for user parameter input
            world_data, flowers_data, property_conf = generateInteractiveMap(sim_params) # Call new function for random environment
        except Exception as e:
            print(f"An error occurred during interactive setup: {e}")
            import traceback
            traceback.print_exc() 
            return 
    else: 
        ## Batch Mode Setup - Load parameters and map from files
        print(f"Running in BATCH mode with map: {args.mapfile} and params: {args.paramfile}")
        try:
            sim_params = loadParameters(args.paramfile) # Load parameters from file
            world_data, flowers_data, property_conf = loadMap(args.mapfile, sim_params) # Load map from file
        except FileNotFoundError as e:
            print(f"Error: Required file not found for batch mode. {e}")
            print("Please ensure map and parameter files exist at specified paths or use defaults.")
            return # Exit if essential files are missing
        except Exception as e: # Catch any other errors during batch setup
            print(f"An error occurred during batch setup: {e}")
            import traceback
            traceback.print_exc() 
            return
    if sim_params and world_data is not None and flowers_data is not None and property_conf:
        run_simulation(sim_params, world_data, flowers_data, property_conf, interactive_mode=args.interactive)
    else:
        print("Cannot run simulation.")
if __name__ == "__main__": 
    main()