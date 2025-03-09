#
# converter.py - A conversion machine that converts between Celcius, Farenheit and Kelvin
#
from conversions import *
from tabulate import tabulate
print("\n Welcome to the conversion machine!\n")

conversions = [
    ['Selection','Unit to Convert', 'Converted value'],
    ['1','Celcius', 'Farenheit'],
    ['2','Celcius', 'Kelvin'],
    ['3','Farenheit', 'Celcius'],
    ['4','Farenheit', 'Kelvin'],
    ['5','Kelvin', 'Celcius'],
    ['6','Kelvin', 'Farenheit']]

print(tabulate(conversions, headers='firstrow', tablefmt='grid'))
selection = input("What would you like to convert?")

def selector(selection):
    if selection == '1':
        celcius = float(input("Enter the temperature in Celcius: "))
        print(f"{celcius} Celcius is {cel2fahr(celcius)} Farenheit")
    elif selection == '2':
        celcius = float(input("Enter the temperature in Celcius: "))
        print(f"{celcius} Celcius is {cel2kel(celcius)} Kelvin")
    elif selection == '3':
        farenheit = float(input("Enter the temperature in Farenheit: "))
        print(f"{farenheit} Farenheit is {fahr2cel(farenheit)} Celcius")
    elif selection == '4':
        farenheit = float(input("Enter the temperature in Farenheit: "))
        print(f"{farenheit} Farenheit is {fahr2kel(farenheit)} Kelvin")
    elif selection == '5':
        kelvin = float(input("Enter the temperature in Kelvin: "))
        print(f"{kelvin} Kelvin is {kel2cel(kelvin)} Celcius")
    elif selection == '6':
        kelvin = float(input("Enter the temperature in Kelvin: "))
        print(f"{kelvin} Kelvin is {kel2fahr(kelvin)} Farenheit")
    else:
        print("Invalid selection")
        selection = input("Please input a valid selection from the table: ")
        print(selector(selection))

print(selector(selection))
print("\nThank you for using the conversion machine!")