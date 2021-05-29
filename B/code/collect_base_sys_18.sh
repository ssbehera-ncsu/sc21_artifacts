models=("base_simulation_data")
i=0

for direc in base_sys_18; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
