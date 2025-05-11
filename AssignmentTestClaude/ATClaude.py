import math
import random
import argparse
import csv
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
from mpl_toolkits.mplot3d import Axes3D

# --- Constants ---
# Bee States
STATE_IN_HIVE_IDLE = "IN_HIVE_IDLE"
STATE_FORAGING = "FORAGING"
STATE_RETURNING = "RETURNING"
STATE_DEPOSITING = "DEPOSITING"
STATE_BUILDING = "BUILDING"  # Building comb

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
        """Build a cell. Return True if successful."""
        if self.state == CELL_EMPTY:
            self.state = CELL_COMB_BUILT
            return True
        return False

    def deposit_nectar(self, amount):
        """Deposit nectar into the cell. Return amount deposited."""
        if self.state == CELL_COMB_BUILT:
            can_deposit = self.max_nectar - self.nectar_level
            deposit_amount = min(amount, can_deposit)
            self.nectar_level += deposit_amount
            return deposit_amount  # Return how much was actually deposited
        return 0

    def get_color(self):
        """Returns a color based on state and nectar level."""
        if self.state == CELL_EMPTY:
            return 'lightgrey'  # Should not be plotted directly if empty usually
        elif self.state == CELL_COMB_BUILT:
            # Empty comb is white
            if self.nectar_level == 0:
                return 'white'
            # Brighter orange shades for more nectar (levels 1-5)
            nectar_colors = ['#FFE5CC', '#FFCC99', '#FFB266', '#FF9933', '#FF8000']
            return nectar_colors[min(int(self.nectar_level) - 1, 4)]  # Ensure bounds


class Hive:
    """Represents the beehive structure."""
    def __init__(self, x, y, width, height, frame_width=5):
        self.x = x  # Bottom-left corner X in property coordinates
        self.y = y  # Bottom-left corner Y in property coordinates
        self.width = width
        self.height = height
        # Simple entrance at the bottom middle
        self.entrance_pos = (x + width / 2, y - 0.5)  # Slightly outside bottom edge
        self.cells = {}  # Dictionary mapping (local_x, local_y) to HoneycombCell
        self.frame_width = frame_width  # Width of the initial comb stripe
        self.comb_stripe_built = False  # Flag to track if vertical stripe is built

    def initialize_cells(self):
        """Initialize all possible cell positions (empty initially)"""
        for local_y in range(int(self.height)):
            for local_x in range(int(self.width)):
                cell = HoneycombCell(local_x, local_y)
                self.cells[(local_x, local_y)] = cell

    def build_vertical_stripe(self):
        """Builds the initial vertical stripe of comb."""
        # Convert hive dimensions and frame width to integers for calculations
        hive_width_int = int(self.width)
        hive_height_int = int(self.height)
        frame_width_int = int(self.frame_width)

        # Use integer division for placement calculations
        start_x = (hive_width_int - frame_width_int) // 2
        end_x = start_x + frame_width_int

        for local_y in range(hive_height_int):
            for local_x in range(start_x, end_x):
                if 0 <= local_x < hive_width_int and 0 <= local_y < hive_height_int:
                    cell = self.cells.get((local_x, local_y))
                    if cell:
                        cell.build()  # Set cell to built state
        
        self.comb_stripe_built = True

    def get_cell_global_coords(self, local_x, local_y):
        """Convert local hive coords to global property coords."""
        return self.x + local_x + 0.5, self.y + local_y + 0.5  # Center of cell

    def get_cell_local_coords(self, global_x, global_y):
        """Convert global property coords to local hive coords."""
        local_x = int(global_x - self.x)
        local_y = int(global_y - self.y)
        return local_x, local_y

    def get_cell(self, local_x, local_y):
        """Gets a cell at local coordinates, returns None if not exists."""
        return self.cells.get((local_x, local_y))

    def find_build_spot(self):
        """Finds an empty spot to build next comb cell in the vertical stripe."""
        # Only build within the vertical stripe area
        hive_width_int = int(self.width)
        hive_height_int = int(self.height)
        start_x = (hive_width_int - int(self.frame_width)) // 2
        end_x = start_x + int(self.frame_width)
        
        # Find the first empty cell in the stripe (bottom-up)
        for local_y in range(hive_height_int):
            for local_x in range(start_x, end_x):
                cell = self.get_cell(local_x, local_y)
                if cell and cell.state == CELL_EMPTY:
                    return (local_x, local_y)  # Return empty cell coordinates
        
        # If we got here, entire vertical stripe is built
        self.comb_stripe_built = True
        return None

    def find_deposit_spot(self):
        """Finds a built comb cell with space for nectar."""
        # First check if all building is complete
        if not self.comb_stripe_built:
            return None  # Focus on building first
            
        # Iterate and find built cells that aren't full
        for cell in self.cells.values():
            if cell.state == CELL_COMB_BUILT and cell.nectar_level < cell.max_nectar:
                return (cell.x, cell.y)  # Return local coords
        
        return None  # No suitable cell found

    def is_comb_full(self):
        """Check if all comb cells in the vertical stripe are full."""
        if not self.comb_stripe_built:
            return False
            
        # Check all cells in the vertical stripe
        hive_width_int = int(self.width)
        hive_height_int = int(self.height)
        start_x = (hive_width_int - int(self.frame_width)) // 2
        end_x = start_x + int(self.frame_width)
        
        for local_y in range(hive_height_int):
            for local_x in range(start_x, end_x):
                cell = self.get_cell(local_x, local_y)
                if cell and (cell.state != CELL_COMB_BUILT or cell.nectar_level < cell.max_nectar):
                    return False  # Found a cell that's not built or not full
        
        return True  # All cells in stripe are built and full


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
        self.regen_rate = regen_rate  # Nectar regenerated per time step

    def take_nectar(self, amount):
        """A bee takes nectar from the flower."""
        taken = 0
        if self.current_nectar > 0:
            taken = min(amount, self.current_nectar)
            if self.is_limited:
                self.current_nectar -= taken
        else:
            taken = 0  # No nectar available
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
            return None  # No flowers available

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


