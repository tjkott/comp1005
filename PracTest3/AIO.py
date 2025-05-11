# Student Name: <put your name here> 
# Student ID:   <put your ID here>
#
# buzzness.py - module with class definitions for simulation of bee colony
#
# Version information: 
#     2024-04-07 : Initial Version released
#
import random

class Bee(): # Providing state and behaviour for worker bee in the simulation
    def __init__(self, ID, pos):
        """
        Initialise Bee object
        ID:  identifier for the bee
        pos: (x,y) position of bee
        age: set to zero at birth
        inhive: is the bee inside the hive, or out in the world?, True at birth
        """
        self.ID = ID
        self.pos = pos
        self.age = 0
        self.inhive = True

    def step_change(self, subgrid=None, maxX=None, maxY=None): # sets default value of the maxX parameter to be None (empty value)
        """
        Update Bee object on each timestep
        subgrid: gives view of surroundings for choosing where to move (not used for now)
        Made changes so that bees don't move outside the boundary of the plots. 
        """
        # maxX and maxY are the maximum coordinate boundaries of the plot. 
        validmoves = [(0,0), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]  ## (d) In the Bee, update the valid moves to inlcude all 9 Moore neighbouhoods. 

        # Try to find a valid move that keeps the bee within boundaries
        valid_step = False #default assumption of hte new step is false. 
        attempts = 0
        max_attempts = 10  # In order to prevent infinite loop
        
        while not valid_step and attempts < max_attempts:
            move = random.choice(validmoves)  # randomly choose a move out of the validmoves array. 
            newX = self.pos[0] + move[0]
            newY = self.pos[1] + move[1]
            
            if maxX is None or maxY is None: # Check if new position is within boundaries
                valid_step = True
            else:
                if 0 <= newX < maxX and 0 <= newY < maxY: #Ensure the new position is in between the origin and the max coordinates of the pot. 
                    valid_step = True
            attempts += 1
        
        if valid_step: 
            print(f"{self.ID}: {self.pos} -> {(newX, newY)}")
            self.pos = (newX, newY)  # update the position of the bee
        else:
            # If no valid_steps found after max attempts, stay in place
            print(f"{self.ID}: Staying at {self.pos} (no valid moves)")

        # Remove the duplicate position update that was causing bugs
        # print(self.pos, move)
        # self.pos = (self.pos[0] + move[0], self.pos[1] + move[1]) <- This line was causing bees to move outside boundaries
    
    def get_pos(self):
        return self.pos
    
    def get_inhive(self):
        
        return self.inhive
    
    def set_inhive(self, value):
        self.inhive = value

simlength = 5
hiveX = 30
hiveY = 25
hive = np.zeros((hiveX,hiveY))
ready_for_honey = 10
# generate 5 bees. 
blist = [Bee(f"b{i+1}", (np.random.randint(0, hiveX), np.random.randint(0, hiveY))) for i in range(5)] # for loop for generating 5 bees 

def plot_hive(hive, blist, ax): #ax is a single axes which you can drae your subploot. 
    ## (b) readiness for honey

    if ready_for_honey == 10:
        hive[:, :] = 10
    else:
        hive[:, :] = 10 - ready_for_honey # 10 is brown, not ready, 0 is ready
    
    ## (c) Stripe of comb in the centre. 
    stripe_center = hiveX // 2 # Since, we are working with arrays, floats cannot be used in slicing. Thus, division with remainder.
    hive[int(stripe_center - 1): int(stripe_center+2), :] = 0 # Make the stripe white with the colour map. 

    for j in range(hiveY):
        if j % 2 == 0: # Even squares are yellow. 
            hive[int(stripe_center), j] = 5 # 5 is the yellow in the colourmap
    
    # x and y positions of the bees. 
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()] # list of x coordinates only if inhive = True
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]
    ax.imshow(hive.T, origin="lower", cmap='YlOrBr', vmin=0, vmax=10) # colour map for the hive.
    ax.scatter(xvalues, yvalues)

propertyX = 50
propertyY = 40
hive_position = 22, 20 # x,y position of the hive in the world.
world_bees = [Bee(f"wb{i+1}", (np.random.randint(0, propertyX), np.random.randint(0, propertyY))) for i in range(2)]
for b in world_bees:
    b.set_inhive(False)
def plot_world(ax):
    world = np.zeros((propertyX, propertyY)) #world is a 2D array of zeros.
    world[:, :] = 5 #Assign green value from the tab20 colourmap. 
    # (d) Add a variable to hold the hive position, pass it to world_plot to plot a square. 
    world[hive_position[0]:hive_position[0]+2, hive_position[1]:hive_position[1]+2] = 16 # Assign white value from the tab20 colourmap for the hive

    # alternating green and brown squares.
    for x in range(propertyX//2, propertyX): #from 'origin' of the plot to the end of the x-limit
        if x % 2 == 0: # if the i is even
            for y in range(propertyY//2, propertyY):
                if y % 2 == 0:
                    world[x, y] = 5 #green squares for eveb columns
                else:
                    world[x, y] = 10
        elif x % 2 == 1: #for odd index
            for y in range(propertyY//2, propertyY):
                world[x, y] = 5 #green row
    
    
    world[30:39, 5:10] = 0 # blue pond 
    world[10:15, 30:35] = 14 # gray patch

    #Vertical stripes
    for x in range(1, 10):
        if x % 2 == 0: # if the column is odd, set it to brown.
            world[x:x+1, 2:4] = 4 #Brown is 0
        else: #if the col is even set it to green
            world[x:x+1, 2:4] = 5 #Green is 4

    ## (c) Plotted with the tab20 colourmap. 
    ax.imshow(world.T, origin="lower", cmap='tab20', vmin=0, vmax=19)
    #Plot the world bees
    xvalues = [b.get_pos()[0] for b in world_bees]
    yvalues = [b.get_pos()[1] for b in world_bees]
    ax.scatter(xvalues, yvalues, c='black', marker='o', s=80)

# Run the simulation. 
for t in range(simlength):
    for b in blist:
        b.step_change(maxX=hiveX, maxY=hiveY) # pass the boundaries of the hive to the step_change function.
    for b in world_bees:
        b.step_change(maxX=propertyX, maxY=propertyY) # pass the boundaries of the world. 
    fig, axes = plt.subplots(1, 2, figsize=(15,6)) # 1 row with 2 columns sup fig
    
    ## (e) Plot a duplicate of the plot in the 2nd column and add a supertitle. 
    
    fig.suptitle(f"BEE WORLD. Simulation: {simlength}", fontsize=15, fontweight='bold')

    plot_hive(hive, blist, axes[0])
    axes[0].set_title('Bee Hive')
    axes[0].set_xlabel("X position")
    axes[0].set_ylabel("Y position")

    plot_world(axes[1]) # the property
    axes[1].set_title('Property') ## (e) Update the plot title to describe the plot. 
    axes[1].set_xlabel("X position")
    axes[1].set_ylabel("Y position")

    plt.show()
    plt.pause(1)
    simlength = simlength - 1
fig.savefig('task4.png')
