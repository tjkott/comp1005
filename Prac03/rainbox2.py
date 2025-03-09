import matplotlib.pyplot as plt
import numpy as np 
import math
from math import sin, cos, tan, sqrt

# trying to calculate y
def semi_circle(x, radius):
    y = np.zeros(len(x))
    for i in range (len(x)):
        y[i] = math.sqrt(radius**2 - x[i]**2)
    return y

x_red = np.linspace(-40, 40, num=100)
y_red = semi_circle(x_red, 40)
print(y_red)