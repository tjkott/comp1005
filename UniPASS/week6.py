fruits = ['apple', 'banana', 'cherry']
newList = [n for n in fruits if 'a' in n]
# print(newList)

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
oddDoubles = [n*2 for n in numbers if n % 2 == 1]
#print(oddDoubles)

squares = []
squares = [n**2 for n in range(1, 11)]
print(squares)