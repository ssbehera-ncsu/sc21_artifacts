import statistics
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt
import glob
import seaborn as sns
import pickle
from dateutil import parser
import pandas as pd
from scipy.stats import lognorm
from scipy.stats import alpha
from scipy.stats import fisk
from scipy.stats import genextreme
from scipy.stats import gengamma
from scipy.stats import loglaplace
from scipy.stats import burr
from scipy.stats import maxwell
from scipy.stats import mielke
from scipy.stats import moyal
from scipy.stats import nakagami
from scipy.stats import norminvgauss
from scipy.stats import powerlognorm
from scipy.stats import wald
from scipy.stats import cauchy
from mpl_toolkits import mplot3d

#applications = ['CHIMERA(360)', 'S3D(240)', 'GTC(120)', 'POP(480)', 'VULCAN(720)', 'GYRO(120)']
applications = ['CHIMERA', 'S3D', 'GTC', 'POP', 'VULCAN', 'GYRO']
#col_list = ['computation time', 'checkpoint time', 'waste time', 'restart time', 'wallclock time', 'efficiency',
#             'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'pct. of checkpoints to BB', 'daily write workloads to Burst Buffers']

col_list = ['Checkpoint time', 'Re-compuation waste time', 'Reovery time']

     #['Efficiency', 'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'Daily writes to BurstBuffer']

base_simulation_data = [[4.527178478279721,6.842923937062951,0.054423218096535254,96.932467119464,14.943,474.611,0.7916768738272747,4916.525170713457],
[1.4975163916409917,1.951113630203402,0.008665693369352813,98.58330298531513,6.854,452.24,0.5542342676376343,1650.2646338746974],
[0.550393965108764,0.657356825058439,0.0011521152115071456,99.49999583900035,2.25,410.409,0.6107410494857678,203.93035176182906],
[0.027835411941428037,0.03288952963585561,5.912297579292569e-06,99.94950660128842,0.295,530.298,0.23625576048509925,5.170502329896779],
[0.0719710821508895,0.1037881537789315,1.1672278328318825e-05,99.96340966361255,1.12,2636.799,0.19203846190529755,3.3454176018585615],
[0.017071010949399813,0.0341533515082716,6.032433778088154e-07,99.99288680527921,0.921,9951.371,0.07826347724542444,0.26882886329734074]]

ckpt_simulation_data = [[4.527273865417369,6.824722745863304,0.05507150377017264,96.93663815326468,15.121,474.621,0.7917723123601038,4913.9370938221455],
[1.498168723874222,1.947662525183744,0.008931201920208477,98.58430967046804,7.064,452.437,0.5539207989474871,1650.5279777662274],
[0.5521320131992778,0.013847435764089883,0.0011567236723532732,99.76456232841132,2.259,411.705,0.6103528964377267,205.1000782264922],
[0.027755941881798547,0.0016718494489555674,5.711880712209731e-06,99.97550396199377,0.285,528.784,0.23708917855468056,5.157429654626944],
[0.07197209206104459,0.0034187471803422535,1.0734327391266535e-05,99.98429809592285,1.03,2636.836,0.19210839442420716,3.346121326605405],
[0.017079552140427983,0.0016792423478466413,5.894886434714905e-07,99.99739479233861,0.9,9956.35,0.07820911739413997,0.26897626071530306]]

ckpt_lm_simulation_data = [[3.1749799537987013,5.363542266925214,0.030673381704411688,97.68326833403553,8.422,332.852,1.130409873146954,3469.450813466389],
[1.0512085588571594,1.5118870085217244,0.00480064746475552,98.94505156261631,3.797,317.458,0.7905106462471085,1161.608345152305],
[0.3874157472876001,0.012756414172909208,0.0006569616961613416,99.83358888326632,1.283,288.882,0.8711258401343078,143.93010823201027],
[0.019643329553258627,0.0009593436214786954,2.9862113197151317e-06,99.98285768646792,0.149,374.229,0.33532883940580765,3.6486647048607455],
[0.05055443647600497,0.0023255875730594264,6.732403393068437e-06,99.98898727457703,0.646,1852.159,0.27289931754498814,2.350247239378569],
[0.012065070012782408,0.0010774851637386294,3.2945865296281353e-07,99.99817482479904,0.503,7033.209,0.1098745959291134,0.19000154983277825]]


ckpt_time_base = []
ckpt_time_ckpt = []
ckpt_time_lm = []
recomputation_time_base = []
recomputation_time_ckpt = []
recomputation_time_lm = []
recovery_time_base = []
recovery_time_ckpt = []
recovery_time_lm = []

