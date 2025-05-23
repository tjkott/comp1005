#!/bin/bash # instructs system use bash for run this.
exp_dir="test5sweep_$(date "+%Y-%m-%d_%H.%M.%S")" # Create a unique directory for the experiment
mkdir "$exp_dir" # Create the actual directory, using name from previous line. 
# Copy scripts to experiment directory 
cp test5.py "$exp_dir/" # Copy the python script. 
cp test5Sweep.sh "$exp_dir/" # Copy this bash script as well. 
cd "$exp_dir" || { echo "Failed to cd into $exp_dir"; exit 1; } # Go to new directry, or exit and inform user on failure. 
# Check for correct number of command-line arguments 
if [ "$#" -ne 6 ]; then # Check if six argument are give to script. 
    echo "Usage: $0 low_r hi_r step_r low_a hi_a step_a" # Tell user how use script right way.
    echo "Example: $0 0.001 0.003 0.001 0.1 0.5 0.2" # Give one example for them to follow easy.
    exit 1 # Stop script now, problem with args was found.
fi 
# Assign command-line arguments to variables 
low_r=$1 # 1st arg = r_low.
hi_r=$2 # 2nd arg = r_hi.
step_r=$3 # 3rd arg = r_step.
low_a=$4 # 4th arg = a_low.
hi_a=$5 # 5th arg = a_hi.
step_a=$6 # 6th arg = a_step.
echo "Parameters for the sweep:" # A title print for parameters list.
echo "Transmission constant (r) range: Start=$low_r, End=$hi_r, Step=$step_r" # Show the r range for current sweep.
echo "Recovery rate (a) range      : Start=$low_a, End=$hi_a, Step=$step_a" # Show the a range for current sweep.
echo "------------------------------------------------------" # Line for visual calirty
# Parameter sweep
for r in $(seq "$low_r" "$step_r" "$hi_r"); # Start loop for r. 
do
    for a in $(seq "$low_a" "$step_a" "$hi_a"); # Start inner loop for a, from low number to hi by step size.
    do # Do all the things in loop for each a value.
        echo "Running experiment with: r = $r, a = $a" # Tell what r and a combination we use for this run.
        output_csv_filename="results_r_${r}_a_${a}.csv" # Make name for the csv file for save results for this r, a.
        # Execute Python simulation and redirect its standard output (CSV data) to the CSV file # This comment explains what next python command does.
        python test5.py "$r" "$a" > "$output_csv_filename" # Run python code, put all its printings to the csv file.
        echo "Experiment r=$r, a=$a finished. Output saved to $output_csv_filename" # Say experiment done, and where result file is.
        echo # Put a empty line, for easy read the output.
    done # Finish a loop for 'a' values.
done # Finish r loop for 'r' values.
echo "-----------------------------------------------------" # Another line for look nice, a separator.
echo "Parameter sweep complete." # Tell all the experiments are done now.
echo "Results (data and plots) are saved in: $(pwd)" # Show where all files (CSVs, plots) got saved for user.