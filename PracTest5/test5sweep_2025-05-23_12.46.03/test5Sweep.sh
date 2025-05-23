#!/bin/bash # Shebang, tells system use bash for run this.

# Create a unique directory for the experiment # This comment here, it explains the purpose for next lines.
exp_dir="test5sweep_$(date "+%Y-%m-%d_%H.%M.%S")" # Makes name for new directry, use date an time.
mkdir "$exp_dir" # Create the actual directry, using name from up.

# Copy scripts to experiment directory # This a comment, it is section title for copy file operations.
cp test5.py "$exp_dir/" # Copy the python script, put in new folder.
cp test5Sweep.sh "$exp_dir/" # Copy this current script too, for the record things.

# Change to experiment directory, exit on failure # This comment means next line for changin directory.
cd "$exp_dir" || { echo "Failed to cd into $exp_dir"; exit 1; } # Go to new directry, or stop if no can do it.

# Check for correct number of command-line arguments # This here comment explain next part check arguments given.
if [ "$#" -ne 6 ]; then # Check if six argument are give to script, no more no less.
    echo "Usage: $0 low_r hi_r step_r low_a hi_a step_a" # Tell user how use script right way.
    echo "Example: $0 0.001 0.003 0.001 0.1 0.5 0.2" # Give one example for them to follow easy.
    exit 1 # Stop script now, problem with args was found.
fi # End the if check for arguments given.

# Assign command-line arguments to variables # This comment tell that next lines store the arguments.
low_r=$1 # First arg from command line it is r_low.
hi_r=$2 # Second arg from command line it is r_hi.
step_r=$3 # Third arg from command line it is r_step.
low_a=$4 # Fourth arg from command line it is a_low.
hi_a=$5 # Fifth arg from command line it is a_hi.
step_a=$6 # Sixth arg from command line it is a_step.

# Print setup information # This comment indicate some information printings coming.
echo "Experiment Directory: $(pwd)" # Show what directry we are in currently.
echo "Parameters for the sweep:" # A title print for parameters list.
echo "Transmission constant (r) range: Start=$low_r, End=$hi_r, Step=$step_r" # Show the r values range for the sweep.
echo "Recovery rate (a) range      : Start=$low_a, End=$hi_a, Step=$step_a" # Show the a values range for the sweep.
echo "-----------------------------------------------------" # Just a line for make it look nice and seprate things.

# Parameter sweep: loop through r and a values # This comment is title for main loop sections below.
for r in $(seq "$low_r" "$step_r" "$hi_r"); # Start loop for r, from low number to hi number by the step size.
do # Do all the things in loop for each r value.
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

# Final messages # This comment indicates the final messages of script.
echo "-----------------------------------------------------" # Another line for look nice, a separator.
echo "Parameter sweep complete." # Tell all the experiments are done now.
echo "Results (data and plots) are saved in: $(pwd)" # Show where all files (CSVs, plots) got saved for user.