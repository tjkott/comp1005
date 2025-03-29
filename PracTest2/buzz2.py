#
# Student ID   : 22307822
# Student Name : Thejana Kottawatta Hewage
#
# buzz2.py - randomly generate 10 trees
#

import numpy as np
import matplotlib.pyplot as plt

treeX = np.random.randint(1,5,10)
treeY = np.random.randint(1,5,10)
hiveX = np.array([3])
hiveY = np.array([3])

def buzz2():
    plt.scatter(treeX, treeY, color='Green')
    plt.scatter(hiveX, hiveY, color='Yellow')
    plt.xlabel("X position")
    plt.xlim(0,6)
    plt.ylabel("Y position")
    plt.ylim(0,6)
    plt.title('Buzz2: Ten Random Trees')
    plt.show()
buzz2()