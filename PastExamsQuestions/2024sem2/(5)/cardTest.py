from cards import Card
def main():
    card_collection = []
    print("--- Dog Breed Card Entry Program ---")
    choice = input("Do you want to enter a dog breed's card? (Y/N): ").strip().upper()
    while choice == "Y":
        breed_name = input("Enter dog breed name: ").strip()
        if not breed_name:
            print("  Breed name cannot be empty. Please try again.")
            choice = input("Do you want to enter another dog breed's card? (Y/N): ").strip().upper()
            continue
        try:
            strength_str = input(f"Enter strength for {breed_name} (1-5): ")
            strength = int(strength_str)
            intelligence_str = input(f"Enter intelligence for {breed_name} (1-5): ")
            intelligence = int(intelligence_str)
            speed_str = input(f"Enter speed for {breed_name} (1-5): ")
            speed = int(speed_str)
            health_str = input(f"Enter health for {breed_name} (1-5): ")
            health = int(health_str)
            current_card = Card(character=breed_name, 
                                strength=strength, 
                                intelligence=intelligence, 
                                speed=speed, 
                                health=health)
            card_collection.append(current_card)
            print(f"'{breed_name}' card added successfully.")

        except ValueError as e:
            print(f"  Input Error: {e}")
            print(f"  Could not create card for '{breed_name}'. Please ensure all ratings are whole numbers between 1 and 5, and breed name is not empty.")
        choice = input("Do you want to enter another dog breed's card? (Y/N): ").strip().upper()

    print("\n--- Program Finished ---")

if __name__ == "__main__":
    main()
