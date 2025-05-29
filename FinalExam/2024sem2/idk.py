import numpy as np
import matplotlib.pyplot as plt
import csv

# Initialize the grid
grid = np.zeros((20, 20), dtype=int)
# grid[2, 3] = 1 # You can keep this initial point if you like

# --- Function definitions (from your example) ---
def make_tree(grid, topleft_pos, size, colour):
    x, y = topleft_pos
    # Ensure indices are within bounds
    y_end = min(y + size, grid.shape[0])
    x_end = min(x + size, grid.shape[1])
    grid[y:y_end, x:x_end] = colour

def make_house(grid, topleft_pos, height, width, colour):
    x, y = topleft_pos
    # Ensure indices are within bounds
    y_end = min(y + height, grid.shape[0])
    x_end = min(x + width, grid.shape[1])
    grid[y:y_end, x:x_end] = colour

# --- CSV Processing ---
csv_file_path = 'objects.csv' # Make sure this path is correct

try:
    with open(csv_file_path, mode='r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader) # Skip the header row

        for row in reader:
            object_type = row[0].strip().lower()
            params = [int(p) for p in row[1:] if p] # Convert non-empty params to int

            if object_type == 'tree':
                if len(params) == 4: # x, y, size, colour
                    topleft_pos = (params[0], params[1])
                    size = params[2]
                    colour = params[3]
                    make_tree(grid, topleft_pos, size, colour)
                    print(f"Made tree at {topleft_pos} with size {size}, colour {colour}")
                else:
                    print(f"Skipping malformed tree row: {row}")
            elif object_type == 'house':
                if len(params) == 5: # x, y, height, width, colour
                    topleft_pos = (params[0], params[1])
                    height = params[2]
                    width = params[3]
                    colour = params[4]
                    make_house(grid, topleft_pos, height, width, colour)
                    print(f"Made house at {topleft_pos} with H:{height}, W:{width}, colour {colour}")
                else:
                    print(f"Skipping malformed house row: {row}")
            else:
                print(f"Unknown object type: {object_type} in row: {row}")

except FileNotFoundError:
    print(f"Error: The file {csv_file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")


# --- Plotting (from your example) ---
print("\nFinal grid:")
print(grid)
plt.imshow(grid, cmap='jet') # Or any other cmap you prefer e.g., 'viridis', 'plasma'
plt.colorbar(label='Object ID / Colour')
plt.title('Objects from CSV on Grid')
plt.xlabel('X-coordinate')
plt.ylabel('Y-coordinate')
plt.xticks(np.arange(0, 20, 2))
plt.yticks(np.arange(0, 20, 2))
plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
plt.show()