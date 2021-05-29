models=("pckpt_ckpt_lm_simulation_data_18_82_0" "pckpt_ckpt_lm_simulation_data_18_779_41" "pckpt_ckpt_lm_simulation_data_18_738_82" "pckpt_ckpt_lm_simulation_data_18_697_123" "pckpt_ckpt_lm_simulation_data_18_656_164" "pckpt_ckpt_lm_simulation_data_18_615_205" "pckpt_ckpt_lm_simulation_data_18_574_246" "pckpt_ckpt_lm_simulation_data_18_533_287" "pckpt_ckpt_lm_simulation_data_18_492_328")
i=0

for direc in lmpckpt_18_820_0 lmpckpt_18_779_041 lmpckpt_18_738_082 lmpckpt_18_697_123 lmpckpt_18_656_164 lmpckpt_18_615_205 lmpckpt_18_574_246 lmpckpt_18_533_287 lmpckpt_18_492_328; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
