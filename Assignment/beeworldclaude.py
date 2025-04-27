
# BeeWorld Simulation
# 
# A simulation of bee behavior, honey production, and environmental interaction

import matplotlib.pyplot as plt
import numpy as np
import random
import argparse
import csv
import math
from enum import Enum

class BeeState(Enum):
    """Enum representing possible states of a bee"""
    IDLE = 0
    SEEKING_NECTAR = 1
    RETURNING_WITH_NECTAR = 2
    DEPOSITING_NECTAR = 3
    BUILDING_COMB = 4

class Bee:
    """Represents a bee in the simulation with position, state, and behavior"""
    def __init__(self, ID, pos):
        """
        Initialize Bee object
        ID:  identifier for the bee
        pos: (x,y) position of bee
        age: set to zero at birth
        inhive: is the bee inside the hive or out in the world? True at birth
        """
        self.ID = ID
        self.pos = pos
        self.age = 0
        self.inhive = True
        self.state = BeeState.IDLE
        self.nectar_carried = 0
        self.max_nectar_capacity = 2
        self.current_mission = None
        self.visited_flowers = set()  # Track visited flowers to avoid revisiting empty ones
    
    def step_change(self, world_map=None, mission_manager=None, hive_map=None, flower_list=None, 
                   maxX=None, maxY=None, hive_position=None):
        """
        Update Bee object on each timestep based on its current state and mission
        """
        # If bee has a mission, execute mission logic
        if self.current_mission:
            self.current_mission.execute(self)
            return
            
        # Basic movement logic (when no mission is active)
        validmoves = [(0,0), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
        
        # Try to find a valid move that keeps the bee within boundaries
        valid_step = False
        attempts = 0
        max_attempts = 10  # Prevent infinite loop
        
        while not valid_step and attempts < max_attempts:
            move = random.choice(validmoves)
            newX = self.pos[0] + move[0]
            newY = self.pos[1] + move[1]
            
            # Check if new position is within boundaries
            if self.inhive:
                if hive_map is not None:
                    # Check hive boundaries
                    if 0 <= newX < hive_map.shape[0] and 0 <= newY < hive_map.shape[1]:
                        valid_step = True
            else:
                if world_map is not None:
                    # Check world boundaries and make sure it's not a barrier
                    if (0 <= newX < world_map.shape[0] and 0 <= newY < world_map.shape[1] and
                        world_map[newX, newY] != 14):  # 14 is barrier value
                        valid_step = True
            
            attempts += 1
        
        if valid_step:
            print(f"{self.ID}: {self.pos} -> {(newX, newY)}")
            self.pos = (newX, newY)
        else:
            print(f"{self.ID}: Staying at {self.pos} (no valid moves)")
        
        # Age with each step
        self.age += 1
        
        # If idle in the hive for too long, assign a nectar collection mission
        if self.inhive and self.state == BeeState.IDLE and random.random() < 0.3:
            if mission_manager:
                mission_manager.assign_nectar_mission(self)
    
    def find_exit_path(self, hive_map, hive_position):
        """Find the shortest path to exit the hive"""
        # Simple implementation - move toward the center of the hive exit
        exit_x = hive_position[0] + 1  # Middle of the hive exit
        exit_y = hive_position[1] + 1
        
        # Calculate the direction to move (simplified)
        dx = exit_x - self.pos[0]
        dy = exit_y - self.pos[1]
        
        # Normalize to get a single-step direction
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        
        return dx, dy
    
    def find_nearest_flower(self, flower_list):
        """Find the nearest flower that still has nectar"""
        nearest_flower = None
        min_distance = float('inf')
        
        for flower in flower_list:
            if flower.nectar > 0 and flower not in self.visited_flowers:
                distance = self.distance_to(flower.pos)
                if distance < min_distance:
                    min_distance = distance
                    nearest_flower = flower
        
        # If all known flowers are empty, reset visited set to try them again
        if nearest_flower is None and len(self.visited_flowers) > 0:
            self.visited_flowers.clear()
            return self.find_nearest_flower(flower_list)
            
        return nearest_flower
    
    def distance_to(self, target_pos):
        """Calculate distance to target position"""
        return math.sqrt((self.pos[0] - target_pos[0])**2 + (self.pos[1] - target_pos[1])**2)
    
    def move_toward(self, target_pos, world_map=None):
        """Move one step toward target position, avoiding barriers"""
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        
        # Determine step direction
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)
        
        # Try to move in the determined direction
        new_x = self.pos[0] + step_x
        new_y = self.pos[1] + step_y
        
        # Check if move is valid (within bounds and not a barrier)
        if world_map is not None:
            if (0 <= new_x < world_map.shape[0] and 
                0 <= new_y < world_map.shape[1] and
                world_map[new_x, new_y] != 14):  # 14 is barrier value
                self.pos = (new_x, new_y)
                return True
            
            # Try alternate moves if direct path is blocked
            alternate_moves = [(step_x, 0), (0, step_y), (step_x, -step_y), (-step_x, step_y)]
            
            for move in alternate_moves:
                alt_x = self.pos[0] + move[0]
                alt_y = self.pos[1] + move[1]
                
                if (0 <= alt_x < world_map.shape[0] and 
                    0 <= alt_y < world_map.shape[1] and
                    world_map[alt_x, alt_y] != 14):
                    self.pos = (alt_x, alt_y)
                    return True
        
        return False
    
    def get_pos(self):
        return self.pos
    
    def get_inhive(self):
        return self.inhive
    
    def set_inhive(self, value):
        self.inhive = value
    
    def collect_nectar(self, flower):
        """Collect nectar from a flower"""
        amount_to_collect = min(flower.nectar, self.max_nectar_capacity - self.nectar_carried)
        
        if amount_to_collect > 0:
            flower.nectar -= amount_to_collect
            self.nectar_carried += amount_to_collect
            print(f"{self.ID}: Collected {amount_to_collect} nectar from {flower.name}")
            
            if flower.nectar <= 0:
                self.visited_flowers.add(flower)
                
            return True
        return False
    
    def deposit_nectar(self, hive_comb):
        """Deposit nectar into hive comb"""
        if self.nectar_carried > 0 and hive_comb is not None:
            cell = hive_comb.find_empty_cell(self.pos)
            
            if cell:
                amount_deposited = min(self.nectar_carried, 5 - cell.nectar_level)
                cell.nectar_level += amount_deposited
                self.nectar_carried -= amount_deposited
                print(f"{self.ID}: Deposited {amount_deposited} nectar in cell at {cell.pos}")
                return True
        
        return False


