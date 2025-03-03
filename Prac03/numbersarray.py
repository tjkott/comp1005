#
# numbersarray.py
#
print("Enter ten number...")
total = 0

for i in  range(10):
    print('Enter a number (', i, ')...')
    number = int(input())
    total = total + number
print('Total is ', total)
