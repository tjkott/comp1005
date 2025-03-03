#
# growthplot.py - simulation of unconstrained growth. 
#
import matplotlib.pyplot as plt

print("\nSIMULATION - Unconstrained Growth\n")
length = 100
population = 100
growth_rate = 0.1
time_step = 0.5
num_iter = length / time_step
growth_step = growth_rate * time_step
print("INITIAL VALUES:\n")
print("Similation Length (hours): ", length)
print("Initial Population: ", population)
print("Growth Rate(per hour): ",  growth_rate)
print("Time Step (part hour per step): ",  time_step)
print("Num iterations (sim length * time step per hour): ", num_iter)
print("growth step (growth rate per time step): ", growth_step)
print("\nRESULTS:\n")
print("Time: ", 0, "\tGrowth: ", 0, " \tPopulation: ", 100)

times=[0] #A list for the x-axis 'times', initial value is 0.
pops=[100] # a list for the populations, initial value is 0. 
for i in range(1, int(num_iter) + 1):
    growth = growth_step * population
    population = population + growth
    time = i * time_step
    times.append(time) # add current time to the 'times' list. 
    pops.append(population) # add current population to the 'pops' list.
    print("Time: ", time, " \tGrowth: ",  growth, "\tPopulation: ", population)
print("\nPROCESSING COMPLETE.\n")

plt.title('Prac 3.1: Unconstrained Growth  ')
plt.plot(times, pops, color = 'r')
plt.show()