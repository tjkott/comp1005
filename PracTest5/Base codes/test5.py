'''

Student Name: Thejana Kottawatta Hewage
Student ID  : 22307822

test5.py: Simulate spread of disease through a population 
            using SIR model 
 
Based on SIR model:
    Shiflet&Shiflet Module 4.3 Modeling the Spread of SARS S2/24
    and https://www.youtube.com/watch?v=k6nLfCbAzgo 
'''

import matplotlib.pyplt as plt 
import numpy as np

Scur = 762   # number of people susceptible
Rcur = 0     # number of people recovered
Icur = 1     # number of people infected

trans_const = 0.00218   # infectiousness of disease: r = kb/N
recov_rate = 0.5        # recovery rate: a = 1/(# days infected)
simlength = 20          # number of days in simulation

resultarray = np.zeros((simlength,3)) # 2D array of floats 
resultarray[0,:] = Scur, Rcur, Icur     # record initial values



for i in range(1, simlength):
    new_infected = trans_const * Scur * Icur   # = rSI
    new_recovered = recov_rate * Icur          # = aI

    Scur = Scur - new_infected
    Icur = Icur + new_infected - new_recoverd
    Rcur = Rcur + new_recovered

    resultarray[i,:] = Scur, Rcur, Icur
 
print("Scur,\tRcur,/tIcur")
for i in range(simlength):
    print(resultarray[i,0])   # prints susceptible column of array, add recovered and infected

