'''

Student Name: Thejana Kottawatta Hewage
Student ID  : 22307822

test5.py: Simulate spread of disease through a population 
            using SIR model 
 
Based on SIR model:
    Shiflet&Shiflet Module 4.3 Modeling the Spread of SARS S2/24
    and https://www.youtube.com/watch?v=k6nLfCbAzgo 
'''

import matplotlib.pyplot as plt
import numpy as np
import sys

# Default values if no inputs provied in the command line
Scur = 762 # dEfault susceptible
Rcur = 0 # Default recovered
Icur = 1  # DEfault infected
trans_const = 0.00218  # Default infectiousness of disease 
recov_rate = 0.5  # Default recovery rate 
simlength = 20  # DEfault simlength

# Parse command line inputs
if len(sys.argv) == 3:
    try:
        trans_const = float(sys.argv[1])
        recov_rate = float(sys.argv[2])
        print(f"Received parameters from command line: r = {trans_const}, a = {recov_rate}")
    except ValueError:
        print("Error: Invalid command-line arguments. Expected two float values for r and a.")
        print(f"Using default parameters: r = {trans_const}, a = {recov_rate}")
elif len(sys.argv) == 1:
    print("No command-line arguments provided. Using default parameters.")
    print(f"Default parameters: r = {trans_const}, a = {recov_rate}")
else:
    print("Usage: python test5.py [<trans_const> <recov_rate>]")
    print("If parameters are provided, both trans_const (r) and recov_rate (a) must be specified.")
    print(f"Using default parameters: r = {trans_const}, a = {recov_rate}")


resultarray = np.zeros((simlength, 3))  # 2D array for S, R, I values over time
resultarray[0, :] = Scur, Rcur, Icur    # Record initial values


for i in range(1, simlength):
    new_infected = trans_const * Scur * Icur    # Calculate new infections: rSI
    new_recovered = recov_rate * Icur           # Calculate new recoveries: aI
    Scur = Scur - new_infected
    Icur = Icur + new_infected - new_recovered  # Corrected variable: new_recovered
    Rcur = Rcur + new_recovered
    Scur = max(0, Scur) # Ensure minimum population counts
    Icur = max(0, Icur)
    Rcur = max(0, Rcur)
    resultarray[i, :] = Scur, Rcur, Icur

# Plotting data
print("Day,Susceptible,Recovered,Infected")
for i in range(simlength):
    print(f"{i},{resultarray[i,0]:.6f},{resultarray[i,1]:.6f},{resultarray[i,2]:.6f}")# Print data formatted to 6 decimal places, commaseparated
plt.figure(figsize=(10, 6)) 
# Modifying the colours and markers for the plot
plt.plot(resultarray[:, 0], 'k-', label='Susceptible')  # Susceptible: solid black line
plt.plot(resultarray[:, 1], 'g^', label='Recovered')    # Recovered: Green triangles
plt.plot(resultarray[:, 2], 'rD', label='Infected')     # Infected: Red diamonds
plt.xlabel("# Days")  # x and y axis labels
plt.ylabel("# People")
title_r_formatted = f"{trans_const:.6g}" 
title_a_formatted = f"{recov_rate:.6g}"
plt.title(f"SIR model with r: {title_r_formatted}, a: {title_a_formatted}")
plt.legend()
plt.grid(True) # Add a grid for easier reading
plot_filename = f"SIR_r{title_r_formatted}_a{title_a_formatted}.png"  # Save the plot. 
plt.savefig(plot_filename)
print(f"Plot saved as {plot_filename}")