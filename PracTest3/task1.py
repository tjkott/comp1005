# Student Name: Thejana Kottawatta Hewage
# Student ID:   22307822
#
# task1.py - simulation of bee colony in a world with trees and flowers
#
# Version information: 11/04//2025 - Final version
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

def plot_hive(hive, blist, ax):
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()] # list of x coordinates only if inhive = True
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower") 
    ax.scatter(xvalues, yvalues)

## (c) Create 5 bees and append to the blist. 
blist = [Bee(f"b{i+1}", (np.random.randint(0, hiveX), np.random.randint(0, hiveY))) for i in range(5)]
for t in range(simlength):
    for b in blist:
        b.step_change()
    fig, axes = plt.subplots(1, 1, figsize=(10,6))

    plot_hive(hive, blist, axes)
    ## (e) Update the plt title, xlabel, ylabel to describe the plot. 
    plt.xlabel("X position")
    plt.ylabel("Y position")
    plt.title('Task 1: Beehive')
    plt.show()
    #plt.pause(1)
    #plt.clf()
# Save fig 1. 
fig.savefig('task1.png')
 

# hive will range between 0 and 10
# 10 is brown, not ready
# 0 is ready
# 1-5 is honey level
hive = np.zeros((hiveX,hiveY))

#plt.ion()



