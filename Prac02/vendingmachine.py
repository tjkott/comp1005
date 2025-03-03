#
# vendingmachine.py - Simulate a vending machine
#

import time
print('Welcome to the snack vending machine!', '\nThe slots are loaded with delivious treats!.\n')
print()

treats = [
    ['ID', 'Name', 'Price', 'Quantity'],
    [1, 'Choco pie', 1.00, 5], 
    [2, 'Hello Panda', 0.50, 10], 
    [3, 'Fortune Cookie', 0.30, 10], 
    [4, 'Fig Roll', 0.30, 10], 
    [5, 'Maliban Orange Cream', 0.30, 10], 
    [6, 'Maliban Custard Cream', 0.30, 10], 
    [7, 'Maliban Chocolate Cream', 0.30, 10], 
    [8, 'Eccles Cake', 0.80, 5], 
    [9, 'Wagon Wheel', 1.50, 1], 
]
RESET = '\033[0m'
while 1 == 1:
    want_treat = input('\nWould you like a treat? (y/n): \n').upper()
    if want_treat == 'Y':
        BOLD = '\033[1m'
        print(BOLD, "Which treat would you like?")
        print(RESET, "")
        from tabulate import tabulate
        BLUE = '\033[34m'
        print(BLUE, tabulate(treats, headers='firstrow', tablefmt='grid'))
        treat_selection = int(input('Enter the ID of the treat you would like: '))
        print(RESET, f"That will be ${treats[treat_selection][2]} please.")
        if treats[treat_selection][3] > 0:
            print('Enjoy your treat!')
            treats[treat_selection][3] -= 1
        elif treats[treat_selection][3] == 0:
            RED = '\033[31m'
            print(RED, f"Oh dear! We are all out of {treats[treat_selection][1]}.")
        time.sleep(4)
    elif want_treat == 'N':
        print(RESET, 'No worries, have a good rest of your day!')
        time.sleep(4)
