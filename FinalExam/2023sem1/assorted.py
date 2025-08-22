biscuits = []
biscuits.extend(['Monte Carlo']*7)
biscuits.extend(['Shortbread Cream']*7)
biscuits.extend(['Delta Cream']*6)
biscuits.extend(['Orange Slice']*6)
biscuits.extend(['Kingston']*5)

def print_biscuits():
    """Print the current biscuits in the jar."""
    biscuit_names = set(biscuits) # dictionary
    for biscuit in biscuit_names:
        print(f"{biscuit}: {biscuits.count(biscuit)}")
print_biscuits()

def valid_input(prompt):
    try:
        if 1 <= int(prompt) <= 99:
            return int(prompt)
    except ValueError:
        pass
    print("Invalid input. Please enter a year between 1 and 99.")