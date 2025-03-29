#
# Student ID   : 22307822
# Student Name : Thejana Kottawatta Hewage
#
# buzz4.py - 
#

import numpy as np
import matplotlib.pyplot as plt
import string

def buzz4(trees):
    trees = int(trees)
    treeX = np.random.uniform(1,5,trees)
    treeY = np.random.uniform(1,5,trees)
    hiveX = np.array([3])
    hiveY = np.array([3])
    
    # Distances
    distances = np.empty(0) #Array which stores distance values
    for i in range(trees):
        distances = np.append(distances, np.sqrt((treeX[i] - hiveX[0])**2 + (treeY[i] - hiveY[0])**2))
    
    # Plot
    fig, (scplt, colplt) = plt.subplots(1, 2, figsize=(12, 6))
    # scatter plot
    scplt.scatter(treeX, treeY, color='Green')
    scplt.scatter(hiveX, hiveY, color='Yellow')
    scplt.set_xlabel("X position")
    scplt.set_xlim(0,6)
    scplt.set_ylabel("Y position")
    scplt.set_ylim(0,6)
    scplt.set_title('Buzz4:  Random Trees')
    
    # column graph 
    tree_names = np.array(list(string.ascii_uppercase[:trees])) #Name each tree for the column graph
    colplt.bar(tree_names, distances, color='Yellow', hatch='/', edgecolor='Black', linewidth=1)
    colplt.set_xlabel("Trees")
    colplt.set_ylabel("Distance")
    colplt.set_title('Distance to Trees')

    # Final plot
    fig.suptitle("Buzz4: Floaty Trees and Distances", fontsize=16)
    plt.show()

def main(number_of_trees):
    if 5.0 <= number_of_trees <= 20.0:
        print(buzz4(number_of_trees))
    else:
        number_of_trees = float(input("Invalid input. Please enter a valid number of trees."))
        main(number_of_trees)
main(float(input("Enter the number of trees: ")))