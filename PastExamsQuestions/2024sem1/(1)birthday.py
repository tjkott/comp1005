myname = "Thejana Kottawatta"
myyear = 19
print(f"Hello, my name is {myname}."   )

def valid_input(prompt):
    input_str = input(prompt).strip() 
    try:
        if 1 <= int(input_str) <= 99:
            return int(input_str)  
    except ValueError:
        pass
    print("Invalid input. Please enter a year between 1 and 99.")
    return valid_input(prompt)  
user_year = valid_input("What is your year? ")

def print_cake(age):
    cake_width = 10 
    cols = (age + 1) // 2 
    candles_g1_count = (age + 1) // 2 
    candles_g2_count = age // 2      
    cake_width = cols * 2
    if cake_width == 0:
        cake_width = 2 
    print("* " * candles_g1_count)
    candle_line2_part1 = "*|" * candles_g2_count
    candle_line2_padding = "  " * (candles_g1_count - candles_g2_count) 
    print(candle_line2_part1 + candle_line2_padding)
    print("| " * candles_g1_count)
    print("#" * cake_width)
    print("=" * cake_width)
    print("#" * cake_width)
    print("=" * cake_width)
    print("#" * cake_width)
print_cake(user_year)