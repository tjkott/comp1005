import matplotlib.pyplot as plt
import os
print(os.getcwd)
fileobj = open(r'C:\Users\theja\OneDrive\Documents\comp1005\Prac05\marchweatherfull.csv', 'r')
# fileobj = open(‘marchweatherfull.csv’, ‘r’) 
data = fileobj.readlines()
fileobj.close()

def mins():
    mins_strings= []
    for line in data[1:]:   
        columns = line.strip().split (",") # strip any white-spaces and split into csv
        if len(columns) > 2: # ensures line has at least 3 columns to ensure valid data
            mins_strings.append(columns[2])
    mins = [float(val) for val in mins_strings]
    return mins
mins()

 # make an empty list to store the mins column on each line of the file 
          # note that each entry will need to be converted to a float

# do the same for maxs, nines and threes

