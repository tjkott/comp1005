"""a) (4 marks) Extending the above code, write code to:
i) Ask which biscuit they want
ii) If available, delete the selected biscuit, otherwise print an appropriate
message
iii) Ask if they want another biscuit. If they want another biscuit, and there are
still biscuits, continue from (i)
iv) If finished, print the number of biscuits remaining"""
biscuits = []
biscuits.extend(['Monte Carlo']*7)
biscuits.extend(['Shortbread Cream']*7)
biscuits.extend(['Delta Cream']*6)
biscuits.extend(['Orange Slice']*6)
biscuits.extend(['Kingston']*5)
#more = input('\nWould you like a biscuit (Y/N)... ')

def takeBiscuit():
    """(i) Ask which biscuit they want"""
    while len(biscuits) > 0 and more == 'Y':
        biscuit = input('Which biscuit would you like? ').strip()
        if biscuit in biscuits:
            biscuits.remove(biscuit)
            print(f'You have taken a {biscuit}.')
            biscuit = input('Would you like another biscuit (Y/N)? ').strip().upper()
            if biscuit == 'Y':
                continue
            elif biscuit == 'N':
                print(f'There are {len(biscuits)} biscuits remaining.')
                break
    else:
        print('No biscuits left in the jar.')

#takeBiscuit()

def take_biscuits(b_list, b_name, b_number):
    if b_list.count(b_name) >= b_number:
        print(f"There are enough {b_name} in the jar.")
        selected_biscuits = []
        for b in range(b_number):
            b_list.remove(b_name)
            selected_biscuits.append(b_name)
        return selected_biscuits
    else:
        print(f"Error: Not enough {b_name} biscuits available. Requested: {b_number}, Available: {b_list.count(b_name)}.")
        return []
"""3 marks) Provide the code to:
i) Ask for the biscuit type and the number required.
ii) Call the function from part (b)."""
print(take_biscuits(biscuits, input("Biscuit type: "), int(input("Number of biscuits: "))))
