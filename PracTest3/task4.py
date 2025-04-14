# Student Name: Thejana Kottawatta Hewage
# Student ID:   22307822
#
# task4.py - Make the bees move
#
# Version information: 13/04//2025 - Final version
#
# Usage: <how to run the program>
#
import matplotlib.pyplot as plt
import random
import numpy as np
from buzzness import Bee


simlength = 5
hiveX = 30
hiveY = 25
hive = np.zeros((hiveX,hiveY))
ready_for_honey = 10
# generate 5 bees. 
blist = [Bee(f"b{i+1}", (np.random.randint(0, hiveX), np.random.randint(0, hiveY))) for i in range(5)] # for loop for generating 5 bees 

def plot_hive(hive, blist, ax): #ax is a single axes which you can drae your subploot. 
    ## (b) readiness for honey

    if ready_for_honey == 10:
        hive[:, :] = 10
    else:
        hive[:, :] = 10 - ready_for_honey # 10 is brown, not ready, 0 is ready
    
    ## (c) Stripe of comb in the centre. 
    stripe_center = hiveX // 2 # Since, we are working with arrays, floats cannot be used in slicing. Thus, division with remainder.
    hive[int(stripe_center - 1): int(stripe_center+2), :] = 0 # Make the stripe white with the colour map. 

    for j in range(hiveY):
        if j % 2 == 0: # Even squares are yellow. 
            hive[int(stripe_center), j] = 5 # 5 is the yellow in the colourmap
    
    # x and y positions of the bees. 
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()] # list of x coordinates only if inhive = True
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower", cmap='YlOrBr', vmin=0, vmax=10) # colour map for the hive.
    ax.scatter(xvalues, yvalues)

propertyX = 50
propertyY = 40
hive_position = 22, 20 # x,y position of the hive in the world.
world_bees = [Bee(f"wb{i+1}", (np.random.randint(0, propertyX), np.random.randint(0, propertyY))) for i in range(2)]
for b in world_bees:
    b.set_inhive(False)
def plot_world(ax):
    world = np.zeros((propertyX, propertyY)) #world is a 2D array of zeros.
    world[:, :] = 5 #Assign green value from the tab20 colourmap. 
    # (d) Add a variable to hold the hive position, pass it to world_plot to plot a square. 
    world[hive_position[0]:hive_position[0]+2, hive_position[1]:hive_position[1]+2] = 16 # Assign white value from the tab20 colourmap for the hive

    # alternating green and brown squares.
    for x in range(propertyX//2, propertyX): #from 'origin' of the plot to the end of the x-limit
        if x % 2 == 0: # if the i is even
            for y in range(propertyY//2, propertyY):
                if y % 2 == 0:
                    world[x, y] = 5 #green squares for eveb columns
                else:
                    world[x, y] = 10
        elif x % 2 == 1: #for odd index
            for y in range(propertyY//2, propertyY):
                world[x, y] = 5 #green row
    
    
    world[30:39, 5:10] = 0 # blue pond 
    world[10:15, 30:35] = 14 # gray patch

    #Vertical stripes
    for x in range(1, 10):
        if x % 2 == 0: # if the column is odd, set it to brown.
            world[x:x+1, 2:4] = 4 #Brown is 0
        else: #if the col is even set it to green
            world[x:x+1, 2:4] = 5 #Green is 4

    ## (c) Plotted with the tab20 colourmap. 
    ax.imshow(world.T, origin="lower", cmap='tab20', vmin=0, vmax=19)
    #Plot the world bees
    xvalues = [b.get_pos()[0] for b in world_bees]
    yvalues = [b.get_pos()[1] for b in world_bees]
    ax.scatter(xvalues, yvalues, c='black', marker='o', s=80)

# Run the simulation. 
for t in range(simlength):
    for b in blist:
        b.step_change()
    for b in world_bees:
        b.step_change()
    fig, axes = plt.subplots(1, 2, figsize=(15,6)) # 1 row with 2 columns sup fig
    
    ## (e) Plot a duplicate of the plot in the 2nd column and add a supertitle. 
    
    fig.suptitle(f"BEE WORLD. Simulation: {simlength}", fontsize=15, fontweight='bold')

    plot_hive(hive, blist, axes[0])
    axes[0].set_title('Bee Hive')
    axes[0].set_xlabel("X position")
    axes[0].set_ylabel("Y position")

    plot_world(axes[1]) # the property
    axes[1].set_title('Property') ## (e) Update the plot title to describe the plot. 
    axes[1].set_xlabel("X position")
    axes[1].set_ylabel("Y position")

    plt.show()
    plt.pause(1)
    simlength = simlength - 1
fig.savefig('task4.png')

#plt.ion()

## (c) Update the plot to 



