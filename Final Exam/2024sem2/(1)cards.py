# QUESTION ONE

cards = [] # Holds deck of cards = 13 cards from 4 suits
hand = [] # holds selected cards bu user. 
value = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
cards.extend([v+"H" for v in value])  # Hearts card suit
cards.extend([v+"D" for v in value])  # Diamonds card suit
cards.extend([v+"C" for v in value])  # Clubs card suit
cards.extend([v+"S" for v in value])  # Spades card suit

# (a) 
"""(4 marks) Extending the above code, write code to:
 i) Ask if the user if they would like a card
 ii) While there are still cards in the deck, and they want a card…
 iii) Select a card randomly from the deck of cards, put it into the hand and
 delete it from cards
 iv) Ask if they want another card, and continue from (ii)
 v) When finished, print the number of cards remaining, and then the cards in
 the player’s hand"""
def take_card():
    """
    Allows users to take 1 card from the deck."""
    while len(cards) > 0:
        user_question = input("Would you like a card? (Y/N): ").strip().upper()
        if user_question == "Y":
            import random
            card = random.choice(cards)  # Select a random card from the deck
            cards.remove(card)  # Remove the selected card from the deck
            hand.append(card)  # Add the selected card to the user's hand
            print(f"You drew: {card}")
        elif user_question == "N":
            print(f"Number of cards remaining in the deck: {len(cards)}")
            print(f"Number of cards in your hand: {len(hand)}")
            break

# (b) 
""" b) (6 marks) Write a function take_cards(c_list, c_count) to allow multiple cards to be
 taken at once. Your function should:
 i) Check if there are enough cards (c_count) in the card list (c_list) .
 ii) Return a list of randomly selected cards, or an empty list if not enough.
 Selected cards must be deleted from the cards deck"""
def take_cards(c_list, c_count):
    """
    Allow user to tak multiple cards from the deck.
    """
    import random
    for i in range(c_count):
        if len(c_list) > 0:
            card = random.choice(c_list)
            c_list.remove(card)
            hand.append(card)
        else:
            print("No more cards left in the deck.")
            break
    return hand

# (c)
""" c) (3 marks) Provide the code to:
 i) Ask how many players are playing the card game.
 ii)  Create a list of lists “hands” to hold all of the players’ cards
 iii) Call the take_cards function from part (b) to select seven cards for each
 player into the hands list """
def card_distributor(n_players):
    import random
    list_of_lists = []
    for i in range(n_players):
        player_hand = [take_cards(cards, 7)]
        list_of_lists.append(player_hand)
    return list_of_lists
#print(card_distributor(2))  # Example: distribute cards to 4 players


#(e) 
"""Write two versions of code to generate the following lists.
i)	Use for loops in one version ii)	Use list comprehensions for the second version.
i.	Given a list of strings in templist, convert each to a floating-point number and convert to kilometres (conversion factor 1.60934)
	miles_list = ['4', '2', '42'] 	(3 marks) 
becomes [6.43736, 3.21868, 67.59228] 
"""
miles_list = ['4', '2', '42']
def converterLoopVersion():
    km_list = []
    for mile in miles_list:
        km_list.append(float(mile) * 1.60934)
    return km_list
def converterListVersion():
    km_list = [float(mile) * 1.60934 for mile in miles_list]
    return km_list
print(converterLoopVersion())
print(converterListVersion())

# ii
"""ii.	Write code to create a new list containing the first two letters in the words in wordlist
	– first letter in uppercase and second in lowercase:	(3 marks) 
wordlist = ["forty" , "two", "forty two"] becomes [“Fo”,”Tw”,”Fo”] 
"""