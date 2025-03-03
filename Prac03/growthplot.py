#
# growth.py - simulation of unconstrained growth. 
#
print("\nSIMULATION - Unconstrained Growth\n")
length = 10
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
for i in range(1, int(num_iter) + 1):
    growth = growth_step * population
    population = population + growth
    time = i * time_step
    print("Time: ", time, " \tGrowth: ",  growth, "\tPopulation: ", population)
print("\nPROCESSING COMPLETE.\n")