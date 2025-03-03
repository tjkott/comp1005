#
# numbersarray.py: Read ten numbers give sum, min, max and mean. 
#
import numpy as np
import matplotlib.pyplot as plt

numarray = np.zeros(5) # create an empty 10 element array

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

plt.title('Plot of the Numbers')
plt.plot(xaxis, yaxis, marker = '^', linestyle = '', color = 'r')
plt.show()