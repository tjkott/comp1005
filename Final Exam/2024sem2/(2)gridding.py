"""
b)	(7 marks). The following code creates the array grid with zeros as initial values.
•	Write a function make_tree(grid, topleft_pos, size, colour) to add a tree to the grid
•	Write a function make_house(grid, topleft_pos, height, width, colour) to add a house to the grid
•	Make trees at positions (row,col) = (4,5) and (7.2) with size 5 and colour = 5
•	Make a house at (10,10) with height 5, width 8 and colour = 7
•	Plot the grid using the “jet” colormap, applying a map range from 0 to 10
"""
import numpy as np
import matplotlib.pyplot as plt
# cmap = 'jet'

grid = np.zeros((20,20), dtype = int)
grid[2, 3] = 1

def make_tree(grid, topleft_pos, size, colour):
    x, y = topleft_pos
    grid[y:y+size, x:x+size] = colour

def make_house(grid, topleft_pos, height, width, colour):
    x, y = topleft_pos
    grid[y:y+height, x:x+width] = colour

make_tree(grid, (4,5), 5, 5)
make_house(grid, (10,10), 5, 8, 7)

print(grid)
plt.imshow(grid, cmap='jet')
plt.show()