#
# rainbow.py - plot a rainbow
#
import matplotlib.pyplot as plt
import numpy as np
import math
from math import sin, cos, tan

def semi_circle(x, radius):
    y = np.zeros(len(x))
    for i in range(len(x)):
        y[i] = math.sqrt(radius**2 - x[i]**2)
    return y

x_red = np.linspace(-40, 40, num=100) # creates 100 equally spaced x_values. 
y_red = semi_circle(x_red, 40) # creates y_values. 

x_orange = np.linspace(-37, 37, num=100)
y_orange = semi_circle(x_orange, 37)

x_yellow = np.linspace(-34, 34, num=100)
y_yellow = semi_circle(x_yellow, 34)

x_green = np.linspace(-31, 31, num=100)
y_green = semi_circle(x_green, 31)

x_blue = np.linspace(-28, 28, num=100)
y_blue = semi_circle(x_blue, 28)

plt.plot(x_red, y_red, marker='o', color = 'r')
plt.plot(x_orange, y_orange, marker='o', color = 'orange')
plt.plot(x_yellow, y_yellow, marker='o', color = 'yellow')
plt.plot(x_green, y_green, marker='o', color = 'green')
plt.plot(x_blue, y_blue, marker='o', color = 'blue')
plt.show()