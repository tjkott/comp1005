class Car:
    # Class constant
    MAX_SPEED = 240  # Maximum speed in km/h

    # Class variable
    manufacturer = "Generic Motors"

    def __init__(self, model, color):
        # Instance variables
        self.model = model
        self.color = color
        self.current_speed = 0

    # Method to accelerate the car
    def accelerate(self, speed_increment):
        if self.current_speed + speed_increment <= Car.MAX_SPEED:
            self.current_speed += speed_increment
            print(f"The car has accelerated to {self.current_speed} km/h.")
        else:
            self.current_speed = Car.MAX_SPEED
            print(f"The car is at its maximum speed of {Car.MAX_SPEED} km/h.")

    # Method to brake the car
    def brake(self, speed_decrement):
        if self.current_speed - speed_decrement >= 0:
            self.current_speed -= speed_decrement
            print(f"The car has slowed down to {self.current_speed} km/h.")
        else:
            self.current_speed = 0
            print("The car has stopped.")

# Example usage:
my_car = Car("Sedan", "Red")
print(f"Manufacturer: {Car.manufacturer}, Model: {my_car.model}, Color: {my_car.color}")
my_car.accelerate(50)
my_car.brake(20)