class Mission:
    """Base class for bee missions"""
    def __init__(self):
        self.completed = False
    
    def execute(self, bee):
        """Execute mission logic for the bee"""
        pass


class NectarMission(Mission):
    """Mission to collect nectar and return it to the hive"""
    def __init__(self, hive_position, flower_list, world_map, hive_map, hive_comb):
        super().__init__()
        self.hive_position = hive_position
        self.flower_list = flower_list
        self.world_map = world_map
        self.hive_map = hive_map
        self.hive_comb = hive_comb
        self.target_flower = None
        self.phase = "exit_hive"  # phases: exit_hive, find_flower, return_to_hive, deposit
    
    def execute(self, bee):
        """Execute the nectar collection mission"""
        if self.phase == "exit_hive":
            # Exit the hive
            if bee.inhive:
                dx, dy = bee.find_exit_path(self.hive_map, self.hive_position)
                new_x = bee.pos[0] + dx
                new_y = bee.pos[1] + dy
                
                # Check if at exit point
                exit_x = self.hive_position[0] + 1
                exit_y = self.hive_position[1] + 1
                
                if (new_x, new_y) == (exit_x, exit_y):
                    # Transition to world coordinates
                    bee.pos = self.hive_position
                    bee.set_inhive(False)
                    bee.state = BeeState.SEEKING_NECTAR
                    self.phase = "find_flower"
                    print(f"{bee.ID}: Exited hive, now seeking flowers")
                else:
                    bee.pos = (new_x, new_y)
            else:
                self.phase = "find_flower"
        
        elif self.phase == "find_flower":
            if not self.target_flower or self.target_flower.nectar <= 0:
                self.target_flower = bee.find_nearest_flower(self.flower_list)
                
            if self.target_flower:
                # Move toward the flower
                if bee.distance_to(self.target_flower.pos) <= 1:
                    # At flower, collect nectar
                    success = bee.collect_nectar(self.target_flower)
                    if success and bee.nectar_carried >= bee.max_nectar_capacity:
                        self.phase = "return_to_hive"
                        bee.state = BeeState.RETURNING_WITH_NECTAR
                        print(f"{bee.ID}: Nectar collected, returning to hive")
                else:
                    bee.move_toward(self.target_flower.pos, self.world_map)
            else:
                # No flowers with nectar, return to hive
                self.phase = "return_to_hive"
                print(f"{bee.ID}: No flowers with nectar found, returning to hive")
        
        elif self.phase == "return_to_hive":
            # Return to hive entrance
            hive_entrance = (self.hive_position[0] + 1, self.hive_position[1] + 1)
            
            if bee.distance_to(hive_entrance) <= 1:
                # Enter hive
                bee.set_inhive(True)
                bee.pos = hive_entrance
                self.phase = "deposit"
                bee.state = BeeState.DEPOSITING_NECTAR
                print(f"{bee.ID}: Reached hive, preparing to deposit nectar")
            else:
                bee.move_toward(hive_entrance, self.world_map)
        
        elif self.phase == "deposit":
            # Deposit nectar in honeycomb
            if bee.deposit_nectar(self.hive_comb):
                if bee.nectar_carried <= 0:
                    # Mission complete
                    bee.state = BeeState.IDLE
                    self.completed = True
                    print(f"{bee.ID}: Mission completed")
                    bee.current_mission = None
            else:
                # Try to find a suitable cell
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                new_x = bee.pos[0] + dx
                new_y = bee.pos[1] + dy
                
                # Ensure position is within hive bounds
                if (0 <= new_x < self.hive_map.shape[0] and 
                    0 <= new_y < self.hive_map.shape[1]):
                    bee.pos = (new_x, new_y)


