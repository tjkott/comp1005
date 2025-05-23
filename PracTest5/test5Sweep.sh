#!/bin/bash

# Create a unique directory name for the experiment, including a timestamp
exp_dir="test5sweep_$(date "+%Y-%m-%d_%H.%M.%S")"
mkdir "$exp_dir"

# Copy the scripts into the experiment directory
cp test5.py "$exp_dir/"
cp test5Sweep.sh "$exp_dir/" # Copy itself for record-keeping

# Change into the experiment directory; exit if cd fails
cd "$exp_dir" || { echo "Failed to cd into $exp_dir"; exit 1; }

# Check if the correct number of command-line arguments are provided
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 low_r hi_r step_r low_a hi_a step_a"
    echo "Example: $0 0.001 0.003 0.001 0.1 0.5 0.2"
    exit 1
fi

# Assign command-line arguments to variables
low_r=$1
hi_r=$2
step_r=$3
low_a=$4
hi_a=$5
step_a=$6

echo "Experiment Directory: $(pwd)"
echo "Parameters for the sweep:"
echo "Transmission constant (r) range: Start=$low_r, End=$hi_r, Step=$step_r"
echo "Recovery rate (a) range      : Start=$low_a, End=$hi_a, Step=$step_a"
echo "-----------------------------------------------------"

# Loop through the specified ranges of r and a values
for r in $(seq "$low_r" "$step_r" "$hi_r");
do
    for a in $(seq "$low_a" "$step_a" "$hi_a");
    do
        echo "Running experiment with: r = $r, a = $a"
        
        # Execute the Python script with the current r and a values
        # Ensure 'python' points to your desired Python interpreter (e.g., python3)
        python test5.py "$r" "$a"
        
        echo "Experiment r=$r, a=$a finished."
        echo # Add a blank line for better readability of output
    done
done

echo "-----------------------------------------------------"
echo "Parameter sweep complete."
echo "Results (data and plots) are saved in: $(pwd)"