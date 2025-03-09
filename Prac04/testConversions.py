#
# testConversions.py - tests the functions in conversions.py 
#
from conversions import *
print("\nTESTING CONVERSIONS\n")
testF = 100
testC = 38
testK = 320
print(f"100F in Celcius is: {fahr2cel(testF)}F. Kelvin is: {fahr2kel(testF)}")
print(f"38C in Fahrenheit is: {cel2fahr(testC)}F. Kelvin is: {cel2kel(testC)}")
print(f"320K in Celcius is: {kel2cel(testK)}F. Fahrenheit is: {kel2fahr(testK)}")
print("\nTESTING COMPLETE\n")