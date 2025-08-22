input_dir="input_data"
output_dir="output_results"
mkdir -p "output_dir"
files = $(ls -v "${input_dir}")
num_of_files