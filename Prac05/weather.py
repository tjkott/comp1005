#
# weather.py: Print min and max temps from a file
# (source: http://www.bom.gov.au/climate/)

import matplotlib.pyplot as plt
import os
print(os.getcwd)


fileobj = open(r'C:\Users\theja\OneDrive\Documents\comp1005\Prac05\marchweather.csv', 'r')
# fileobj = open('marchweather.csv', 'r')
line1 = fileobj.readline().strip()
line2 = fileobj.readline().strip()
fileobj.close()

mins_string = line1.split(',')
maxs_strings = line2.split(',')
mins = [float(val) for val in mins_string] # each entry converted to a float
maxs = [float(val) for val in maxs_strings]

dates = range(1,32)
plt.plot(dates, mins, dates, maxs) 
plt.show()