import matplotlib.pyplot as plt

# Activity 2
# Read file. 
fileobj = open(r'C:\Users\theja\OneDrive\Documents\comp1005\Prac05\marchweatherfull.csv', 'r')
# fileobj = open(‘marchweatherfull.csv’, ‘r’) 
data = fileobj.readlines()
fileobj.close()

def column_extractor(column_index):
    column_strings = []
    for line in data[1:]:
        columns = line.strip().split(",")
        if len(columns) > column_index:
            column_strings.append(columns[column_index])
    column = [float(val) for val in column_strings]
    return column
mins = column_extractor(2)
max_s = column_extractor(3)
nines = column_extractor(10)
threes = column_extractor(16)

# Activity 3
file2 = open(r'C:\Users\theja\OneDrive\Documents\comp1005\Prac05\marchout.csv', 'w')
#file2 = open(‘marchout.csv’, ‘w’) 
file2.write(",Mins,Maxs,Nines,Threes\n")
for i in range(len(mins)):
    file2.write("," + str(mins[i]) + "," + str(max_s[i]) + "," + str(nines[i]) + "," + str(threes[i]) + "\n")
file2.close()