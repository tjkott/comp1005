#
# strings1.py: Read in a string and print it in reverse
#              using a loop and a method call

instring = input('Enter a string... ')

# *** add (2) upper and (3) duplicating code here

# reversing with a while loop
print('Reversed string is : ', end='')
index = len(instring)-1
while index > -1:
    print(instring[index], end='')
    index = index - 1
print()

# reversing with a for-range loop
print('Reversed string is : ', end='')
for index in range(len(instring)-1, -1, -1):
    print(instring[index], end='')
print()

# reversing with slicing
print('Reversed string is :', instring[::-1])   