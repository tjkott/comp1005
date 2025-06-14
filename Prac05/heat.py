# heat.py - 2D heat equation solver

import numpy as np
import matplotlib.pyplot as plt

size = 20

currg = np.zeros((size,size))
print(currg)
for i in range(size):
    currg[i,0] = 10 # set every first column fo each array to 10
nextg = np.zeros((size,size))

for timestep in range(5):
    for r in range(1, size-1):
        for c in range (1, size-1 ):
            nextg[r,c] = 0.1 * (currg[r-1:r+2,c-1:c+2].sum() + currg[r,c])
    for i in range(size):
        nextg[i,0] = 10
  
    print("Time step: ", timestep)
    print(nextg)
    currg = nextg.copy()
    plt.imshow(currg, cmap=plt.cm.hot)
    plt.show()
