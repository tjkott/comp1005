# first example,no matplot 
import pygame
import sys
import csv
import math
import random
import argparse
import asyncio
import platform

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
ORANGE_SHADES = [
    (255, 165, 0),  # Level 1
    (255, 140, 0),  # Level 2
    (255, 115, 0),  # Level 3
    (255, 90, 0),   # Level 4
    (255, 69, 0)    # Level 5
]

class Bee:
    def __init__(self, x, y, hive):
        self.x = x
        self.y = y
        self.state = "in_hive"  # States: in_hive, seeking_nectar, returning
        self.nectar = 0
        self.hive = hive
        self.target = None

    def find_nearest_flower(self, flowers):
        if not flowers:
            return None
        min_dist = float('inf')
        nearest = None
        for flower in flowers:
            if flower.nectar > 0:
                dist = math.hypot(self.x - flower.x, self.y - flower.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest = flower
        return nearest

    def move(self, flowers, barriers):
        if self.state == "in_hive":
            self.state = "seeking_nectar"
            self.target = self.find_nearest_flower(flowers)
        elif self.state == "seeking_nectar":
            if self.target and self.target.nectar > 0:
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = math.hypot(dx, dy)
                if dist < 1:
                    self.nectar = min(self.target.nectar, 1)
                    self.target.nectar -= self.nectar
                    self.state = "returning"
                    self.target = self.hive
                else:
                    step = 1 / dist
                    new_x = self.x + dx * step
                    new_y = self.y + dy * step
                    if not self.collides(new_x, new_y, barriers):
                        self.x = new_x
                        self.y = new_y
            else:
                self.target = self.find_nearest_flower(flowers)
        elif self.state == "returning":
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist < 1:
                if self.nectar > 0:
                    self.hive.deposit_nectar(self.nectar)
                    self.nectar = 0
                self.state = "in_hive"
                self.target = None
            else:
                step = 1 / dist
                new_x = self.x + dx * step
                new_y = self.y + dy * step
                if not self.collides(new_x, new_y, barriers):
                    self.x = new_x
                    self.y = new_y

    def collides(self, x, y, barriers):
        for barrier in barriers:
            if math.hypot(x - barrier.x, y - barrier.y) < 1:
                return True
        return False

class Flower:
    def __init__(self, x, y, name, color, nectar=10):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.nectar = nectar

class Hive:
    def __init__(self, x, y, frame_size=5):
        self.x = x
        self.y = y
        self.frame_size = frame_size
        self.comb = [[0 for _ in range(frame_size)] for _ in range(frame_size)]  # 0: empty, 1: comb, 2-6: nectar levels
        self.comb_built = False
        self.build_step = 0

    def build_comb(self):
        if not self.comb_built:
            if self.build_step < self.frame_size * self.frame_size:
                row = self.build_step // self.frame_size
                col = self.build_step % self.frame_size
                self.comb[row][col] = 1
                self.build_step += 1
            else:
                self.comb_built = True

    def deposit_nectar(self, amount):
        if not self.comb_built:
            return
        for i in range(self.frame_size):
            for j in range(self.frame_size):
                if self.comb[i][j] >= 1 and self.comb[i][j] < 6:
                    self.comb[i][j] = min(self.comb[i][j] + amount, 6)
                    return

class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class BeeWorld:
    def __init__(self, map_file=None, param_file=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bee World Simulation")
        self.clock = pygame.time.Clock()
        self.hive = Hive(WIDTH // CELL_SIZE // 2, HEIGHT // CELL_SIZE // 2)
        self.bees = [Bee(self.hive.x, self.hive.y, self.hive) for _ in range(5)]
        self.flowers = []
        self.barriers = []
        self.running = True
        self.interactive = map_file is None

        if map_file:
            self.load_map(map_file)
        else:
            self.flowers = [
                Flower(5, 5, "Daisy", YELLOW, 10),
                Flower(15, 15, "Rose", (255, 0, 0), 10)
            ]
            self.barriers = [Barrier(10, 10)]

        if param_file:
            self.load_params(param_file)

    def load_map(self, map_file):
        with open(map_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "flower":
                    x, y, name, r, g, b, nectar = map(float, row[1:])
                    self.flowers.append(Flower(x, y, name, (r, g, b), nectar))
                elif row[0] == "barrier":
                    x, y = map(float, row[1:3])
                    self.barriers.append(Barrier(x, y))

    def load_params(self, param_file):
        with open(param_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "bees":
                    num_bees = int(row[1])
                    self.bees = [Bee(self.hive.x, self.hive.y, self.hive) for _ in range(num_bees)]
                elif row[0] == "frame_size":
                    self.hive.frame_size = int(row[1])
                    self.hive.comb = [[0 for _ in range(self.hive.frame_size)] for _ in range(self.hive.frame_size)]

    def draw(self):
        self.screen.fill(GREEN)
        # Draw hive
        for i in range(self.hive.frame_size):
            for j in range(self.hive.frame_size):
                x = (self.hive.x + i - self.hive.frame_size // 2) * CELL_SIZE
                y = (self.hive.y + j - self.hive.frame_size // 2) * CELL_SIZE
                if self.hive.comb[i][j] == 1:
                    pygame.draw.rect(self.screen, BROWN, (x, y, CELL_SIZE, CELL_SIZE))
                elif self.hive.comb[i][j] > 1:
                    color = ORANGE_SHADES[min(self.hive.comb[i][j] - 2, 4)]
                    pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))

        # Draw flowers
        for flower in self.flowers:
            pygame.draw.circle(self.screen, flower.color, (flower.x * CELL_SIZE, flower.y * CELL_SIZE), 5)

        # Draw barriers
        for barrier in self.barriers:
            pygame.draw.rect(self.screen, BLACK, (barrier.x * CELL_SIZE, barrier.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw bees
        for bee in self.bees:
            pygame.draw.circle(self.screen, YELLOW, (int(bee.x * CELL_SIZE), int(bee.y * CELL_SIZE)), 3)

        pygame.display.flip()

    async def run(self):
        while self.running:
            if self.interactive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.running = False

            self.hive.build_comb()
            for bee in self.bees:
                bee.move(self.flowers, self.barriers)
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(1.0 / FPS)

        pygame.quit()

def main():
    parser = argparse.ArgumentParser(description="Bee World Simulation")
    parser.add_argument('-i', '--interactive', action='store_true', help="Run in interactive mode")
    parser.add_argument('-f', '--map_file', type=str, help="Map file for batch mode")
    parser.add_argument('-p', '--param_file', type=str, help="Parameter file for batch mode")
    args = parser.parse_args()

    if args.interactive:
        world = BeeWorld()
    else:
        if not args.map_file or not args.param_file:
            print("Batch mode requires both map and parameter files")
            sys.exit(1)
        world = BeeWorld(args.map_file, args.param_file)

    if platform.system() == "Emscripten":
        asyncio.ensure_future(world.run())
    else:
        asyncio.run(world.run())

if __name__ == "__main__":
    main()