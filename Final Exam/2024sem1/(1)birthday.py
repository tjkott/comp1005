myname = "Thejana Kottawatta"
myyear = 19
print(f"Hello, my name is {myname}."   )

def valid_input(prompt):
    while True:
        try:
            if 1 <= int(prompt) <= 99:
                return int(prompt)
        except ValueError:
            pass
        print("Invalid input. Please enter a year between 1 and 99.")
user_name = input("What is your name? ")
user_year = valid_input("What is your year? ")

def commentYear():
    if myyear == user_year:
        print("We are in the same year!")
    elif myyear < user_year:
        print("You are younger than me.")
    else:
        print("You are older than me.")
commentYear()

def print_cake(age):
    cake_width = 10 
    # Determine the number of candle columns and candles in each "layer"
    # cols determines the width and the number of positions for the top layer of flames
    cols = (age + 1) // 2 
    
    # candles_g1_count: flames on the very top line, bodies on the third candle line
    candles_g1_count = (age + 1) // 2 
    # candles_g2_count: flame-and-body pairs on the middle candle line
    candles_g2_count = age // 2      

    # Cake width is determined by the candle columns
    # Each column is two characters wide (e.g., "* " or "*|")
    cake_width = cols * 2
    # Ensure a minimum width if calculations somehow result in zero for positive age (unlikely with int age)
    if cake_width == 0:
        cake_width = 2 

    # Print Candle Layers
    # Line 1: Flames of the first group of candles
    print("* " * candles_g1_count)

    # Line 2: Flame-and-body of the second group, plus padding to align with first group
    candle_line2_part1 = "*|" * candles_g2_count
    candle_line2_padding = "  " * (candles_g1_count - candles_g2_count) # Padding if age is odd
    print(candle_line2_part1 + candle_line2_padding)

    # Line 3: Bodies of the first group of candles
    print("| " * candles_g1_count)

    # Print Cake Body (3 layers, 5 lines total as per example)
    print("#" * cake_width)
    print("=" * cake_width)
    print("#" * cake_width)
    print("=" * cake_width)
    print("#" * cake_width)


for i in range(myyear//100)
if  i % 10 == 0:
    print("*", end="")
print()

