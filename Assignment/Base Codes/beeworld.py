# Student Name: <put your name here> 
# Student ID:   <put your ID here>
#
# beeworld.py - simulation of bee colony in a world with trees and flowers
#
# Version information: 
#
# Usage: <how to run the program>
#
import matplotlib.pyplot as plt
import numpy as np
from buzzness import Bee

def plot_hive(hive, blist, ax):
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower") 
    ax.scatter(xvalues, yvalues)

simlength = 1
hiveX = 30
hiveY = 25
b1 = Bee("b1", (5,10))
blist = [b1]

# hive will range between 0 and 10
# 10 is brown, not ready
# 0 is ready
# 1-5 is honey level
hive = np.zeros((hiveX,hiveY))

#plt.ion()

for t in range(simlength):
    for b in blist:
        b.step_change()
    fig, axes = plt.subplots(1, 1, figsize=(10,6))

    plot_hive(hive, blist, axes)
    #plot_hive(hive, blist, axes[0])
    
    plt.show()
    #plt.pause(1)
    #plt.clf()

