class Cat():
    myclass = "Cat"
    def __init__(self, name, dob, colour, breed):
        self.name = name
        self.dob = dob
        self.colour = colour
        self.breed = breed
    def print_it(self):
        print(f"Name: {self.name}")
        print(f"DOB: {self.dob}")
        print(f"Colour: {self.colour}")
        print(f"Breed: {self.breed}")
        print(f"Class: {self.myclass}")

garfield = Cat('Garfield', '1/1/1978', 'Orange', 'Tabby')
print(garfield)
garfield.print_it()
