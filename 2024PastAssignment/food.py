import numpy as np
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Food():
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos

    def get_pos(self):
        return self.pos