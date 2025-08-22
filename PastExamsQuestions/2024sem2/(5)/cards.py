# cards.py

class Card:
    def __init__(self, character: str, strength: int, intelligence: int, speed: int, health: int):
        self.character = character
        if not 1 <= strength <= 5:
            raise ValueError("Strength rating must be between 1 and 5.")
        self.strength = strength
        if not 1 <= intelligence <= 5:
            raise ValueError("Intelligence rating must be between 1 and 5.")
        self.intelligence = intelligence
        if not 1 <= speed <= 5:
            raise ValueError("Speed rating must be between 1 and 5.")
        self.speed = speed
        if not 1 <= health <= 5:
            raise ValueError("Health rating must be between 1 and 5.")
        self.health = health
    def __str__(self):
        return (f"Character: {self.character}\n"
                f"  Strength:     {self.strength}\n"
                f"  Intelligence: {self.intelligence}\n"
                f"  Speed:        {self.speed}\n"
                f"  Health:       {self.health}")

# Example Usage (optional, for testing)
if __name__ == '__main__':
    try:
        card1 = Card("Wizard", 3, 5, 2, 3)
        print(card1)
        print("-" * 20)
        card2 = Card("Warrior", 5, 2, 3, 5)
        print(card2)
        # Example of invalid input
        # card3 = Card("Rogue", 4, 4, 6, 3) 
        # print(card3)
    except ValueError as e:
        print(f"Error creating card: {e}")