#
# numberbar.py - print a bar chart of numbers. 
# 
import numpy as np
import matplotlib.pyplot as plt

numarray = np.zeros(10) # create an empty 10 element array

print("Enter ten number...")

for i in  range(len(numarray)):
    print('Enter a number (', i, ')...')
    numarray[i] = int(input())

xaxis = ['Total', 'Minimum', 'Maximum', 'Mean']
yaxis = []
print('Total is ', numarray.sum())
yaxis.append(numarray.sum())
print('Minimum is ', numarray.min())
yaxis.append(numarray.min())
print('Maximum is ', numarray.max())
yaxis.append(numarray.max())
print('Mean is ', numarray.mean())
yaxis.append(numarray.mean())

plt.title('Numbers Bar Chart')
plt.xlabel('Index')
plt.ylabel('Number')
plt.bar([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], numarray, 0.9, color='purple')
plt.show()