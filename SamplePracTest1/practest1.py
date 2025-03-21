#
# Student Name: Thejana Kottawatta
# Student ID: 22307822
#
#  practest1.py: Read in a string and print it
#
instring = input('Enter a string... ')
print('The input string is: ', instring)

outstring = ""
char_counter = 0

for char in instring:
    if char_counter % 3 == 2:
        outstring += char.lower()
    elif char_counter % 3 == 1:
        outstring += char.upper()
    elif char_counter % 3 == 0:
        outstring += '*'
    char_counter += 1

print(outstring)
