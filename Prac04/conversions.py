#
# conversions.py – module with functions to convert between units #
# fahr2cel : Convert from Fahrenheit to Celsius.
#

def fahr2cel(fahr):
    """Convert from Fahrenheit to Celsius. Argument:
    fahr – the temperature in Fahrenheit """
    celsius = (fahr - 32) * (5/9)
    return celsius

def cel2fahr(cel):
    """Convert from Celsius to Fahrenheit. Argument:
    cel – the temperature in Celsius """
    fahrenheit = (cel * (9/5)) + 32
    return fahrenheit

def cel2kel(cel):
    """Convert from Celsius to Kelvin. Argument:
    cel – the temperature in Celsius """
    kelvin = cel + 273.15
    return kelvin

def kel2cel(kel):
    """Convert from Kelvin to Celsius. Argument:
    kel – the temperature in Kelvin """
    celsius = kel - 273.15
    return celsius

def fahr2kel(fahr):
    """Convert from Fahrenheit to Kelvin. Argument:
    fahr – the temperature in Fahrenheit """
    kelvin = (fahr - 32) * (5/9) + 273.15
    return kelvin

def kel2fahr(kel):
    """Convert from Kelvin to Fahrenheit. Argument:
    kel – the temperature in Kelvin """
    fahrenheit = (kel - 273.15) * (9/5) + 32
    return fahrenheit