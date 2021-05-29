models=("ckpt_lm_simulation_data_50" "ckpt_lm_simulation_data_60" "ckpt_lm_simulation_data_70" "ckpt_lm_simulation_data_80" "ckpt_lm_simulation_data_90" "ckpt_lm_simulation_data_100" "ckpt_lm_simulation_data_110" "ckpt_lm_simulation_data_120" "ckpt_lm_simulation_data_130" "ckpt_lm_simulation_data_140" "ckpt_lm_simulation_data_150")
i=0

for direc in lmpckpt_50 lmpckpt_60 lmpckpt_70 lmpckpt_80 lmpckpt_90 lmpckpt_100 lmpckpt_110 lmpckpt_120 lmpckpt_130 lmpckpt_140 lmpckpt_150; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
