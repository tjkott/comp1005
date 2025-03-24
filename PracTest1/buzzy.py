"""
Student Name: Thejana Kottawatta Hewage
Student ID : 22307822"

buzzy.py: Prac test 1 – flight of the tiny bee

"""
def valid_distance_range():
    distance = int(input('Enter distance to flower...'))
    while 1 == 1:
        if 0 < distance < 20:
            return distance
        else:
            distance = input('Out of range, please re-enter...')
            return distance

def valid_time_range():
    time = int(input('Enter time for simulation...'))
    while 1 == 1:
        if 0 < time < 301:
            return time
        else:
            time = input('Out of range, please re-enter...')
            return time

def main():
    # Variables
    distance = valid_distance_range()
    time = valid_time_range()
    next_distance = 0
    direction = 1  #1 = default is forwards
    # Main Loop
    for t in range(time):
        if next_distance == 0:
            direction = 1
            print('\U0001F36F') # Honey pot
            next_distance += direction
            continue # prevent rest of the loop from executing if at the honey pot
        elif next_distance == distance:
            print(' '* next_distance, '\U0001F41D', '\U0001F338') #flower
            direction = -1
            next_distance += direction
        print(' '*next_distance, '\U0001F41D') #normal honey bee traversal
        next_distance += direction
main()