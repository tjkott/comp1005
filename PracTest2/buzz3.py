#
# Student ID   : 22307822
# Student Name : Thejana Kottawatta Hewage
#
# buzz3.py - user input number of trees
#

import numpy as np
import matplotlib.pyplot as plt


def buzz3(trees):
    trees = int(trees)
    treeX = np.random.uniform(1,5,trees)
    treeY = np.random.uniform(1,5,trees)
    hiveX = np.array([3])
    hiveY = np.array([3])
    plt.scatter(treeX, treeY, color='Green')
    plt.scatter(hiveX, hiveY, color='Yellow')
    plt.xlabel("X position")
    plt.xlim(0,6)
    plt.ylabel("Y position")
    plt.ylim(0,6)
    plt.title('Buzz3: Floaty Random Trees')
    plt.show()

def main(number_of_trees):
    if 5.0 <= number_of_trees <= 20.0:
        print(buzz3(number_of_trees))
    else:
        number_of_trees = float(input("Invalid input. Please enter a valid number of trees."))
        main(number_of_trees)
main(float(input("Enter the number of trees: ")))