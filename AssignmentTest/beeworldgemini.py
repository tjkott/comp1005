import math
import random

# --- Constants ---
# Bee States
STATE_IN_HIVE_IDLE = "IN_HIVE_IDLE"
STATE_FORAGING = "FORAGING"
STATE_RETURNING = "RETURNING"
STATE_DEPOSITING = "DEPOSITING"
STATE_BUILDING = "BUILDING" # Optional advanced state

# Cell States
CELL_EMPTY = "EMPTY"
CELL_COMB_BUILT = "COMB_BUILT"

# --- Classes ---

class HoneycombCell:
    """Represents a single cell in the honeycomb."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = CELL_EMPTY
        self.nectar_level = 0  # Max 5
        self.max_nectar = 5

    def build(self):
        if self.state == CELL_EMPTY:
            self.state = CELL_COMB_BUILT
            # print(f"Cell ({self.x},{self.y}) built.") # Debug
            return True
        return False

    def deposit_nectar(self, amount):
        if self.state == CELL_COMB_BUILT:
            can_deposit = self.max_nectar - self.nectar_level
            deposit_amount = min(amount, can_deposit)
            self.nectar_level += deposit_amount
            # print(f"Deposited {deposit_amount} nectar in cell ({self.x},{self.y}). Level: {self.nectar_level}") # Debug
            return deposit_amount # Return how much was actually deposited
        return 0

    def get_color(self):
        """Returns a color based on state and nectar level."""
        if self.state == CELL_EMPTY:
            return 'lightgrey' # Should not be plotted directly if empty usually
        elif self.state == CELL_COMB_BUILT:
            # Orange shades for nectar level (brighter = more nectar)
            # Using simple mapping, can be refined
            if self.nectar_level == 0:
                return 'orange' # Built, no nectar
            elif self.nectar_level == 1:
                return '#FFBF00' # Amber
            elif self.nectar_level == 2:
                return '#FFB000'
            elif self.nectar_level == 3:
                return '#FFA000'
            elif self.nectar_level == 4:
                 return '#FF9000'
            else: # Level 5
                return '#FF8000' # Brightest orange


class Hive:
    """Represents the beehive structure."""
    def __init__(self, x, y, width, height, frame_width=5):
        self.x = x # Bottom-left corner X in property coordinates
        self.y = y # Bottom-left corner Y in property coordinates
        self.width = width
        self.height = height
        # Simple entrance at the bottom middle
        self.entrance_pos = (x + width / 2, y - 0.5) # Slightly outside bottom edge
        self.cells = {}  # Dictionary mapping (local_x, local_y) to HoneycombCell
        self.frame_width = frame_width # Width of the initial comb stripe

        # Initial comb build (vertical stripe)
        self._build_initial_comb()

    def _build_initial_comb(self):
        """Builds the initial vertical stripe of comb."""
        # Ensure calculations use integer logic where needed for range/indexing
        # Convert hive dimensions and frame width to integers for calculations
        hive_width_int = int(self.width)
        hive_height_int = int(self.height)
        # Ensure frame_width is also treated as int if it wasn't already
        frame_width_int = int(self.frame_width)

        # Use integer division and ensure results are integers for range()
        # // performs floor division, result is int if both operands are int
        start_x = (hive_width_int - frame_width_int) // 2
        # end_x calculation now uses integers, resulting in an integer
        end_x = start_x + frame_width_int

        print(f"Building initial comb from x={start_x} to x={end_x-1} within hive dims {hive_width_int}x{hive_height_int}") # Should print integers

        # Use the integer versions in range()
        for local_y in range(hive_height_int):
            for local_x in range(start_x, end_x):
                 # Check bounds using integer width/height
                 if 0 <= local_x < hive_width_int and 0 <= local_y < hive_height_int:
                    # Pass integers to HoneycombCell constructor (local_x, local_y are from range)
                    cell = HoneycombCell(local_x, local_y)
                    cell.build() # Immediately set to built
                    self.cells[(local_x, local_y)] = cell
                 # else:
                 #    print(f"Skipping cell build at ({local_x},{local_y}) - out of bounds {hive_width_int}x{hive_height_int}")

    def get_cell_global_coords(self, local_x, local_y):
        """Convert local hive coords to global property coords."""
        return self.x + local_x + 0.5, self.y + local_y + 0.5 # Center of cell

    def get_cell_local_coords(self, global_x, global_y):
        """Convert global property coords to local hive coords."""
        local_x = int(global_x - self.x)
        local_y = int(global_y - self.y)
        return local_x, local_y

    def get_cell(self, local_x, local_y):
        """Gets a cell at local coordinates, returns None if not exists."""
        return self.cells.get((local_x, local_y))

    def find_deposit_spot(self):
        """Finds a built comb cell with space for nectar."""
        # Simple strategy: iterate through cells and find first available
        # Could be optimized (e.g., random sampling, checking near entrance)
        for cell in self.cells.values():
            if cell.state == CELL_COMB_BUILT and cell.nectar_level < cell.max_nectar:
                return (cell.x, cell.y) # Return local coords
        return None # No suitable cell found

    # --- Advanced Comb Building (Placeholder) ---
    def find_build_spot(self):
        """Finds an empty spot adjacent to existing comb."""
        # This requires more complex logic: iterate empty locations, check neighbors
        # For now, we'll just say building isn't implemented beyond initial comb
        print("Advanced comb building not implemented yet.")
        return None


class Flower:
    """Represents a flower as a nectar source."""
    def __init__(self, x, y, name="Flower", color="purple", initial_nectar=10.0, is_limited=True, regen_rate=0.1):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.max_nectar = initial_nectar
        self.current_nectar = initial_nectar
        self.is_limited = is_limited
        self.regen_rate = regen_rate # Nectar regenerated per time step

    def take_nectar(self, amount):
        """A bee takes nectar from the flower."""
        taken = 0
        if self.current_nectar > 0:
            taken = min(amount, self.current_nectar)
            if self.is_limited:
                self.current_nectar -= taken
        else:
            taken = amount # Assume unlimited if not limited
        return taken

    def regenerate(self):
        """Regenerate nectar over time if limited."""
        if self.is_limited:
            self.current_nectar = min(self.max_nectar, self.current_nectar + self.regen_rate)

    def is_depleted(self):
        return self.is_limited and self.current_nectar <= 0


class Obstacle:
    """Represents a terrain barrier."""
    def __init__(self, x, y, width, height, color="gray"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def contains(self, px, py):
        """Checks if a point (px, py) is inside the obstacle."""
        return (self.x <= px < self.x + self.width and
                self.y <= py < self.y + self.height)


class Property:
    """Represents the environment outside the hive."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.flowers = []
        self.obstacles = []
        # self.hive = None # The simulation will add the hive reference later if needed

    def add_flower(self, flower):
        self.flowers.append(flower)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def get_closest_available_flower(self, bee_pos):
        """Finds the nearest flower with nectar."""
        min_dist = float('inf')
        closest_flower = None
        bx, by = bee_pos

        available_flowers = [f for f in self.flowers if not f.is_depleted()]
        if not available_flowers:
            return None # No flowers available

        for flower in available_flowers:
            dist_sq = (flower.x - bx)**2 + (flower.y - by)**2
            if dist_sq < min_dist:
                min_dist = dist_sq
                closest_flower = flower

        return closest_flower

    def is_obstacle(self, x, y):
        """Checks if the given coordinate is within any obstacle."""
        for obs in self.obstacles:
            if obs.contains(x, y):
                return True
        return False

    def is_within_bounds(self, x, y):
        """Checks if coordinates are within property bounds."""
        return 0 <= x < self.width and 0 <= y < self.height


