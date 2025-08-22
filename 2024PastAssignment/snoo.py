import numpy as np
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from creatures import Puppy, Cat, Squirrel
from food import Food

def build_backyard(dims):
    backyard = np.zeros((dims[0], dims[1])) 
    return backyard

def plot_puppies(ax, puppies):
    for puppy in puppies:
        ax.scatter(puppy.pos[0], puppy.pos[1], puppy.pos[2], c='blue', marker='D')

def plot_cats(ax, cats):
    for cat in cats:
        ax.scatter(cat.pos[0], cat.pos[1], cat.pos[2], c='orange', marker='o')

def plot_squirrels(ax, squirrels):
    for squirrel in squirrels:
        ax.scatter(squirrel.pos[0], squirrel.pos[1], squirrel.pos[2], c='brown', marker='s')

def plot_food(ax, foods):
    for food in foods:
        ax.scatter(food.pos[0], food.pos[1], food.pos[2], c='green', marker='^')

def plot_energy(ax, puppies, cats):
    labels = [f"Puppy {i+1}" for i in range(len(puppies))] + [f"Cat {i+1}" for i in range(len(cats))]
    energy_levels = [puppy.energy for puppy in puppies] + [cat.energy for cat in cats]
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, energy_levels, align='center', color='cyan')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # Invert y-axis to display puppies and cats at the top

