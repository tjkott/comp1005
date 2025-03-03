#
# growthsubplot.py - give multipple plots in the same sigure. 
#
import matplotlib.pyplot as plt
import numpy as np

print("\nSIMULATION - Unconstrained Growth\n")
length = 100
population = 100
growth_rate = 0.1
time_step = 0.5
num_iter = length / time_step
growth_step = growth_rate * time_step
print("INITIAL VALUES:\n")
print("Simulation Length (hours): ", length)
print("Initial Population: ", population)
print("Growth Rate(per hour): ",  growth_rate)
print("Time Step (part hour per step): ",  time_step)
print("Num iterations (sim length * time step per hour): ", num_iter)
print("growth step (growth rate per time step): ", growth_step)
print("\nRESULTS:\n")
print("Time: ", 0, "\tGrowth: ", 0, " \tPopulation: ", 100)

zero_array = np.zeros(int(num_iter) + 1) # create an empty array of size num_iter + 1
time_array = np.zeros(int(num_iter) + 1) # create an empty array of size num_iter + 1

for i in range(1, int(num_iter) + 1):
    growth = growth_step * population
    population = population + growth
    time = i * time_step
    zero_array[i] = population
    time_array[i] = time
    print("Time: ", time, " \tGrowth: ",  growth, "\tPopulation: ", population)
print("\nPROCESSING COMPLETE.\n")

plt.title('Prac 3.1: Unconstrained Growth  ')
plt.plot(time_array, zero_array, color = 'r')
plt.show()

plt.subplot(211)
plt.plot(time_array, zero_array, '--')
plt.title('March Temperatures')
plt.ylabel('Temperature')
plt.subplot(212)
plt.plot(time_array, zero_array, 'ro')
plt.ylabel('Temperature')
plt.xlabel
plt.show()