class CombBuildMission(Mission):
    """Mission to build honeycomb in the hive"""
    def __init__(self, hive_comb):
        super().__init__()
        self.hive_comb = hive_comb
        self.target_cell = None
    
    def execute(self, bee):
        """Execute the comb building mission"""
        if not self.target_cell:
            # Find a suitable location to build comb
            self.target_cell = self.hive_comb.find_build_location(bee.pos)
        
        if self.target_cell:
            if bee.distance_to(self.target_cell.pos) <= 1:
                # Build comb
                self.target_cell.has_comb = True
                print(f"{bee.ID}: Built comb at {self.target_cell.pos}")
                bee.state = BeeState.IDLE
                self.completed = True
                bee.current_mission = None
            else:
                # Move toward target cell
                dx = self.target_cell.pos[0] - bee.pos[0]
                dy = self.target_cell.pos[1] - bee.pos[1]
                
                step_x = 0 if dx == 0 else dx // abs(dx)
                step_y = 0 if dy == 0 else dy // abs(dy)
                
                new_x = bee.pos[0] + step_x
                new_y = bee.pos[1] + step_y
                
                if (0 <= new_x < self.hive_comb.width and 
                    0 <= new_y < self.hive_comb.height):
                    bee.pos = (new_x, new_y)
        else:
            # No suitable building location, mission complete
            bee.state = BeeState.IDLE
            self.completed = True
            bee.current_mission = None

class MissionManager:
    """Manages bee missions"""
    def __init__(self, hive_position, flower_list, world_map, hive_map, hive_comb):
        self.hive_position = hive_position
        self.flower_list = flower_list
        self.world_map = world_map
        self.hive_map = hive_map
        self.hive_comb = hive_comb
    
    def assign_nectar_mission(self, bee):
        """Assign a nectar collection mission to a bee"""
        # Check if comb exists first
        if self.hive_comb.has_comb_cells():
            mission = NectarMission(
                self.hive_position,
                self.flower_list,
                self.world_map,
                self.hive_map,
                self.hive_comb
            )
            bee.current_mission = mission
            bee.state = BeeState.SEEKING_NECTAR
            print(f"{bee.ID}: Assigned nectar collection mission")
        else:
            # No comb cells yet, assign comb building mission
            self.assign_comb_building_mission(bee)
    
    def assign_comb_building_mission(self, bee):
        """Assign a comb building mission to a bee"""
        mission = CombBuildMission(self.hive_comb)
        bee.current_mission = mission
        bee.state = BeeState.BUILDING_COMB
        print(f"{bee.ID}: Assigned comb building mission")