class Bee:
    """Represents a single bee."""
    def __init__(self, id, start_x, start_y, hive, property_env, speed=1.0, capacity=1.0):
        self.id = id
        self.x = start_x
        self.y = start_y
        self.hive = hive
        self.property = property_env
        self.speed = speed
        self.state = STATE_IN_HIVE_IDLE
        self.nectar_load = 0.0
        self.capacity = capacity
        self.target = None # Can be (x, y) tuple, a Flower object, or a Cell object coords
        self.current_mission = None # 'FORAGE' or 'BUILD' - simple decision for now
        self.location = 'HIVE' # 'HIVE' or 'PROPERTY'

    def _set_target(self, target_pos):
        """Sets the target coordinates."""
        if target_pos:
             self.target = target_pos
        else:
             self.target = None # Explicitly clear target

    def _move_towards_target(self):
        """Moves the bee one step towards its target, handling obstacles simply."""
        if self.target is None:
            # Random jitter if idle in hive? Or stay still.
            if self.state == STATE_IN_HIVE_IDLE:
                 # Move slightly within hive bounds
                 dx = random.uniform(-0.5, 0.5) * self.speed
                 dy = random.uniform(-0.5, 0.5) * self.speed
                 new_x = self.x + dx
                 new_y = self.y + dy
                 # Ensure bee stays roughly within hive visual area for simplicity
                 if self.hive.x <= new_x < self.hive.x + self.hive.width and \
                    self.hive.y <= new_y < self.hive.y + self.hive.height:
                     self.x = new_x
                     self.y = new_y

            return

        target_x, target_y = self.target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < self.speed:
            # Arrived at target
            self.x = target_x
            self.y = target_y
            return True # Indicate arrival
        else:
            # Move one step
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            next_x = self.x + move_x
            next_y = self.y + move_y

            # --- Simple Obstacle Avoidance ---
            # If moving outside hive, check property obstacles
            if self.location == 'PROPERTY' and self.property.is_obstacle(next_x, next_y):
                # Simplistic: Stop if obstacle ahead. Better: Try to go around.
                # print(f"Bee {self.id} avoiding obstacle at ({next_x:.1f}, {next_y:.1f})") # Debug
                # Try a small random perturbation to get unstuck (very basic)
                angle_offset = random.uniform(-math.pi / 4, math.pi / 4)
                move_x = math.cos(math.atan2(dy, dx) + angle_offset) * self.speed
                move_y = math.sin(math.atan2(dy, dx) + angle_offset) * self.speed
                next_x = self.x + move_x
                next_y = self.y + move_y
                # Check again after perturbation
                if self.property.is_obstacle(next_x, next_y):
                    return False # Still blocked

            # Check property bounds if outside hive
            if self.location == 'PROPERTY':
                 next_x = max(0, min(self.property.width - 0.01, next_x))
                 next_y = max(0, min(self.property.height - 0.01, next_y))
            # Check hive bounds if inside hive (allow exiting via entrance)
            elif self.location == 'HIVE':
                 hive_entrance_x, hive_entrance_y = self.hive.entrance_pos
                 is_exiting = abs(self.x - hive_entrance_x) < self.hive.width / 2 and self.y < self.hive.y + 1 # Near bottom edge

                 if not is_exiting: # If not near entrance, stay within main hive area
                     next_x = max(self.hive.x, min(self.hive.x + self.hive.width - 0.01, next_x))
                     next_y = max(self.hive.y, min(self.hive.y + self.hive.height - 0.01, next_y))
                 # else: allow moving towards entrance y coordinate even if slightly below hive box


            self.x = next_x
            self.y = next_y
            return False # Not arrived yet

    def step_change(self):
        """Determines the bee's action for the current timestep."""

        # Check location based on position relative to hive entrance area
        hive_entrance_x, hive_entrance_y = self.hive.entrance_pos
        # Consider bee 'in hive' if roughly within its bounds or just below entrance
        if self.hive.x <= self.x < self.hive.x + self.hive.width and \
           self.hive.y <= self.y < self.hive.y + self.hive.height:
            self.location = 'HIVE'
        elif self.y < self.hive.y and abs(self.x - hive_entrance_x) < 2: # Near entrance outside
             # If returning and near entrance, transition to HIVE
             if self.state == STATE_RETURNING:
                 self.location = 'HIVE'
                 self.x = hive_entrance_x # Snap to entrance x
                 self.y = self.hive.y # Snap to bottom edge y
             else:
                 self.location = 'PROPERTY' # Still foraging if just left
        else:
            self.location = 'PROPERTY'


        # --- State Machine Logic ---
        arrived = self._move_towards_target()

        if self.state == STATE_IN_HIVE_IDLE:
            # Simple decision: Always forage for now
            # Could add logic to check if building is needed
            self.current_mission = 'FORAGE'
            # Find target: hive entrance to exit
            self._set_target(self.hive.entrance_pos)
            self.state = STATE_FORAGING
            # print(f"Bee {self.id} decided to FORAGE. Heading to entrance {self.target}") # Debug

        elif self.state == STATE_FORAGING:
            # If target is entrance and arrived (or passed it), find flower
            if self.target == self.hive.entrance_pos and self.location == 'PROPERTY':
                flower_target = self.property.get_closest_available_flower((self.x, self.y))
                if flower_target:
                    self._set_target((flower_target.x, flower_target.y))
                    self.target_object = flower_target # Store the flower object
                    # print(f"Bee {self.id} exited hive, targeting flower at {self.target}") # Debug
                else:
                    # No flowers available, return to hive idle? Or wander?
                    # print(f"Bee {self.id} found no available flowers. Returning to hive entrance.") # Debug
                    self._set_target(self.hive.entrance_pos)
                    self.state = STATE_RETURNING # Go back empty

            # If target is a flower and arrived
            elif self.target and hasattr(self, 'target_object') and self.target_object and arrived:
                flower = self.target_object
                nectar_to_collect = self.capacity - self.nectar_load
                if nectar_to_collect > 0:
                    collected = flower.take_nectar(nectar_to_collect * 1.1) # Ask for slightly more to ensure capacity fill if possible
                    self.nectar_load += collected
                    # print(f"Bee {self.id} collected {collected:.2f} nectar from {flower.name}. Load: {self.nectar_load:.2f}") # Debug

                # If full or flower depleted, return to hive
                if self.nectar_load >= self.capacity or flower.is_depleted():
                    self._set_target(self.hive.entrance_pos)
                    self.state = STATE_RETURNING
                    self.target_object = None
                    # print(f"Bee {self.id} returning to hive. Target: {self.target}") # Debug
                else:
                     # Flower not depleted, but bee isn't full? (Shouldn't happen with current logic)
                     # Find next closest flower
                     next_flower = self.property.get_closest_available_flower((self.x, self.y))
                     if next_flower and next_flower != flower:
                         self._set_target((next_flower.x, next_flower.y))
                         self.target_object = next_flower
                         # print(f"Bee {self.id} moving to next flower {self.target}") # Debug
                     else: # No other flowers or same one is closest
                         if not next_flower: print(f"Bee {self.id}: No other flowers, returning.") # Debug
                         self._set_target(self.hive.entrance_pos)
                         self.state = STATE_RETURNING
                         self.target_object = None


        elif self.state == STATE_RETURNING:
            # If arrived at hive entrance (or inside hive now)
            if self.location == 'HIVE':
                # Find a place to deposit nectar
                deposit_spot_local = self.hive.find_deposit_spot()
                if deposit_spot_local and self.nectar_load > 0:
                    target_global_x, target_global_y = self.hive.get_cell_global_coords(*deposit_spot_local)
                    self._set_target((target_global_x, target_global_y))
                    self.target_object = deposit_spot_local # Store local coords of target cell
                    self.state = STATE_DEPOSITING
                    # print(f"Bee {self.id} entered hive, found deposit spot {deposit_spot_local}. Target Global: {self.target}") # Debug
                else:
                    # No deposit spot or no nectar, become idle
                    # print(f"Bee {self.id} entered hive, no deposit spot or no nectar. Becoming idle.") # Debug
                    self.state = STATE_IN_HIVE_IDLE
                    self._set_target(None)
                    self.target_object = None


        elif self.state == STATE_DEPOSITING:
            # If arrived at the target cell coordinates
            if arrived and hasattr(self, 'target_object') and self.target_object:
                cell_local_x, cell_local_y = self.target_object
                cell = self.hive.get_cell(cell_local_x, cell_local_y)
                if cell:
                    deposited = cell.deposit_nectar(self.nectar_load)
                    self.nectar_load -= deposited
                    # print(f"Bee {self.id} deposited {deposited:.2f} nectar at {self.target_object}. Load left: {self.nectar_load:.2f}") # Debug
                else:
                     print(f"Error: Bee {self.id} arrived at non-existent cell {self.target_object}") # Debug

                # Finished depositing (or couldn't), become idle
                self.state = STATE_IN_HIVE_IDLE
                self._set_target(None)
                self.target_object = None

        # --- Placeholder for Building State ---
        # elif self.state == STATE_BUILDING:
        #     # Move towards build spot
        #     # If arrived, call hive.build_cell() or cell.build()
        #     # Change state back to idle
        #     pass

        # Fallback / Error check
        # else:
        #     print(f"Warning: Bee {self.id} in unknown state: {self.state}")
        #     self.state = STATE_IN_HIVE_IDLE
        #     self._set_target(None)

    # --- Interaction (Placeholder) ---
    def interact(self, other_bees):
        # Simple collision avoidance or information sharing could go here
        pass

