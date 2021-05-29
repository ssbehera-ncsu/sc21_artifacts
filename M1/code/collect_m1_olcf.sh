models=("ckpt_simulation_data_50" "ckpt_simulation_data_60" "ckpt_simulation_data_70" "ckpt_simulation_data_80" "ckpt_simulation_data_90" "ckpt_simulation_data_100" "ckpt_simulation_data_110" "ckpt_simulation_data_120" "ckpt_simulation_data_130" "ckpt_simulation_data_140" "ckpt_simulation_data_150")
i=0

for direc in ckpt_50 ckpt_60 ckpt_70 ckpt_80 ckpt_90 ckpt_100 ckpt_110 ckpt_120 ckpt_130 ckpt_140 ckpt_150; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
