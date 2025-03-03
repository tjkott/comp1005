import random
import math
import matplotlib
import matplotlib.pyplot as plt
from time import time

def calculate_pi(num_darts):
    """
    Calculate an approximation of pi using the Monte Carlo method.
    
    Args:
        num_darts: Number of random darts to throw
        
    Returns:
        Approximation of pi and the points for visualization
    """
    inside_circle = 0
    circle_points = []
    square_points = []
    
    # Throw random darts
    for _ in range(num_darts):
        # Generate random coordinates between -1 and 1
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        
        # Calculate distance from origin (0,0)
        distance = x**2 + y**2
        
        # Check if the dart landed inside the circle
        if distance <= 1:
            inside_circle += 1
            circle_points.append((x, y))
        else:
            square_points.append((x, y))
    
    # Calculate pi: Area of circle = pi * r^2, Area of square = (2r)^2 = 4r^2
    # So pi = 4 * (area of circle / area of square) = 4 * (darts in circle / total darts)
    pi_approximation = 4 * inside_circle / num_darts
    
    return pi_approximation, circle_points, square_points

def visualize_darts(circle_points, square_points, pi_approx, num_darts):
    """
    Visualize the dart throws and the resulting approximation of pi.
    """
    plt.figure(figsize=(10, 10))
    
    # Plot circle points in blue
    circle_x = [p[0] for p in circle_points]
    circle_y = [p[1] for p in circle_points]
    plt.scatter(circle_x, circle_y, color='blue', s=10, alpha=0.6, label='Inside circle')
    
    # Plot square points in red
    square_x = [p[0] for p in square_points]
    square_y = [p[1] for p in square_points]
    plt.scatter(square_x, square_y, color='red', s=10, alpha=0.6, label='Outside circle')
    
    # Draw the circle
    circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=2)
    plt.gca().add_patch(circle)
    
    # Draw the square
    plt.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'black', linewidth=2)
    
    plt.axis('equal')
    plt.grid(True)
    plt.title(f'Estimating π using the Monte Carlo method\n'
              f'Darts thrown: {num_darts}\n'
              f'π approximation: {pi_approx:.8f}\n'
              f'Actual π: {math.pi:.8f}\n'
              f'Error: {abs(pi_approx - math.pi):.8f}', fontsize=12)
    plt.legend()
    plt.savefig('monte_carlo_pi.png')
    plt.show()

def run_simulation(num_darts=10000, visualize=True, sample_size=1000):
    """
    Run the Monte Carlo simulation with the specified number of darts.
    
    Args:
        num_darts: Total number of darts to throw
        visualize: Whether to create a visualization
        sample_size: Number of points to plot (for performance reasons)
    """
    start_time = time()
    
    pi_approx, circle_points, square_points = calculate_pi(num_darts)
    
    end_time = time()

    duration = end_time - start_time
    
    print(f"Number of darts: {num_darts}")
    print(f"π approximation: {pi_approx:.8f}")
    print(f"Actual π value : {math.pi:.8f}")
    print(f"Error          : {abs(pi_approx - math.pi):.8f}")
    print(f"Execution time : {duration:.4f} seconds")
    
    if visualize:
        # If there are many points, sample a subset for visualization
        if len(circle_points) > sample_size:
            circle_sample = random.sample(circle_points, min(sample_size, len(circle_points)))
            square_sample = random.sample(square_points, min(sample_size, len(square_points)))
            visualize_darts(circle_sample, square_sample, pi_approx, num_darts)
        else:
            visualize_darts(circle_points, square_points, pi_approx, num_darts)

if __name__ == "__main__":
    # Uncomment different dart counts to see how accuracy improves
    run_simulation(1000)    # Try with 1,000 darts
    # run_simulation(10000)   # Try with 10,000 darts
    # run_simulation(100000)  # Try with 100,000 darts
    # run_simulation(1000000, visualize=False)  # Try with 1,000,000 darts (no visualization)