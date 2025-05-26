
""") (7 marks) The program griddle2.py (below) displays a vertical and a horizontal line. Write additional code to:
i)	Use loops and the provided arrays to draw black vertical and horizontal lines on the plot – making a grid of numrows rows and numcols columns.
ii)	Add a title to the plot - include the number of rows and columns (as variables).
iii)	Use a scatter plot to put dots in each row/column using plt.scatter(xvalues, yvalues). Use nested loops or just loop through rows or columns and plot one row/col per loop.
iv)	Using the lists of colours and dot sizes, have the code cycle through the lists of colours/sizes. Use plt.scatter(xvalues, yvalues, c=colours, s=sizes)
"""
import matplotlib.pyplot as plt
import numpy as np

numrows = 8
numcols = 10
colours = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
sizes = [20,40,60]
x_ones = np.ones(numrows + 1)
y_range = np.arange(0, numrows+1)

y_ones = np.ones(numcols + 1)

x_range = np.arange(0, numcols + 1)
print(y_range)
print(x_ones)

for y in range(numrows + 1): # Horizontal lines
    plt.plot([0, numcols], [y, y], color='black')  # Horizontal lines
for x in range(numcols + 1):  # Vertical lines
    plt.plot([x, x], [0, numrows], color='black')  # Vertical lines
plt.title(f"Rainbow plot: {numrows} rows and {numcols} columns")

colours_index = 0
sizes_index = 0
for row in range(numrows):
    y_center = row + 0.5
    for col in range(numcols):
        x_center = col + 0.5
        plt.scatter(x_center, y_center, c=colours[colours_index], s=sizes[sizes_index])
        if colours_index < len(colours) - 1:
            colours_index += 1
        else:
            colours_index = 0
        if sizes_index < len(sizes) - 1:
            sizes_index += 1
        else:
            sizes_index = 0  
plt.show()