import argparse
import csv
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random


class Simulation:
    """Orchestrates the Bee World simulation."""

    def __init__(self, args):
        self.args = args
        self.params = {}
        self.hive = None
        self.property = None
        self.bees = []
        self.timestep = 0
        self.max_timesteps = 100 # Default, override from params

        # Plotting setup
        self.fig, (self.ax_hive, self.ax_property) = plt.subplots(1, 2, figsize=(14, 7))
        self.paused = False
        if self.args.interactive:
            self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_key_press(self, event):
        """Handle key presses for interactive mode."""
        if event.key == ' ':
            self.paused = not self.paused
            print("Simulation Paused" if self.paused else "Simulation Resumed")
        elif event.key == 'q':
            plt.close(self.fig) # Allows main loop to exit
            print("Quitting simulation.")
        elif event.key == 's' and self.paused:
            print("Stepping forward...")
            self.step() # Execute one step while paused

    def load_params(self, filename):
        """Loads simulation parameters from a CSV file."""
        print(f"Loading parameters from: {filename}")
        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader) # Skip header row
                temp_params = {} # Load into a temporary dict first
                for i, row in enumerate(reader):
                    # Skip empty rows or rows that are comments (start with #)
                    if not row or not row[0] or row[0].strip().startswith('#'):
                        continue

                    if len(row) >= 2:
                        param = row[0].strip()
                        # Get value and strip comments/whitespace from the value part
                        value_str = row[1].split('#')[0].strip()

                        # Try converting to number, default to string
                        try:
                            if '.' in value_str:
                                temp_params[param] = float(value_str)
                            else:
                                temp_params[param] = int(value_str)
                        except ValueError:
                            print(f"Warning: Could not parse parameter '{param}' value '{value_str}' as number. Storing as string.")
                            temp_params[param] = value_str # Keep as string if conversion fails
                    else:
                         print(f"Warning: Skipping invalid parameter row {i+2}: {row}")

            # Now apply loaded parameters from temp_params, ensuring correct types
            self.params = temp_params # Store the processed params

            self.max_timesteps = int(self.params.get('max_timesteps', 100)) # Default 100
            self.prop_width = int(self.params.get('property_width', 50)) # Ensure int
            self.prop_height = int(self.params.get('property_height', 40)) # Ensure int
            # Ensure plot_update_interval is int
            self.params['plot_update_interval'] = int(self.params.get('plot_update_interval', 1))
            # Ensure bee parameters are correct type (already handled by initial parse, but good to check)
            self.params['num_bees'] = int(self.params.get('num_bees', 10))
            self.params['bee_speed'] = float(self.params.get('bee_speed', 1.0))
            self.params['bee_capacity'] = float(self.params.get('bee_capacity', 1.0))


            print(f"Parameters loaded: {self.params}")

        except FileNotFoundError:
            print(f"Error: Parameter file '{filename}' not found. Using defaults.")
            # Set defaults if file not found
            self.max_timesteps = 100
            self.prop_width = 50
            self.prop_height = 40
            self.params = {'max_timesteps': self.max_timesteps, 'property_width': self.prop_width, 'property_height': self.prop_height,
                           'plot_update_interval': 1, 'num_bees': 10, 'bee_speed': 1.0, 'bee_capacity': 1.0} # Basic defaults
            print(f"Using default parameters: {self.params}")

        except Exception as e:
            print(f"An unexpected error occurred loading parameters: {e}")
            # Consider setting defaults or exiting depending on severity
            exit() # Exit if params fail critically


    def load_map(self, filename):
        """Loads the environment (hive, flowers, obstacles) from a CSV file."""
        print(f"Loading map from: {filename}")
        if not hasattr(self, 'prop_width'): # Ensure params were loaded first
             print("Warning: Property dimensions not set from params, using defaults.")
             self.prop_width = 50
             self.prop_height = 40

        self.property = Property(self.prop_width, self.prop_height)

        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader) # Skip header row
                for i, row in enumerate(reader):
                    # Skip empty rows or rows that are comments (start with #)
                    if not row or not row[0] or row[0].strip().startswith('#'):
                        continue # Skip this row entirely

                    try:
                        # Strip whitespace from all elements first
                        row = [item.strip() for item in row]

                        # Helper function to get value and strip comments
                        def get_value(index, default=None):
                            if index < len(row):
                                return row[index].split('#')[0].strip() # Split at # and take first part
                            return default

                        obj_type = get_value(0).lower()
                        x = float(get_value(1))
                        y = float(get_value(2))

                        if obj_type == 'hive':
                            width = float(get_value(3))
                            height = float(get_value(4))
                            # Handle potential comment on frame_w value
                            frame_w_str = get_value(5, '5') # Default to '5' if missing
                            frame_w = int(frame_w_str)
                            self.hive = Hive(x, y, width, height, frame_w)
                            print(f"Hive created at ({x},{y}) size {width}x{height}, frame {frame_w}")
                        elif obj_type == 'obstacle':
                            width = float(get_value(3))
                            height = float(get_value(4))
                            color = get_value(5, 'gray')
                            self.property.add_obstacle(Obstacle(x, y, width, height, color))
                        elif obj_type == 'flower':
                            name = get_value(3, "Flower")
                            color = get_value(4, "purple")
                            nectar_str = get_value(5, '10.0')
                            limited_str = get_value(6, 'True')
                            regen_str = get_value(7, '0.1')

                            nectar = float(nectar_str)
                            limited = limited_str.lower() == 'true'
                            regen = float(regen_str)

                            self.property.add_flower(Flower(x, y, name, color, nectar, limited, regen))
                        else:
                            print(f"Warning: Unknown object type '{obj_type}' in map file row {i+2}.")
                    except (IndexError, ValueError, TypeError) as e: # Catch potential errors during parsing/conversion
                        print(f"Error parsing map file row {i+2}: {row} -> {e}")
                        # Decide if you want to continue or exit on row error
                        # For critical errors like hive, maybe exit later if self.hive is still None
                        continue # Continue to next row

            if not self.hive:
                print("Error: No hive definition parsed correctly from map file. Cannot start simulation.")
                exit()

            # self.property.hive = self.hive # Give property a reference back? Might not be needed.

        except FileNotFoundError:
            print(f"Error: Map file '{filename}' not found. Cannot start simulation.")
            exit()
        except Exception as e:
            print(f"An unexpected error occurred loading map: {e}")
            exit()

    def initialize_bees(self):
        """Creates the bee objects within the hive."""
        num_bees = int(self.params.get('num_bees', 10))
        bee_speed = float(self.params.get('bee_speed', 1.0))
        bee_capacity = float(self.params.get('bee_capacity', 1.0))

        if not self.hive:
             print("Error: Cannot initialize bees, hive not created.")
             return

        for i in range(num_bees):
            # Start bees randomly within the hive bounds
            start_x = self.hive.x + random.uniform(1, self.hive.width - 1)
            start_y = self.hive.y + random.uniform(1, self.hive.height - 1)
            self.bees.append(Bee(i, start_x, start_y, self.hive, self.property, bee_speed, bee_capacity))
        print(f"Initialized {num_bees} bees.")


    def plot_hive(self):
        """Plots the current state of the hive."""
        self.ax_hive.cla() # Clear previous plot
        self.ax_hive.set_title(f"Bee Hive (Time left: {self.max_timesteps - self.timestep})")
        self.ax_hive.set_xlabel("X position (local)")
        self.ax_hive.set_ylabel("Y position (local)")
        self.ax_hive.set_xlim(-1, self.hive.width + 1)
        self.ax_hive.set_ylim(-1, self.hive.height + 1)
        self.ax_hive.set_aspect('equal', adjustable='box')
        self.ax_hive.grid(True, linestyle='--', alpha=0.6)

        # Plot hive background (optional, could represent frame)
        hive_rect = patches.Rectangle((0, 0), self.hive.width, self.hive.height,
                                      linewidth=1, edgecolor='darkgoldenrod', facecolor='khaki', alpha=0.3)
        self.ax_hive.add_patch(hive_rect)


        # Plot honeycomb cells
        cell_xs, cell_ys, cell_colors = [], [], []
        for (lx, ly), cell in self.hive.cells.items():
             if cell.state == CELL_COMB_BUILT:
                 cell_xs.append(lx + 0.5) # Center of cell
                 cell_ys.append(ly + 0.5)
                 cell_colors.append(cell.get_color())

        if cell_xs: # Only plot if there are cells
             # Use scatter for cells, s is marker size squared
             self.ax_hive.scatter(cell_xs, cell_ys, c=cell_colors, marker='h', s=150, edgecolors='black', linewidth=0.5)


        # Plot bees inside the hive
        hive_bees_x = [b.x - self.hive.x for b in self.bees if b.location == 'HIVE']
        hive_bees_y = [b.y - self.hive.y for b in self.bees if b.location == 'HIVE']
        # Color bees based on state (example)
        hive_bee_colors = []
        for bee in self.bees:
             if bee.location == 'HIVE':
                 if bee.state == STATE_DEPOSITING: hive_bee_colors.append('blue')
                 elif bee.state == STATE_IN_HIVE_IDLE: hive_bee_colors.append('black')
                 else: hive_bee_colors.append('red') # Returning/Building

        if hive_bees_x:
            self.ax_hive.scatter(hive_bees_x, hive_bees_y, c=hive_bee_colors, marker='o', s=20, label='Bees (Hive)')


    def plot_property(self):
        """Plots the current state of the property."""
        self.ax_property.cla()
        self.ax_property.set_title("Property")
        self.ax_property.set_xlabel("X position")
        self.ax_property.set_ylabel("Y position")
        self.ax_property.set_xlim(-1, self.property.width + 1)
        self.ax_property.set_ylim(-1, self.property.height + 1)
        self.ax_property.set_aspect('equal', adjustable='box')
        self.ax_property.set_facecolor('lightgreen') # Background color

        # Plot Hive Location outline
        hive_rect = patches.Rectangle((self.hive.x, self.hive.y), self.hive.width, self.hive.height,
                                      linewidth=2, edgecolor='black', facecolor='khaki', alpha=0.6)
        self.ax_property.add_patch(hive_rect)
        # Plot hive entrance marker
        self.ax_property.plot(self.hive.entrance_pos[0], self.hive.entrance_pos[1], 'ko', markersize=5)


        # Plot obstacles
        for obs in self.property.obstacles:
            rect = patches.Rectangle((obs.x, obs.y), obs.width, obs.height,
                                     linewidth=1, edgecolor='black', facecolor=obs.color)
            self.ax_property.add_patch(rect)

        # Plot flowers
        flower_xs = [f.x for f in self.property.flowers]
        flower_ys = [f.y for f in self.property.flowers]
        flower_colors = [f.color for f in self.property.flowers]
        # Vary size based on nectar amount (example)
        flower_sizes = [max(5, 50 * (f.current_nectar / f.max_nectar)) if f.is_limited and f.max_nectar > 0 else 50 for f in self.property.flowers]
        flower_markers = ['*' if not f.is_depleted() else 'x' for f in self.property.flowers] # Use 'x' for depleted

        # Plot flowers individually to handle different markers
        for i, f in enumerate(self.property.flowers):
            self.ax_property.scatter(flower_xs[i], flower_ys[i], c=flower_colors[i],
                                     marker=flower_markers[i], s=flower_sizes[i],
                                     label='Flowers' if i == 0 else "") # Label only once


        # Plot bees outside the hive
        prop_bees_x = [b.x for b in self.bees if b.location == 'PROPERTY']
        prop_bees_y = [b.y for b in self.bees if b.location == 'PROPERTY']
         # Color bees based on state (example)
        prop_bee_colors = []
        for bee in self.bees:
             if bee.location == 'PROPERTY':
                 if bee.state == STATE_FORAGING: prop_bee_colors.append('red') # Foraging bee
                 elif bee.state == STATE_RETURNING: prop_bee_colors.append('blue') # Returning bee
                 else: prop_bee_colors.append('grey') # Should not happen?

        if prop_bees_x:
            self.ax_property.scatter(prop_bees_x, prop_bees_y, c=prop_bee_colors, marker='o', s=20, label='Bees (Property)')

        # self.ax_property.legend(loc='upper right', fontsize='small')


    def step(self):
        """Executes one time step of the simulation."""
        if not plt.fignum_exists(self.fig.number): # Check if plot window closed
             print("Plot window closed, ending simulation.")
             return False # Signal to stop

        # 1. Update Bees
        for bee in self.bees:
            bee.step_change()
            # bee.interact(self.bees) # Interaction step (optional)

        # 2. Update Environment (e.g., flower regeneration)
        for flower in self.property.flowers:
            flower.regenerate()

        # 3. Update Hive (if needed, e.g., comb building progress)
        # Currently comb is static after init

        # 4. Increment timestep
        self.timestep += 1

        # 5. Plotting (throttled)
        update_interval = int(self.params.get('plot_update_interval', 1))
        if self.timestep % update_interval == 0:
            self.plot_hive()
            self.plot_property()
            plt.pause(0.01) # Very small pause to allow plot to draw and process events

        # Check termination condition
        if self.timestep >= self.max_timesteps:
            print("Maximum timesteps reached.")
            return False # Signal to stop

        return True # Signal to continue


    def run(self):
        """Runs the main simulation loop."""
        if self.args.parameter_file:
            self.load_params(self.args.parameter_file)
        else:
             print("Warning: No parameter file specified. Using defaults.")
             # Set default property size if no params loaded
             self.prop_width = 50
             self.prop_height = 40


        if self.args.map_file:
            self.load_map(self.args.map_file)
        else:
             print("Error: No map file specified. Cannot run simulation.")
             return # Cannot run without a map

        if not self.hive or not self.property:
             print("Error: Hive or Property not initialized correctly.")
             return

        self.initialize_bees()

        print(f"Starting simulation. Interactive: {self.args.interactive}")
        print("Press SPACE to Pause/Resume, 's' to Step (when paused), 'q' to Quit.")

        running = True
        while running:
            if self.args.interactive:
                while self.paused:
                    if not plt.fignum_exists(self.fig.number): # Check if closed while paused
                        running = False
                        break
                    plt.pause(0.1) # Wait while paused
                if not running: break # Exit outer loop if closed

            if not plt.fignum_exists(self.fig.number):
                 running = False
                 break

            running = self.step()

            # Slow down batch mode slightly for visibility if desired
            # if not self.args.interactive:
            #    time.sleep(0.01)


        print("Simulation finished.")
        if self.args.interactive:
            print("Close the plot window to exit completely.")
            plt.show() # Keep plot open until manually closed


# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bee World Simulation")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode with plotting.")
    parser.add_argument("-f", "--map_file", type=str, default="map1.csv",
                        help="Path to the map definition CSV file (e.g., map1.csv).")
    parser.add_argument("-p", "--parameter_file", type=str, default="para1.csv",
                        help="Path to the simulation parameters CSV file (e.g., para1.csv).")

    args = parser.parse_args()

    # Force interactive mode if no map/param files specified? Or just default to files?
    # Current setup defaults to files even without -i flag. Plotting happens either way,
    # but interactivity (pause/step/quit keys) only works with -i.

    simulation = Simulation(args)
    simulation.run()

    #python beeworldgemini.py -f map1.csv -p para1.csv