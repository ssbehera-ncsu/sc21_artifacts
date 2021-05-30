Introduction
============
In this section, we describe how we run all the relevant experiments on our simulation framework.

Download
========
Follow the below steps to download the simulation framework.

 a. Download the pre-built simulation models using git from the location https://github.com/ssbehera-ncsu/sc21artifacts.git.

 b. Our simulations are run using python3.6 or above version. For that, we need to install the following python dependency
    packages: simpy[4.0.1], pickle, pandas[1.1.5], numpy[1.20.2], matplotlib[3.1.0], scipy[1.1.0], openopt[0.5629],
    and seaborn[0.11.1].

 c. As there are five simulation models, we have five directories in the repository, namely B, M1, M2, P1, and P2. Further,
    each directory contains another directory, namely accuracy. That means each directory, created for a specfic
    model, further contains another model in the accuracy directory for a specific experiment.

 d. The datagen directory contains all the scripts that are needed to run to generate the plots in our paper. The default
    data embedded in these scripts are the exact data presented in our paper.

Experiments
===========
This section describes how to run the experiments and generate the data for the plots in our paper.

 Summit Simulation: For each model B, M1, M2, P1, and P2, run the script run_olcf.sh under the directory <modelname>/code/.
 This will run the simulations for the OLCF's titan failure distribution. This experiment will take few minutes or more 
 depending on the underlying system's performance.
    
 Sys 8 Simulation: For each model B, M1, M2, P1, and P2, edit the xml file <modelname>/code/sim_conf.xml. Change the
 <distr name="weibull" *> line to <distr name="weibull" shape="0.711" scale="67.375" location="0.0"/> and run
 run_sys_8.sh to run Sys 8 simulation.
    
 Sys 18 Simulation: For each model B, M1, M2, P1, and P2, edit the xml file <modelname>/code/sim_conf.xml. Change the
 <distr name="weibull" *> line to <distr name="weibull" shape="0.8170" scale="6.6293" location="0.0"/> as above and
 run run_sys_18.sh to run Sys 18 simulation.
    
 The above experiments will generate the data required to analyze lead time variability impact on models P1, P2, M1, and
 M2. They will also generate the data required to analyze all the models' performance. With the data generated,
 Figures 4, 5(a), 5(b), and 6 can be plotted.
    
 Accuracy Simulation: For each model B, M1, M2, P1, and P2, run the script run.sh under the directory <modelname>/accuracy/code/.
 This will generate the data to analyze the impact of prediction accuracy on the models.
    
 p-ckpt vs LM: For model M2, run the script run.sh under the directory M2/sizevar/code/. This will generate the data for the
 experiments for figure 5(c).

Data Collection
===============

Each of the model's directories codebases also contain collect_<model_name>_<system>.sh script which is used to collect the
data for analysis. Running this shell script will generate output for a particular model and system. The output of this script
contains six lists that describe various parameters such as checkpoint overhead, recomputation overhead, recovery overhead,
and others for that experiment.

Plot Generation
===============

datagen/overhead_2_all.py: This script will generate the plot for analyzing the performance comparison of all the models B,
P1, P2, M1, and M2. To generate this plot, collect the data from the relevant directories as described in the previous section
and replace them in the file datagen/overhead_2_all.py as per the following mapping:

 base_simulation_data[] -> B/code/. Run collect_base_olcf.sh.

 ckpt_simulation_data[] -> M1/code/. Run collect_m1_olcf.sh. collect ckpt_simulation_data_100's block and replace
 ckpt_simulation_data's block with that in overhead_2_all.py.

 ckpt_lm_simulation_data[] -> M2/code/. Run collect_m2_olcf.sh. collect ckpt_lm_simulation_data_100's block and replace
 ckpt_lm_simulation_data's block with that in overhead_2_all.py.

 pckpt_simulation_data[] -> P1/code/. Run collect_p1_olcf.sh. collect ckpt_simulation_data_100's block and replace
 pckpt_simulation_data's block with that in overhead_2_all.py.

 pckpt_lm_simulation_data[] -> P2/code/. Run collect_p2_olcf.sh. collect ckpt_lm_simulation_data_100's block and replace
 pckpt_lm_simulation_data's block with that in overhead_2_all.py.
    
Run overhead_2_all.py to generate figure 5(a).
    
For other scripts in datagen directory refer to the mappings.txt file in the repository.
