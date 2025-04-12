# Student Name: Thejana Kottawatta Hewage
# Student ID:   22307822
#
# task2.py - Plot a more complex bee hive
#
# Version information: 12/04//2025 - Final version
#
# Usage: <how to run the program>
#
import matplotlib.pyplot as plt
import random
import numpy as np
from buzzness import Bee

simlength = 1
hiveX = 30
hiveY = 25
hive = np.zeros((hiveX,hiveY))
ready_for_honey = 10
# generate 5 bees. 
blist = [Bee(f"b{i+1}", (np.random.randint(0, hiveX), np.random.randint(0, hiveY))) for i in range(5)] # for loop for generating 5 bees 

def plot_hive(hive, blist, ax):
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

# Run the simulation. 
for t in range(simlength):
    for b in blist:
        b.step_change()
    fig, axes = plt.subplots(1, 2, figsize=(15,6)) # 1 row with 2 columns sup fig
    
    ## (e) Plot a duplicate of the plot in the 2nd column and add a supertitle. 
    
    fig.suptitle('BEE WORLD', fontsize=15, fontweight='bold')
    plot_hive(hive, blist, axes[0])
    axes[0].set_title('Bee Hive')
    axes[0].set_xlabel("X position")
    axes[0].set_ylabel("Y position")

    plot_hive(hive, blist, axes[1]) # the duplicate
    axes[1].set_title('Bee Hive')
    axes[1].set_xlabel("X position")
    axes[1].set_ylabel("Y position")

    plt.show()
    #plt.pause(1)
    #plt.clf()
fig.savefig('task2.png')


# hive will range between 0 and 10
# 10 is brown, not ready
# 0 is ready
# 1-5 is honey level

#plt.ion()

## (c) Update the plot to 



