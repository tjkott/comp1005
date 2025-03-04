#
# Unipass session 1 - Control structures
#

# (1) 
def grade_system(mark):
    if mark < 50:
        grade = "F"
    elif 50 <= mark <= 59:
        grade = "P"
    elif 60 <= mark <= 69:
        grade = "C"
    elif 70 <= mark <= 79:
        grade = "D"
    elif 80 <= mark <= 100:
        grade = "HD"
    else:
        grade = "Invalid mark"
    return grade

print(f"Your grade is: ", grade_system(int(input('What is your mark?:  '))))

# (2)

def numbersbetween5and15():
    for i in range(5, 16):
        print(i)

#print(numbersbetween5and15())

# (3) - Using for loop sum every number 
# between 1 and 50 together and print the result. 

def sumofnumbers():
    sum = 0
    for i in range(1, 51):
        sum += i
    return sum

print(sumofnumbers())

# (4) Write a controlstaatement that if the input number is odd, 
# change its value so that it is 3 times plus 1 of its original number. 
# But if the input number is 