name="tests_$(date +%d%b%y)"
mkdir "name"
mkdir "${name}/code"
cp *.py "${name}/code"
cd "${name}"
python code/process.py data > outut/output.txt