models=("ckpt_simulation_data_50" "ckpt_simulation_data_60" "ckpt_simulation_data_70" "ckpt_simulation_data_80" "ckpt_simulation_data_90" "ckpt_simulation_data_100" "ckpt_simulation_data_110" "ckpt_simulation_data_120" "ckpt_simulation_data_130" "ckpt_simulation_data_140" "ckpt_simulation_data_150")
i=0

for direc in pckpt_50 pckpt_60 pckpt_70 pckpt_80 pckpt_90 pckpt_100 pckpt_110 pckpt_120 pckpt_130 pckpt_140 pckpt_150; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
