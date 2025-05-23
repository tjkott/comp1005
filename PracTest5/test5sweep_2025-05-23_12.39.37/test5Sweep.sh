#!/bin/bash

# Create a unique directory for the experiment
exp_dir="test5sweep_$(date "+%Y-%m-%d_%H.%M.%S")"
mkdir "$exp_dir"

# Copy scripts to experiment directory
cp test5.py "$exp_dir/"
cp test5Sweep.sh "$exp_dir/" # Copy itself for record-keeping

# Change to experiment directory, exit on failure
cd "$exp_dir" || { echo "Failed to cd into $exp_dir"; exit 1; }

# Check for correct number of command-line arguments
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

# Print setup information
echo "Experiment Directory: $(pwd)"
echo "Parameters for the sweep:"
echo "Transmission constant (r) range: Start=$low_r, End=$hi_r, Step=$step_r"
echo "Recovery rate (a) range      : Start=$low_a, End=$hi_a, Step=$step_a"
echo "-----------------------------------------------------"

# Parameter sweep: loop through r and a values
for r in $(seq "$low_r" "$step_r" "$hi_r");
do
    for a in $(seq "$low_a" "$step_a" "$hi_a");
    do
        echo "Running experiment with: r = $r, a = $a"
        
        output_csv_filename="results_r_${r}_a_${a}.csv" # Define output CSV filename for this run
        
        # Execute Python simulation and redirect its standard output (CSV data) to the CSV file
        python test5.py "$r" "$a" > "$output_csv_filename"
        
        echo "Experiment r=$r, a=$a finished. Output saved to $output_csv_filename"
        echo # Blank line for readability
    done
done

# Final messages
echo "-----------------------------------------------------"
echo "Parameter sweep complete."
echo "Results (data and plots) are saved in: $(pwd)"