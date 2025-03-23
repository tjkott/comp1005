# heatsource.py

import numpy as np
import matplotlib.pyplot as plt

size = 20

currg = np.zeros((size,size))
print(currg)

currg[:,0] = 10 # set every first column of each array to 10
nextg = np.zeros((size,size))

# create heat source
hlist = []
fileobj = open('heatsource.csv','r') 
for line in fileobj:
    line_s = line.strip()
    ints = [float(x) for x in line_s.split(',')] # list comprehension
    hlist.append(ints)
fileobj.close()

# Calculate heat diffusion 
for timestep in range(100):
    for r in range(1,size-1):
        for c in range (1, size-1):
            nextg[r,c]=calcheat(curr[r-1:r+2,c-1:c+2]) # heat diffusion

    for r in range(size):
        for c in range(size):
            if harray[r,c] > nextg[r,c]:  # maintaining heat source
                nextg[r,c] = harray[r,c]

    currg = nextg.copy()

harray = np.array(hlist) # heat source array to maintain the heat generation in the simulation
currg = harray.copy()

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
