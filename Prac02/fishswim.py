#
# fishswim.py - simulate fish swimming in a tank
#

import time
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
numlines = 4

leftfish = ["  /", " /\\/", " \\/\\", "  \\"]
rightfish = ["  \\", " \\/\\", " /\\/", "  /"]

time_of_swim = int(input('How long should the fish swim for? :'))

for s in range(time_of_swim):
    for i in range(len(rightfish)):
        print(s*" " + rightfish[i]) 
    time.sleep(0.5)
    for j in range(numlines):
        print(LINE_UP, end=LINE_CLEAR) 

for s in range(time_of_swim, 0, -1):
    for i in range(len(leftfish)):
        print(s*" ", leftfish[i])
    time.sleep(0.5)
    for j in range(numlines):
        print(LINE_UP, end=LINE_CLEAR) 