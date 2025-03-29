import numpy as np

def array_print(myarray):
    count = 0
    for row in myarray:
        for element in row:
            print('num:', element)
            count += 1
    return(count)

#print(array_print(np.array([[1,2,3],[4,5,6]])))

# Pig Latin
def pig_latin(word):
    vowels = ['a','e','i','o','u']
    first_half = ""
    for letter in range(len(word)):
        if word[0] in vowels:
            return word + 'yay'
        elif word[letter] not in vowels:
            first_half += word[letter]
        else: 
            break
    return (first_half + 'ay')

print(pig_latin('dog'))
print(pig_latin('plants'))