# (d) 
"""d) (6 marks) Provide the code to generate the sample output, above.
i.	Ask the user enter the number of rows and columns
ii.	For each user entry, test that it is in a valid range (1-20), use a loop to ask them to re-enter the value and continue looping until it is valid. You can assume the user enters an integer.
iii.	Print alternating + and | characters
iv.	On each row, use a for loop to print the required + or --- characters"""

def valid_input(prompt):
    while True:
        try:
            value = int(input(prompt))  # 1. Get input and try to convert to integer
            if 1 <= value <= 20:               # 2. Check if it's positive
                return value            # 3. If yes, return it and exit the loop
        except ValueError:
            pass
        print("Invalid input. Please enter a positive whole number.")

num_rows = valid_input("Enter number of rows: ")
num_cols = valid_input("Enter number of columns: ")

print("+---" *num_cols + "+")
for i in range (num_rows):
    print("|   " *num_cols + "|")
    print("+---" *num_cols + "+")
