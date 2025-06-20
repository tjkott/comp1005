#
# Student ID   : 22307822
# Student Name : Thejana Kottawatta Hewage
#
# buzz1.py - plot trees for the bees using arrays instead of lists
#

import numpy as np
import matplotlib.pyplot as plt

treeX = np.array([3,3,1,5])
treeY = np.array([1,5,3,3])
hiveX = np.array([3])
hiveY = np.array([3])

def buzz1():
    plt.scatter(treeX, treeY, color='Green')
    plt.scatter(hiveX, hiveY, color='Yellow')
    plt.xlabel("X position")
    plt.ylabel("Y position")
    plt.title('Buzz1: Green Trees')
    plt.show()
buzz1()