class Mission:
    """Defines the mission objective of a bee."""
    def __init__(self, mission_type='FORAGE'):
        self.mission_type = mission_type  # 'FORAGE' or 'BUILD'
        self.target = None
        self.target_object = None
        self.status = 'ACTIVE'  # 'ACTIVE', 'COMPLETED', 'FAILED'
    
    def set_target(self, target, target_object=None):
        self.target = target
        self.target_object = target_object
    
    def complete(self):
        self.status = 'COMPLETED'
    
    def fail(self):
        self.status = 'FAILED'


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
        self.target = None  # Target coordinates (x, y)
        self.target_object = None  # Target object (flower, cell, etc.)
        self.mission = Mission('FORAGE')  # Default mission
        self.location = 'HIVE'  # 'HIVE' or 'PROPERTY'
        self.last_interaction_time = 0  # For bee interactions
        # For 3D visualization
        self.z = 0
        self.z_direction = 1 if random.random() > 0.5 else -1
        self.z_speed = 0.1 * random.random()

    def _set_target(self, target_pos):
        """Sets the target coordinates."""
        if target_pos:
            self.target = target_pos
        else:
            self.target = None  # Explicitly clear target

    def _move_towards_target(self):
        """Moves the bee one step towards its target, handling obstacles, and returns True if arrived."""
        if self.target is None:
            # Random movement if no target
            if self.state == STATE_IN_HIVE_IDLE:
                # Move slightly within hive bounds
                dx = random.uniform(-0.5, 0.5) * self.speed
                dy = random.uniform(-0.5, 0.5) * self.speed
                new_x = self.x + dx
                new_y = self.y + dy
                # Ensure bee stays roughly within hive visual area
                if self.hive.x <= new_x < self.hive.x + self.hive.width and \
                   self.hive.y <= new_y < self.hive.y + self.hive.height:
                    self.x = new_x
                    self.y = new_y
            return False  # No target to arrive at

        target_x, target_y = self.target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < self.speed:
            # Arrived at target
            self.x = target_x
            self.y = target_y
            return True  # Arrived
        else:
            # Move one step
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed
            next_x = self.x + move_x
            next_y = self.y + move_y

            # --- Obstacle Avoidance ---
            if self.location == 'PROPERTY' and self.property.is_obstacle(next_x, next_y):
                # Try to go around obstacles
                angle_offset = random.uniform(-math.pi / 3, math.pi / 3)
                move_x = math.cos(math.atan2(dy, dx) + angle_offset) * self.speed
                move_y = math.sin(math.atan2(dy, dx) + angle_offset) * self.speed
                next_x = self.x + move_x
                next_y = self.y + move_y
                
                # Check again after perturbation
                if self.property.is_obstacle(next_x, next_y):
                    # Try a more extreme avoidance angle
                    angle_offset = random.uniform(-math.pi / 2, math.pi / 2)
                    move_x = math.cos(math.atan2(dy, dx) + angle_offset) * self.speed
                    move_y = math.sin(math.atan2(dy, dx) + angle_offset) * self.speed
                    next_x = self.x + move_x
                    next_y = self.y + move_y
                    
                    if self.property.is_obstacle(next_x, next_y):
                        return False  # Still blocked

            # Check property bounds if outside hive
            if self.location == 'PROPERTY':
                next_x = max(0, min(self.property.width - 0.01, next_x))
                next_y = max(0, min(self.property.height - 0.01, next_y))
            # Check hive bounds if inside hive (allow exiting via entrance)
            elif self.location == 'HIVE':
                hive_entrance_x, hive_entrance_y = self.hive.entrance_pos
                is_exiting = abs(self.x - hive_entrance_x) < self.hive.width / 2 and self.y < self.hive.y + 1  # Near bottom edge

                if not is_exiting:  # If not near entrance, stay within main hive area
                    next_x = max(self.hive.x, min(self.hive.x + self.hive.width - 0.01, next_x))
                    next_y = max(self.hive.y, min(self.hive.y + self.hive.height - 0.01, next_y))

            self.x = next_x
            self.y = next_y
            
            # Update z position for 3D visualization (simple oscillation)
            if self.location == 'PROPERTY':
                self.z += self.z_direction * self.z_speed
                if abs(self.z) > 1.0:  # Keep the z movement within bounds
                    self.z_direction *= -1
            else:
                self.z = 0  # No z movement inside hive
                
            return False  # Not arrived yet

    def update_location(self):
        """Update whether the bee is in the hive or on the property based on position."""
        hive_entrance_x, hive_entrance_y = self.hive.entrance_pos
        
        # Consider bee 'in hive' if roughly within its bounds or just below entrance
        if self.hive.x <= self.x < self.hive.x + self.hive.width and \
           self.hive.y <= self.y < self.hive.y + self.hive.height:
            self.location = 'HIVE'
        elif self.y < self.hive.y and abs(self.x - hive_entrance_x) < 2:  # Near entrance outside
            # If returning and near entrance, transition to HIVE
            if self.state == STATE_RETURNING:
                self.location = 'HIVE'
                self.x = hive_entrance_x  # Snap to entrance x
                self.y = self.hive.y  # Snap to bottom edge y
            else:
                self.location = 'PROPERTY'  # Still foraging if just left
        else:
            self.location = 'PROPERTY'

    def decide_mission(self):
        """Decide what mission the bee should undertake."""
        # If vertical stripe not built, prioritize building
        if not self.hive.comb_stripe_built and self.state == STATE_IN_HIVE_IDLE:
            build_spot = self.hive.find_build_spot()
            if build_spot:
                self.mission = Mission('BUILD')
                return
        
        # Otherwise, forage for nectar
        self.mission = Mission('FORAGE')

    def step_change(self):
        """Determines the bee's action for the current timestep."""
        # Update location based on position
        self.update_location()

        # State machine logic
        arrived = self._move_towards_target()

        # Update state based on current state and conditions
        if self.state == STATE_IN_HIVE_IDLE:
            # Decide whether to build or forage
            self.decide_mission()
            
            if self.mission.mission_type == 'BUILD':
                # Find a spot to build comb
                build_spot = self.hive.find_build_spot()
                if build_spot:
                    # Set target to the build spot
                    local_x, local_y = build_spot
                    global_x, global_y = self.hive.get_cell_global_coords(local_x, local_y)
                    self._set_target((global_x, global_y))
                    self.target_object = build_spot
                    self.state = STATE_BUILDING
                else:
                    # Default to foraging if no build spot
                    self.mission = Mission('FORAGE')
                    self._set_target(self.hive.entrance_pos)
                    self.state = STATE_FORAGING
            else:  # FORAGE mission
                # Find target: hive entrance to exit
                self._set_target(self.hive.entrance_pos)
                self.state = STATE_FORAGING

        elif self.state == STATE_BUILDING:
            # If we've arrived at the build spot
            if arrived and self.target_object:
                local_x, local_y = self.target_object
                cell = self.hive.get_cell(local_x, local_y)
                if cell and cell.state == CELL_EMPTY:
                    # We need 1 unit of nectar to build a cell
                    if self.nectar_load >= 1.0:
                        cell.build()
                        self.nectar_load -= 1.0
                        self.state = STATE_IN_HIVE_IDLE
                        self._set_target(None)
                        self.target_object = None
                    else:
                        # Need more nectar for building, go foraging
                        self._set_target(self.hive.entrance_pos)
                        self.state = STATE_FORAGING
                else:
                    # Cell already built or doesn't exist, go idle
                    self.state = STATE_IN_HIVE_IDLE
                    self._set_target(None)
                    self.target_object = None

        elif self.state == STATE_FORAGING:
            # If target is entrance and arrived (or passed it), find flower
            if self.target == self.hive.entrance_pos and self.location == 'PROPERTY':
                flower_target = self.property.get_closest_available_flower((self.x, self.y))
                if flower_target:
                    self._set_target((flower_target.x, flower_target.y))
                    self.target_object = flower_target  # Store the flower object
                else:
                    # No flowers available, return to hive
                    self._set_target(self.hive.entrance_pos)
                    self.state = STATE_RETURNING  # Go back empty

            # If target is a flower and arrived
            elif self.target and hasattr(self, 'target_object') and self.target_object and arrived:
                flower = self.target_object
                nectar_to_collect = self.capacity - self.nectar_load
                if nectar_to_collect > 0:
                    collected = flower.take_nectar(nectar_to_collect)
                    self.nectar_load += collected

                # If full or flower depleted, return to hive
                if self.nectar_load >= self.capacity or flower.is_depleted():
                    self._set_target(self.hive.entrance_pos)
                    self.state = STATE_RETURNING
                    self.target_object = None
                else:
                    # Flower not depleted, but bee isn't full
                    next_flower = self.property.get_closest_available_flower((self.x, self.y))
                    if next_flower and next_flower != flower:
                        self._set_target((next_flower.x, next_flower.y))
                        self.target_object = next_flower
                    else:  # No other flowers or same one is closest
                        self._set_target(self.hive.entrance_pos)
                        self.state = STATE_RETURNING
                        self.target_object = None

        elif self.state == STATE_RETURNING:
            # If arrived at hive entrance (or inside hive now)
            if self.location == 'HIVE':
                # First check if we were building and need to continue
                if self.mission.mission_type == 'BUILD' and not self.hive.comb_stripe_built:
                    build_spot = self.hive.find_build_spot()
                    if build_spot and self.nectar_load >= 1.0:
                        local_x, local_y = build_spot
                        global_x, global_y = self.hive.get_cell_global_coords(local_x, local_y)
                        self._set_target((global_x, global_y))
                        self.target_object = build_spot
                        self.state = STATE_BUILDING
                        return
                
                # Find a place to deposit nectar
                deposit_spot_local = self.hive.find_deposit_spot()
                if deposit_spot_local and self.nectar_load > 0:
                    target_global_x, target_global_y = self.hive.get_cell_global_coords(*deposit_spot_local)
                    self._set_target((target_global_x, target_global_y))
                    self.target_object = deposit_spot_local  # Store local coords of target cell
                    self.state = STATE_DEPOSITING
                else:
                    # No deposit spot or no nectar, become idle
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

                # Finished depositing (or couldn't), become idle
                self.state = STATE_IN_HIVE_IDLE
                self._set_target(None)
                self.target_object = None

    def interact(self, other_bees):
        """Interact with other bees."""
        current_time = time.time()
        
        # Only interact occasionally to avoid constant checking
        if current_time - self.last_interaction_time < 0.5:  # Once per half second
            return
            
        self.last_interaction_time = current_time
        
        # Simple interaction: copy mission type from nearby bee if they're successful
        if self.state == STATE_IN_HIVE_IDLE:
            for bee in other_bees:
                if bee.id != self.id and bee.location == self.location:
                    # Calculate distance
                    dist = math.sqrt((bee.x - self.x)**2 + (bee.y - self.y)**2)
                    if dist < 2.0:  # Close enough to interact
                        # If other bee has nectar and is depositing or returned recently
                        if (bee.state == STATE_DEPOSITING or bee.state == STATE_RETURNING) and bee.nectar_load > 0:
                            # Adopt their mission type
                            self.mission.mission_type = bee.mission.mission_type
                            break