def main():
    # backyard dimensions
    backyard_size = (60, 60, 0.5) 
    backyard_dims = (backyard_size[0], backyard_size[1])
    house_height = 25
    house_corners = np.array([[backyard_size[0]/4, 0, 0],
                         [(backyard_size[0]/4 + backyard_size[0]/2), 0, 0],
                         [(backyard_size[0]/4 + backyard_size[0]/2), ((backyard_size[1]*1.5)/3), 0],
                         [backyard_size[0]/4, ((backyard_size[1]*1.5)/3), 0],
                         [backyard_size[0]/4, 0, house_height],  
                         [(backyard_size[0]/4 + backyard_size[0]/2), 0, house_height],
                         [(backyard_size[0]/4 + backyard_size[0]/2), ((backyard_size[1]*1.5)/3), house_height],
                         [backyard_size[0]/4, ((backyard_size[1]*1.5)/3), house_height]])
    house_faces = [[0, 1, 2, 3],  # House floor
             [4, 5, 6, 7],  # House roof
             [0, 1, 5, 4],  # Wall 1
             [1, 2, 6, 5],  # Wall 2
             [2, 3, 7, 6],  # Wall 3
             [3, 0, 4, 7]]  # Wall 4
    house_bounds = [(backyard_size[0]/4, 0), (backyard_size[0]/4 + backyard_size[0]/2, (backyard_size[1]*1.5)/3)]
    backyard = build_backyard(backyard_size)

    # Ensure puppy spawn positions are valid. 
    puppy_positions = []
    while len(puppy_positions) < 7:
        new_pos = (random.randint(0, backyard_size[0]), random.randint(0, backyard_size[1]), 0) # Ensure the dog positions are outside the house boundaries
        if not ((backyard_size[0]/4 <= new_pos[0] < (backyard_size[0]/4 + backyard_size[0]/2)) and 
                (0 <= new_pos[1] < ((backyard_size[1]*1.5)/3))):
            puppy_positions.append(new_pos)
    puppies = [Puppy(f"Snoopy {i+1}", "white/black", pos) for i, pos in enumerate(puppy_positions)]

    cats = [Cat(f"Whiskers {i+1}", "orange", (random.randint(house_bounds[0][0], house_bounds[1][0]), random.randint(house_bounds[0][1], house_bounds[1][1]), 0)) for i in range(5)]
    
    # Ensure squirrels spawn positions are valid. 
    squirrel_positions = []
    while len(squirrel_positions) < 3:
        new_pos = (random.randint(0, backyard_size[0]), random.randint(0, backyard_size[1]), 0)
        if not ((backyard_size[0]/4 <= new_pos[0] < (backyard_size[0]/4 + backyard_size[0]/2)) and 
                (0 <= new_pos[1] < ((backyard_size[1]*1.5)/3))):
            squirrel_positions.append(new_pos)
    squirrels = [Squirrel(f"Nutty {i+1}", "brown", pos) for i, pos in enumerate(squirrel_positions)]
    
    # Randomly generate food across the map. 
    food_positions = []
    while len(food_positions) < 5:
        new_pos = (random.randint(4, backyard_size[0] - 4), random.randint(4, backyard_size[1] - 4), 0)
        if all(np.linalg.norm(np.array(new_pos) - np.array(existing_pos)) > 4 for existing_pos in food_positions):
            food_positions.append(new_pos)
    foods = [Food("Nut", pos) for pos in food_positions]
    plt.ion()
    fig = plt.figure(figsize=(13.5, 9))

    # Create a new plot for backyard.
    backyard_plot = fig.add_subplot(121, projection='3d')
    backyard_plot.set_aspect('auto') 
    backyard_plot.set_xlim(0, backyard_size[0])
    backyard_plot.set_ylim(0, backyard_size[1])
    backyard_plot.set_zlim(0, 30)  # Ensure backyard lies on the z=0 plane
    backyard_plot.set_title('3D Backyard with Puppies')
    backyard_plot.set_xlabel('X')
    backyard_plot.set_ylabel('Y')
    backyard_plot.set_zlabel('Z')

    # Create a new plot for energy levels
    energy_plot = fig.add_subplot(122)
    energy_plot.set_title('Energy Levels')
    
    for i in range(10000000):
        # Puppies simulation
        for puppy in puppies:
            puppy.step_change(backyard_size)
            for food in foods: # Check if puppy is within 4 units of food and consume it
                puppy.consume_food(food.get_pos())
            puppy.energy -= 1
        # Cats simulation
        for cat in cats:
            cat.step_change(house_bounds)
            for food in foods: # Check if cat is within 4 units of food and consume it
                cat.consume_food(food.get_pos())
            cat.energy -= 1
        # Squirrels simulation
        for squirrel in squirrels:
            squirrel.step_change(backyard_dims, house_bounds)
        # Update energy plot
        energy_plot.clear()
        plot_energy(energy_plot, puppies, cats)
        # Make puppies chase squirrels
        for puppy in puppies:
            for squirrel in squirrels:
                direction = np.array(squirrel.get_pos()[:2]) - np.array(puppy.get_pos()[:2])
                if np.linalg.norm(direction) != 0: # Check if direction vector is not zero to avoid division by zero
                    direction_normalized = direction / np.linalg.norm(direction)
                    direction_scaled = direction_normalized * 2 # Scale the normalized direction vector by 2 units to move 2 units
                    new_pos_float = np.array(puppy.get_pos()[:2]) + direction_scaled # Calculate new position by adding the scaled direction to the current position of the puppy
                    new_pos = tuple(map(int, new_pos_float)) # Convert new position to integers
                    if (0 <= new_pos[0] < backyard_size[0]) and (0 <= new_pos[1] < backyard_size[1]): # Ensure the new position is within the backyard boundaries and outside the house boundaries
                        # Check if the new position is outside the house boundaries
                        if not ((backyard_size[0]/4 <= new_pos[0] < (backyard_size[0]/4 + backyard_size[0]/2)) and 
                                (0 <= new_pos[1] < ((backyard_size[1]*1.5)/3))):
                            puppy.pos = (new_pos[0], new_pos[1], 0)
        backyard_plot.clear()
        x, y = np.meshgrid(np.linspace(0, backyard_size[0], backyard_size[0]), np.linspace(0, backyard_size[1], backyard_size[1]))
        z = np.full_like(x, 0)  # Ensure the backyard lies on the z=0 plane
        backyard_plot.plot_surface(x, y, z, color='palegreen', alpha=0.5)
        # Plot the house
        for face in house_faces:
            x_house = house_corners[face, 0]
            y_house = house_corners[face, 1]
            z_house = house_corners[face, 2]
            backyard_plot.plot(x_house[[0, 1, 2, 3, 0]], y_house[[0, 1, 2, 3, 0]], z_house[[0, 1, 2, 3, 0]], color='red')
        # PLot everything. 
        plot_puppies(backyard_plot, puppies)
        plot_cats(backyard_plot, cats)
        plot_squirrels(backyard_plot, squirrels)
        plot_food(backyard_plot, foods)
        plt.draw()
        plt.pause(1)

if __name__ == "__main__":
    main()