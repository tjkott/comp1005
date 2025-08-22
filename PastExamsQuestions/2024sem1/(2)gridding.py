"""
(8 marks). The following code creates the array grid with zeros as initial values. Modify 
the code to: 
 
• Set the top seven rows to 1, as shown in the printed grid 
• Set the inner area to 2 
• Set two values to 10, as shown 
• Set all remaining zero values to be -1
"""
import numpy as np
import matplotlib.pyplot as plt
import random
import os

grid = np.zeros((10,10), dtype = int)
# [1st part, 2nd part], 1st part = rows, 2nd part = columns
grid[0:7, :] = 1 
grid[3:6, 2:7] = 2
for i in range(2): 
    grid[random.randint(0, 9), random.randint(0, 9)] = 10
grid[grid == 0] = -1
#print(grid)
#plt.imshow(grid)
#plt.show()

def partc():
    # open the file "grid.csv" and read the data
    filename = "grid.csv"
    with open(filename, 'r') as f:
        str_data = np.loadtxt(f, dtype=str, delimiter=None) # load into an array. Each element is a string
    
    # rid of the "."
    r, c = str_data.shape # get dimensions of the array. 
    for i in range(r):
        for j in range(c):
            str_data[i, j] = int(str_data[i, j][:-1])

    return str_data.astype(int) #return final array as int
print(partc())

