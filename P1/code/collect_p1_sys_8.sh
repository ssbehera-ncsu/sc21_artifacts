models=("pckpt_simulation_data")
i=0

for direc in pckpt_100_sys_8; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
