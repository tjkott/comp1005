# Bakery table printer with blue ANSI color formatting

# ANSI color code for blue
BLUE = '\033[94m'
RESET = '\033[0m'  # Reset to default color

# Data for bakery items
bakery_items = [
    [1, "Choco Pie", "$1.00", 5],
    [2, "Hello Panda", "$0.50", 10],
    [3, "Fortune Cookie", "$0.30", 10],
    [4, "Fig Roll", "$0.30", 10],
    [5, "Maliban Orange Cream", "$0.30", 10],
    [6, "Maliban Custard Cream", "$0.30", 10],
    [7, "Maliban Chocolate Cream", "$0.30", 10],
    [8, "Eccles Cake", "$0.80", 5],
    [9, "Wagon Wheel", "$1.50", 0]
]

# Get maximum widths for each column for proper spacing
max_id_width = max(len(str(item[0])) for item in bakery_items)
max_name_width = max(len(item[1]) for item in bakery_items)
max_price_width = max(len(item[2]) for item in bakery_items)
max_count_width = max(len(str(item[3])) for item in bakery_items)

# Adjust for header text
max_id_width = max(max_id_width, 1)  # '#' is 1 character
max_name_width = max(max_name_width, 4)  # 'Name' is 4 characters
max_price_width = max(max_price_width, 5)  # 'Price' is 5 characters
max_count_width = max(max_count_width, 5)  # 'Count' is 5 characters

# Add padding
id_width = max_id_width + 2
name_width = max_name_width + 2
price_width = max_price_width + 2
count_width = max_count_width + 2

# Calculate total width for the table
total_width = id_width + name_width + price_width + count_width + 5  # 5 for the vertical separators

# Print the table
def print_table():
    # Print top border
    print(f"{BLUE}+{'-' * (total_width - 2)}+{RESET}")
    
    # Print header
    print(f"{BLUE}| #{' ' * (id_width - 1)}| Name{' ' * (name_width - 4)}| Price{' ' * (price_width - 5)}| Count{' ' * (count_width - 5)}|{RESET}")
    
    # Print separator
    print(f"{BLUE}+{'-' * (id_width)}+{'-' * (name_width)}+{'-' * (price_width)}+{'-' * (count_width)}+{RESET}")
    
    # Print data rows
    for item in bakery_items:
        item_id = str(item[0])
        name = item[1]
        price = item[2]
        count = str(item[3])
        
        print(f"{BLUE}| {item_id}{' ' * (id_width - len(item_id))}| {name}{' ' * (name_width - len(name))}| {price}{' ' * (price_width - len(price))}| {count}{' ' * (count_width - len(count))}|{RESET}")
    
    # Print bottom border
    print(f"{BLUE}+{'-' * (total_width - 2)}+{RESET}")
    
    # Print prompt for user selection
    print("Enter your selection: ", end="")

# Run the program
print_table()