class Simulation:
    """Orchestrates the Bee World simulation."""

    def __init__(self, args):
        self.args = args
        self.params = {}
        self.hive = None
        self.property = None
        self.bees = []
        self.timestep = 0
        self.max_timesteps = 100  # Default, override from params
        self.is_3d = False  # Flag for 3D mode

        # Plotting setup
        plt.style.use('dark_background' if args.dark_mode else 'default')
        if self.args.mode_3d:
            self.is_3d = True
            self.fig = plt.figure(figsize=(14, 7))
            self.ax_hive = self.fig.add_subplot(1, 2, 1)
            self.ax_property = self.fig.add_subplot(1, 2, 2, projection='3d')
        else:
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
            plt.close(self.fig)  # Allows main loop to exit
            print("Quitting simulation.")
        elif event.key == 's' and self.paused:
            print("Stepping forward...")
            self.step()  # Execute one step while paused
        elif event.key == '3':
            # Toggle 3D mode
            self.toggle_3d_mode()

    def toggle_3d_mode(self):
        """Toggle between 2D and 3D visualization."""
        if self.is_3d:
            # Switch to 2D
            plt.close(self.fig)
            self.fig, (self.ax_hive, self.ax_property) = plt.subplots(1, 2, figsize=(14, 7))
            self.is_3d = False
            print("Switched to 2D visualization")
        else:
            # Switch to 3D
            plt.close(self.fig)
            self.fig = plt.figure(figsize=(14, 7))
            self.ax_hive = self.fig.add_subplot(1, 2, 1)
            self.ax_property = self.fig.add_subplot(1, 2, 2, projection='3d')
            self.is_3d = True
            print("Switched to 3D visualization")
            
        # Reconnect key events
        if self.args.interactive:
            self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

    def load_params(self, filename):
        """Loads simulation parameters from a CSV file."""
        print(f"Loading parameters from: {filename}")
        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header row
                temp_params = {}  # Load into a temporary dict first
                for i, row in enumerate(reader):
                    # Skip empty rows or rows that are comments (start with #)
                    if not row or not row[0] or row[0].strip().startswith('#'):
                        continue

                    if len(row) >= 2:
                        param = row[0].strip()
                        # Get value and strip comments/whitespace from the value part
                        value_str = row[1].split('#')[0].strip()