class HoneycombCell:
    """Represents a single cell in the honeycomb"""
    def __init__(self, pos):
        self.pos = pos
        self.has_comb = False  # Whether this cell has comb built
        self.nectar_level = 0  # Amount of nectar stored (0-5)

class Honeycomb:
    """Represents the honeycomb structure in the hive"""
    def __init__(self, width, height, frame_positions):
        self.width = width
        self.height = height
        self.frame_positions = frame_positions  # List of (x, y, width, height) tuples for frames
        self.cells = {}  # Dictionary mapping positions to HoneycombCell objects
        
        # Initialize cells for each frame
        for frame in frame_positions:
            x, y, w, h = frame
            for i in range(x, x + w):
                for j in range(y, y + h):
                    self.cells[(i, j)] = HoneycombCell((i, j))
    
    def find_empty_cell(self, bee_pos):
        """Find nearest cell that has comb and can store more nectar"""
        nearest_cell = None
        min_distance = float('inf')
        
        for pos, cell in self.cells.items():
            if cell.has_comb and cell.nectar_level < 5:
                # Cell has comb and isn't full
                distance = math.sqrt((bee_pos[0] - pos[0])**2 + (bee_pos[1] - pos[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cell = cell
        
        return nearest_cell
    
    def find_build_location(self, bee_pos):
        """Find a location to build new comb"""
        # Find cells without comb, prioritizing those adjacent to existing comb
        candidates = []
        
        for pos, cell in self.cells.items():
            if not cell.has_comb:
                # Check if adjacent to existing comb
                has_adjacent_comb = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor_pos = (pos[0] + dx, pos[1] + dy)
                    if neighbor_pos in self.cells and self.cells[neighbor_pos].has_comb:
                        has_adjacent_comb = True
                        break
                
                if has_adjacent_comb:
                    # Higher priority for cells adjacent to existing comb
                    distance = math.sqrt((bee_pos[0] - pos[0])**2 + (bee_pos[1] - pos[1])**2)
                    candidates.append((cell, distance, 0))  # Lower priority value = higher priority
                else:
                    # Lower priority for isolated cells
                    distance = math.sqrt((bee_pos[0] - pos[0])**2 + (bee_pos[1] - pos[1])**2)
                    candidates.append((cell, distance, 1))
        
        if not candidates:
            return None
            
        # Sort by priority first, then by distance
        candidates.sort(key=lambda x: (x[2], x[1]))
        return candidates[0][0] if candidates else None
    
    def has_comb_cells(self):
        """Check if any cells have comb built"""
        return any(cell.has_comb for cell in self.cells.values())
    
    def get_comb_map(self):
        """Return a map indicating comb and nectar levels"""
        comb_map = np.zeros((self.width, self.height))
        
        for pos, cell in self.cells.items():
            if cell.has_comb:
                # Scale nectar level (0-5) to color range (5-10)
                comb_map[pos[0], pos[1]] = 5 + cell.nectar_level
            else:
                # Empty frame cell
                comb_map[pos[0], pos[1]] = 2
        
        return comb_map


class Flower:
    """Represents a flower in the world"""
    def __init__(self, name, pos, color, nectar):
        self.name = name
        self.pos = pos
        self.color = color  # Color code for plotting
        self.nectar = nectar
        self.max_nectar = nectar
    
    def regenerate_nectar(self, amount=0.1):
        """Regenerate some nectar over time"""
        if self.nectar < self.max_nectar:
            self.nectar = min(self.max_nectar, self.nectar + amount)


class Tree:
    """Represents a tree in the world"""
    def __init__(self, name, pos, size, has_flowers=False):
        self.name = name
        self.pos = pos  # Center position
        self.size = size  # Radius or size factor
        self.has_flowers = has_flowers
        self.flowers = []
        
        if has_flowers:
            # Create some flowers on the tree
            num_flowers = random.randint(2, 5)
            for i in range(num_flowers):
                # Place flowers around the tree
                flower_x = pos[0] + random.randint(-size, size)
                flower_y = pos[1] + random.randint(-size, size)
                flower_name = f"{name}_flower_{i}"
                flower_nectar = random.uniform(1, 3)
                
                flower = Flower(flower_name, (flower_x, flower_y), 17, flower_nectar)  # 17 = bright color
                self.flowers.append(flower)


def plot_hive(hive, blist, honeycomb, ax, simlength):
    """Plot the beehive with bees and honeycomb"""
    # Base hive coloring
    hive_base = np.ones_like(hive) * 2  # Light color for background
    
    # Add frames
    for frame in honeycomb.frame_positions:
        x, y, w, h = frame
        hive_base[x:x+w, y:y+h] = 3  # Frame color
    
    # Add comb and nectar information
    comb_map = honeycomb.get_comb_map()
    for pos, cell in honeycomb.cells.items():
        if cell.has_comb:
            # Use nectar level to determine color (brighter = more nectar)
            hive_base[pos[0], pos[1]] = 5 + cell.nectar_level
    
    # Get bee positions
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    
    # Plot the hive
    ax.imshow(hive_base.T, origin="lower", cmap='YlOrBr', vmin=0, vmax=10)
    
    # Plot the bees with colors based on their state
    colors = []
    for b in blist:
        if b.get_inhive():
            if b.state == BeeState.IDLE:
                colors.append('black')
            elif b.state == BeeState.BUILDING_COMB:
                colors.append('blue')
            elif b.state == BeeState.DEPOSITING_NECTAR:
                colors.append('green')
            else:
                colors.append('red')
    
    ax.scatter(xvalues, yvalues, c=colors, marker='o')
    
    # Add time counter
    ax.text(0.05, 0.95, f"Time left: {simlength}", transform=ax.transAxes, fontsize=12)


def plot_world(world, blist, flower_list, trees, ax, hive_position):
    """Plot the world with bees, flowers, and terrain"""
    # Base world coloring
    world_base = np.copy(world)
    
    # Add hive position
    world_base[hive_position[0]:hive_position[0]+2, hive_position[1]:hive_position[1]+2] = 16  # White for hive
    
    # Get bee positions
    xvalues = [b.get_pos()[0] for b in blist if not b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if not b.get_inhive()]
    
    # Get bee colors based on state
    colors = []
    for b in blist:
        if not b.get_inhive():
            if b.state == BeeState.SEEKING_NECTAR:
                colors.append('yellow')
            elif b.state == BeeState.RETURNING_WITH_NECTAR:
                colors.append('orange')
            else:
                colors.append('black')
    
    # Plot the world
    ax.imshow(world_base.T, origin="lower", cmap='tab20', vmin=0, vmax=19)
    
    # Plot trees
    for tree in trees:
        circle = plt.Circle(
            (tree.pos[0], tree.pos[1]), 
            tree.size, 
            color='green', 
            alpha=0.7
        )
        ax.add_patch(circle)
    
    # Plot flowers
    flower_x = [f.pos[0] for f in flower_list]
    flower_y = [f.pos[1] for f in flower_list]
    flower_sizes = [20 * (1 + f.nectar/f.max_nectar) for f in flower_list]
    ax.scatter(flower_x, flower_y, c='purple', marker='*', s=flower_sizes)
    
    # Plot the bees
    ax.scatter(xvalues, yvalues, c=colors, marker='o', s=80)


def read_terrain_file(filename):
    """Read terrain configuration from CSV file"""
    world = None
    flowers = []
    trees = []
    hive_position = None
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        
        # Parse dimensions
        width = int(header[0])
        height = int(header[1])
        world = np.zeros((width, height))
        
        # Parse terrain elements
        for row in reader:
            if len(row) < 1:
                continue
                
            element_type = row[0].strip().lower()
            
            if element_type == "hive":
                # Hive: x, y
                hive_position = (int(row[1]), int(row[2]))
            
            elif element_type == "pond":
                # Pond: x, y, width, height
                x, y, w, h = int(row[1]), int(row[2]), int(row[3]), int(row[4])
                world[x:x+w, y:y+h] = 0  # Blue color for pond
            
            elif element_type == "barrier":
                # Barrier: x, y, width, height
                x, y, w, h = int(row[1]), int(row[2]), int(row[3]), int(row[4])
                world[x:x+w, y:y+h] = 14  # Gray for barrier
            
            elif element_type == "flower":
                # Flower: name, x, y, nectar
                name = row[1]
                x, y = int(row[2]), int(row[3])
                nectar = float(row[4]) if len(row) > 4 else 2.0
                
                flower = Flower(name, (x, y), 17, nectar)
                flowers.append(flower)
            
            elif element_type == "tree":
                # Tree: name, x, y, size, has_flowers
                name = row[1]
                x, y = int(row[2]), int(row[3])
                size = int(row[4])
                has_flowers = row[5].lower() == "true" if len(row) > 5 else False
                
                tree = Tree(name, (x, y), size, has_flowers)
                trees.append(tree)
                if has_flowers:
                    flowers.extend(tree.flowers)
    
    # Set default terrain
    if world is None:
        world = np.zeros((50, 40))
        world[:, :] = 5  # Green background
    
    # Set default hive position if not specified
    if hive_position is None:
        hive_position = (22, 20)
    
    return world, flowers, trees, hive_position


def read_parameter_file(filename):
    """Read simulation parameters from CSV file"""
    params = {
        'num_bees': 5,
        'sim_length': 20,
        'hive_size_x': 30, 
        'hive_size_y': 25,
        'world_size_x': 50,
        'world_size_y': 40,
        'frames': [(10, 5, 10, 15)]  # Default frame position: x, y, width, height
    }
    
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    continue
                    
                param_name = row[0].strip().lower()
                
                if param_name == "num_bees":
                    params['num_bees'] = int(row[1])
                
                elif param_name == "sim_length":
                    params['sim_length'] = int(row[1])
                
                elif param_name == "hive_size":
                    params['hive_size_x'] = int(row[1])
                    params['hive_size_y'] = int(row[2]) if len(row) > 2 else int(row[1])
                
                elif param_name == "world_size":
                    params
                
                elif param_name == "world_size":
                    params['world_size_x'] = int(row[1])
                    params['world_size_y'] = int(row[2]) if len(row) > 2 else int(row[1])
                
                elif param_name == "frame":
                    # Frame: x, y, width, height
                    if len(row) >= 5:
                        frame = (int(row[1]), int(row[2]), int(row[3]), int(row[4]))
                        if 'frames' not in params:
                            params['frames'] = []
                        params['frames'].append(frame)
    except FileNotFoundError:
        print(f"Parameter file {filename} not found, using defaults")
    
    return params

def run_simulation(interactive=False, terrain_file=None, parameter_file=None):
    """Run the BeeWorld simulation"""
    # Load parameters
    if parameter_file:
        params = read_parameter_file(parameter_file)
    else:
        params = {
            'num_bees': 5,
            'sim_length': 20,
            'hive_size_x': 30, 
            'hive_size_y': 25,
            'world_size_x': 50,
            'world_size_y': 40,
            'frames': [(10, 5, 10, 15)]  # Default frame position: x, y, width, height
        }
    
    # Load terrain
    if terrain_file:
        world, flowers, trees, hive_position = read_terrain_file(terrain_file)
    else:
        # Create default world
        world = np.zeros((params['world_size_x'], params['world_size_y']))
        world[:, :] = 5  # Green background
        
        # Add some terrain features
        world[30:39, 5:10] = 0  # Blue pond
        world[10:15, 30:35] = 14  # Gray barrier
        
        # Add checkerboard pattern in one quadrant
        for x in range(params['world_size_x']//2, params['world_size_x']):
            if x % 2 == 0:
                for y in range(params['world_size_y']//2, params['world_size_y']):
                    if y % 2 == 0:
                        world[x, y] = 5  # Green
                    else:
                        world[x, y] = 8  # Brown
            else:
                for y in range(params['world_size_y']//2, params['world_size_y']):
                    world[x, y] = 5  # Green
        
        # Add default flowers
        flowers = [
            Flower("flower1", (15, 15), 17, 3.0),
            Flower("flower2", (25, 35), 17, 2.5),
            Flower("flower3", (35, 15), 17, 2.0),
            Flower("flower4", (45, 25), 17, 3.5)
        ]
        
        # Add default trees
        trees = [
            Tree("oak", (10, 25), 3, True),
            Tree("maple", (40, 35), 2, True)
        ]
        
        # Add tree flowers to flower list
        for tree in trees:
            if tree.has_flowers:
                flowers.extend(tree.flowers)
        
        # Default hive position
        hive_position = (22, 20)
    
    # Create hive
    hive_size_x = params['hive_size_x']
    hive_size_y = params['hive_size_y']
    hive = np.zeros((hive_size_x, hive_size_y))
    
    # Create honeycomb frames
    honeycomb = Honeycomb(hive_size_x, hive_size_y, params['frames'])
    
    # Create bees
    blist = [
        Bee(f"b{i+1}", 
            (np.random.randint(0, hive_size_x), np.random.randint(0, hive_size_y))
        ) for i in range(params['num_bees'])
    ]
    
    # Create mission manager
    mission_manager = MissionManager(hive_position, flowers, world, hive, honeycomb)
    
    # Run simulation loop
    simlength = params['sim_length']
    pause_time = 0.5  # Default pause between frames
    
    while simlength > 0:
        # Update bees
        for b in blist:
            if b.get_inhive():
                b.step_change(
                    hive_map=hive,
                    mission_manager=mission_manager,
                    flower_list=flowers,
                    maxX=hive_size_x,
                    maxY=hive_size_y,
                    hive_position=hive_position
                )
            else:
                b.step_change(
                    world_map=world,
                    mission_manager=mission_manager,
                    flower_list=flowers,
                    maxX=params['world_size_x'],
                    maxY=params['world_size_y'],
                    hive_position=hive_position
                )
        
        # Update flowers (regenerate nectar)
        for flower in flowers:
            flower.regenerate_nectar(0.1)
        
        # Create plot
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f"BEE WORLD SIMULATION", fontsize=15, fontweight='bold')
        
        # Plot hive and world
        plot_hive(hive, blist, honeycomb, axes[0], simlength)
        axes[0].set_title('Bee Hive')
        axes[0].set_xlabel("X position")
        axes[0].set_ylabel("Y position")
        
        plot_world(world, blist, flowers, trees, axes[1], hive_position)
        axes[1].set_title('Property')
        axes[1].set_xlabel("X position")
        axes[1].set_ylabel("Y position")
        
        plt.tight_layout()
        
        if interactive:
            # In interactive mode, wait for user input to continue
            plt.draw()
            plt.pause(0.1)
            input("Press Enter to continue to next step...")
            plt.close()
        else:
            # In batch mode, automatically continue after a pause
            plt.show(block=False)
            plt.pause(pause_time)
            plt.close()
        
        simlength -= 1
    
    # Save final state
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(f"BEE WORLD SIMULATION - FINAL STATE", fontsize=15, fontweight='bold')
    
    plot_hive(hive, blist, honeycomb, axes[0], 0)
    axes[0].set_title('Bee Hive - Final State')
    axes[0].set_xlabel("X position")
    axes[0].set_ylabel("Y position")
    
    plot_world(world, blist, flowers, trees, axes[1], hive_position)
    axes[1].set_title('Property - Final State')
    axes[1].set_xlabel("X position")
    axes[1].set_ylabel("Y position")
    
    plt.tight_layout()
    plt.savefig('beeworld_final.png')
    plt.show()

def parse_arguments():
    parser = argparse.ArgumentParser(description="BeeWorld Simulation")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--terrain-file", help="Path to terrain CSV file")
    parser.add_argument("--parameter-file", help="Path to parameters CSV file")
    return parser.parse_args()

def main():
    """Main function"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Run simulation
    run_simulation(
        interactive=args.interactive,
        terrain_file=args.terrain_file,
        parameter_file=args.parameter_file
    )

if __name__ == "__main__":
    main()