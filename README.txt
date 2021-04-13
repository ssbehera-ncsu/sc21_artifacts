Introduction:
=============
In this section, we describe how we run all the relevant experiments on our simulation framework.

Download:
=========
Follow the below steps to download the simulation framework.

1. Download the pre-built simulation models using git from the location https://github.ncsu.edu/ssbehera/artifacts.git.

2. Our simulations are run using python3.6 or above version. For that, we need to install the following python dependency
packages: simpy, pickle, pandas, numpy, matplotlib, xml, scipy, and openopt.

3. As there are five simulation models, we have five directories in the repository, namely B, M1, M2, P1, and P2.
Further, each directory contains another directory, namely accuracy (and sizevar). That means each directory, created for a
specfic model, further contains another model in the accuracy (and sizevar) directory for a specific experiment.

4. The datagen directory contains all the scripts that are needed to run to generate the plots in our paper. The default data
in these scripts are the exact data presented in our paper.

Experiments:
============
This section describes how to run the experiments to generate the data for the plots in our paper.

1. Base Model Simulation: For each model B, M1, M2, P1, and P2, run the script run_olcf.sh under the directory <modelname>/code/.
This will run the simulations for the OLCF's titan failure distribution. This experiment will take few hours or more depending on
the underlying system's performance.
    
2. Sys 8 Simulation: For each model B, M1, M2, P1, and P2, edit the xml file <modelname>/code/sim_conf.xml. Change the "failure distribution"
line to <distr name="weibull" shape="0.711" scale="67.375" location="0.0"/> and run run_sys_8.sh to run Sys 8 simulation.
    
3. Sys 18 Simulation: Change the "failure distribution" line to <distr name="weibull" shape="0.8170" scale="6.6293" location="0.0"/> as above,
and run run_sys_18.sh to run Sys 18 simulation.
    
4. The above experiments will generate the data required to analyze lead time variability impact on models P1, P2, M1, and M2. They will
also generate the data required to analyze all the models' performance.
    
5. Accuracy Simulation: For each model B, M1, M2, P1, and P2, run the script run.sh under the directory <modelname>/accuracy/code/. This will
generate the data for the experiments to analyze the impact of prediction accuracy on the models.

6. LM size variability: For model M2, run the script run.sh under the directory <M2/sizevar/code/>. This will generate the data for the
experiments to analyze the impact of LM transfer size requirement as factor of checkpoint size.
    
Data Collection:
================

Each of the codebases above contains aggregate.py script which is used to collect the data for analysis. This script takes the directory's name
as input which represents a particular model's run for a specific experiment. The output of this script, in the end, will contain six lists that
describe various parameters such as checkpoint overhead, recomputation overhead, and others for that experiment. We only need to collect these
six lists at the end for plot generation.

Plot Generation:
================

1. datagen/overhead_2_all.py: This script will generate the plot for analyzing the performance comparison of all the models B, P1, P2, M1, and M2.
To generate this plot, collect the data from the relevant directories as described in the previous section and replace them in the file
datagen/overhead_2_all.py as per the following mapping:

    base_simulation_data[] -> B/code/base
    ckpt_simulation_data[] -> M1/code/ckpt_100
    ckpt_lm_simulation_data[] -> M2/code/lm_100
    pckpt_simulation_data[] -> P1/code/pckpt_100
    pckpt_lm_simulation_data[] -> P2/code/lmpckpt_100
    
    For other scripts in datagen directory refer to the mappings.txt file in the repository.
