models=("old_ckpt_simulation_data_18_82_0" "old_ckpt_simulation_data_18_779_41" "old_ckpt_simulation_data_18_738_82" "old_ckpt_simulation_data_18_697_123" "old_ckpt_simulation_data_18_656_164" "old_ckpt_simulation_data_18_615_205" "old_ckpt_simulation_data_18_574_246" "old_ckpt_simulation_data_18_533_287" "old_ckpt_simulation_data_18_492_328")
i=0

for direc in ckpt_18_820_0 ckpt_18_779_041 ckpt_18_738_082 ckpt_18_697_123 ckpt_18_656_164 ckpt_18_615_205 ckpt_18_574_246 ckpt_18_533_287 ckpt_18_492_328; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
