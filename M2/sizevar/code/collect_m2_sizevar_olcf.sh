models=("lm_simulation_data_100_1x" "lm_simulation_data_100_15x" "lm_simulation_data_100_2x" "lm_simulation_data_100_25x" "lm_simulation_data_100_3x" "lm_simulation_data_100_35x" "lm_simulation_data_100_4x")
i=0

for direc in lm_100_1x lm_100_15x lm_100_2x lm_100_25x lm_100_3x lm_100_35x lm_100_4x; do
    echo ${models[$i]} "="
    echo "["
    python3.6 aggregate.py $direc
    echo "]"
    i=$((i+1))
done
