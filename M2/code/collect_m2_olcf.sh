models=("ckpt_lm_simulation_data_50" "ckpt_lm_simulation_data_60" "ckpt_lm_simulation_data_70" "ckpt_lm_simulation_data_80" "ckpt_lm_simulation_data_90" "ckpt_lm_simulation_data_100" "ckpt_lm_simulation_data_110" "ckpt_lm_simulation_data_120" "ckpt_lm_simulation_data_130" "ckpt_lm_simulation_data_140" "ckpt_lm_simulation_data_150")
i=0

for direc in lm_50 lm_60 lm_70 lm_80 lm_90 lm_100 lm_110 lm_120 lm_130 lm_140 lm_150; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
