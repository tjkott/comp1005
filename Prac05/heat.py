import numpy as np
import matplotlib.pyplot as plt

size = 20

currg = np.zeros((size,size))
print(currg)
for i in range(size):
    currg[i,0] = 10

nextg = np.zeros((size,size))

for timestep in range(5):
    for r in range(1, size-1):
        for c in range (1, size-1 ):
            ### HIGHLIGHTED CODE
            nextg[r,c] = (currg[r-1,c-1]*0.1 + currg[r-1,c]*0.1
                         + currg[r-1,c+1]*0.1 + currg[r,c-1]*0.1
                         + currg[r,c]*0.2 + currg[r,c+1]*0.1
                         + currg[r+1,c-1]*0.1 + currg[r+1,c]*0.1
                         + currg[r+1,c+1]*0.1)
            ### HIGHLIGHTED CODE
    for i in range(size):
        nextg[i,0] = 10
  
    print("Time step: ", timestep)
    print(nextg)
    currg = nextg.copy()
    
plt.imshow(currg, cmap=plt.cm.hot)
plt.show()