index = 0
for app in applications:
    ckpt_time_base.append(base_simulation_data[index][0])
    ckpt_time_lm.append(ckpt_lm_simulation_data[index][0])
    ckpt_time_ckpt.append(ckpt_simulation_data[index][0])
    recomputation_time_base.append(base_simulation_data[index][1])
    recomputation_time_lm.append((ckpt_lm_simulation_data[index][1]))
    recomputation_time_ckpt.append(ckpt_simulation_data[index][1])
    recovery_time_base.append(base_simulation_data[index][2])
    recovery_time_lm.append(ckpt_lm_simulation_data[index][2])
    recovery_time_ckpt.append(ckpt_simulation_data[index][2])
    index += 1

base_simulation_df = pd.DataFrame()

base_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_base)
base_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_base)
base_simulation_df['Recovery Time'] = pd.Series(recovery_time_base)
base_simulation_df['Applications'] = pd.Series(applications)

base_simulation_df.set_index('Applications', inplace=True)

lm_simulation_df = pd.DataFrame()
lm_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm)
lm_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm)
lm_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm)
lm_simulation_df['Applications'] = pd.Series(applications)

lm_simulation_df.set_index('Applications', inplace=True)

ckpt_simulation_df = pd.DataFrame()
ckpt_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_ckpt)
ckpt_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_ckpt)
ckpt_simulation_df['Recovery Time'] = pd.Series(recovery_time_ckpt)
ckpt_simulation_df['Applications'] = pd.Series(applications)

ckpt_simulation_df.set_index('Applications', inplace=True)

def plot_clustered_stacked(dfall, labels=None, title="multiple stacked bar plot",  H="//", **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot.
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns)
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)

    for df in dfall : # for each data frame
        axe = df.plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      width=0.75,
                      figsize=(6.4, 5.8),
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            app_index = 0
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                if i == 3:
                    H = '//'
                elif i == 6:
                    H = '\\'
                rect.set_hatch(H * int(i / n_col)) #edited part
                rect.set_width(1 / float(n_df + 1))
                print(i, j)
                if (i == 3) and (j == 2):
                    overhead1 = 0.0
                    overhead2 = 0.0
                    for k in range(0, n_col):
                        overhead1 += dfall[0].iloc[app_index][k]
                    for k in range(0, n_col):
                        overhead2 += dfall[1].iloc[app_index][k]
                    diff = (overhead2 - overhead1) / overhead1 * 100
                    diff = round(diff, 2)
                    axe.text(rect.get_x(), rect.get_y() + rect.get_width(), str(diff) + '%', fontsize=10, fontname='Times New Roman', rotation=70)

                if (i == 6) and (j == 2):
                    overhead1 = 0.0
                    overhead2 = 0.0
                    for k in range(0, n_col):
                        overhead1 += dfall[0].iloc[app_index][k]
                    for k in range(0, n_col):
                        overhead2 += dfall[2].iloc[app_index][k]
                    diff = (overhead2 - overhead1) / overhead1 * 100
                    diff = round(diff, 2)
                    axe.text(rect.get_x(), rect.get_y() + rect.get_width(), str(diff) + '%', fontsize=10, fontname='Times New Roman', rotation=70)
                app_index += 1

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation = 0, fontsize=10, fontname='Times New Roman')
    axe.set_yticklabels([0, 3, 6, 9, 12, 15, 18, 20], fontsize=10, fontname ='Times New Roman')

    # Add invisible data to add another legend
    n=[]
    for i in range(n_df):
        if i == 2:
            H = '\\'
        else:
            H = '//'
        n.append(axe.bar(0, 0, color="gray", hatch= H * i))

    legend_properties = {'size': '10', 'family':'Times New Roman'}
    l1 = axe.legend(h[:n_col], l[:n_col], loc=[0.6338, 0.68], prop=legend_properties)
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[0.21, 0.84], prop=legend_properties)
    axe.add_artist(l1)
    return axe

#print(base_simulation_df.head())

#print(lm_simulation_df.head())

plt.margins(y = 0.15)

plot_clustered_stacked([base_simulation_df, ckpt_simulation_df, lm_simulation_df],
                       ["Base Model", "Failure Prediction Integrated Model", "Failure Prediction and Live Migration Integrated Model"])

plt.xlabel('Scientific Applications', fontsize = 10, fontname = 'Times New Roman')
plt.ylabel('Overhead time (hrs)', fontsize=10, fontname = 'Times New Roman')
plt.yscale('log')
plt.savefig('overhead.png',dpi=600)
