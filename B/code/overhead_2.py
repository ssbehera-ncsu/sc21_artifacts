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
applications = ['CHIMERA', 'XGC', 'S3D', 'GYRO', 'POP', 'VULCAN']
#col_list = ['computation time', 'checkpoint time', 'waste time', 'restart time', 'wallclock time', 'efficiency',
#             'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'pct. of checkpoints to BB', 'daily write workloads to Burst Buffers']

col_list = ['Checkpoint time', 'Re-compuation waste time', 'Reovery time']

     #['Efficiency', 'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'Daily writes to BurstBuffer']

base_simulation_data = [[5.906209404579086,9.169600679330603,0.8012231111111773,95.78483165170321,24.647,619.183,0.5974565681487142,6348.5351930920315],
[1.9431917601784183,2.514602214460817,0.0844681249999373,98.14595607852272,11.225,586.831,0.42001124834491804,2133.2166093919986],
[0.7145523390407579,0.8592947044572643,0.003825777777755569,99.34803741205242,3.766,532.816,0.46285465266481707,264.43355455629785],
[0.035790711344789845,0.04227303928034483,0.004781746031745381,99.93110101908339,0.482,681.856,0.1808199748691967,6.648939751118924],
[0.09437956876001852,0.13500992141994228,0.01121737213402941,99.94991536763791,1.957,3457.777,0.14433690731534438,4.386674577592602],
[0.02253823625535016,0.04025842033704997,0.00031727419354092356,99.99123569748792,1.422,13138.434,0.058464721413464656,0.35492730442781606]]

ckpt_simulation_data = [
[5.865373628893035,5.229631830981899,0.8218981587302245,96.80116729210977,25.283,614.744,0.5987464528100058,6299.416690112582],
[1.9865257394693299,0.026777558228312192,0.085784999999937,99.13376677629999,11.4,587.707,0.42139522684413344,2143.9714398927113],
[0.7201272591518323,0.01082913459195932,0.003825777777755111,99.69508938042479,3.766,533.295,0.4643487711077172,265.56281400911524],
[0.035682317488653054,0.0006879833205796832,0.004890873015872291,99.96565463548143,0.493,678.779,0.18194208803718948,6.621316008145397],
[0.0945798912593951,0.0025985875708782968,0.010776014109338284,99.97751886485163,1.88,3455.641,0.1444216183642792,4.385217890898773],
[0.022658809948702414,0.0020669867257988245,0.00033356182794891566,99.99651984814072,1.495,13157.726,0.05831264393704112,0.35546630083306163]
]

ckpt_lm_simulation_data = [
[3.979748335101044,6.707896584909568,0.44266057142859383,97.01319752356395,13.617,417.168,0.8414736187933837,4534.817538658083],
[1.3709980361873142,0.02396027516290971,0.048904974999965094,99.4028184514417,6.499,413.937,0.5917938172901792,1522.7581954389952],
[0.5123668552550711,0.006048173976589149,0.00218107936506721,99.78385220783696,2.147,379.929,0.652213686550081,189.2235343551978],
[0.02555357633111458,0.00037506245106349776,0.002698412698412324,99.97617632164108,0.272,486.265,0.25431746491299284,4.741418773477559],
[0.06651452130320518,0.0016686070837992055,0.006173280423275427,99.98451572617167,1.077,2431.419,0.2055916448910843,3.0851044796505915],
[0.015983960027449725,0.0011481030865278395,0.0001854112903181423,99.9975950300583,0.831,9288.809,0.08232536293898803,0.25093634257730507]
]


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
    base_total_time = base_simulation_data[index][0] + base_simulation_data[index][1] + base_simulation_data[index][2]
    ckpt_time_base.append(base_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_lm.append(ckpt_lm_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_ckpt.append(ckpt_simulation_data[index][0] / base_total_time * 100)
    recomputation_time_base.append(base_simulation_data[index][1] / base_total_time * 100)
    recomputation_time_lm.append((ckpt_lm_simulation_data[index][1]) / base_total_time * 100)
    recomputation_time_ckpt.append(ckpt_simulation_data[index][1] / base_total_time * 100)
    recovery_time_base.append(base_simulation_data[index][2] / base_total_time * 100)
    recovery_time_lm.append(ckpt_lm_simulation_data[index][2] / base_total_time * 100)
    recovery_time_ckpt.append(ckpt_simulation_data[index][2] / base_total_time * 100)
    index += 1

index = 0
for app in applications:
    print(applications[index])
    tmp1 = (base_simulation_data[index][0] - ckpt_simulation_data[index][0])/ base_simulation_data[index][0]
    print('ckpt:base to ckpt', tmp1)
    tmp2 = (base_simulation_data[index][0] - ckpt_lm_simulation_data[index][0])/ base_simulation_data[index][0]
    print('ckpt:base to lm', tmp2)
    tmp3 = (tmp2 - tmp1)
    print('ckpt:ckpt to lm', tmp3)

    tmp4 = (base_simulation_data[index][1] - ckpt_simulation_data[index][1]) / base_simulation_data[index][1]
    print('recomputation:base to ckpt', tmp4)
    tmp5 = (base_simulation_data[index][1] - ckpt_lm_simulation_data[index][1]) / base_simulation_data[index][1]
    print('recomputation:base to lm', tmp5)
    tmp6 = (tmp5 - tmp4)
    print('recomputation :ckpt to lm', tmp6)

    print('total ckpt: ', ckpt_time_base[index] + recovery_time_base[index] + recomputation_time_base[index]
          - ckpt_time_ckpt[index] - recovery_time_ckpt[index] - recomputation_time_ckpt[index])

    print('total lm: ', ckpt_time_base[index] + recovery_time_base[index] + recomputation_time_base[index]
          - ckpt_time_lm[index] - recovery_time_lm[index] - recomputation_time_lm[index])


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
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            app_index = 0
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col) - 0.1)
                if i == 3:
                    H = '//'
                elif i == 6:
                    H = '\\'
                rect.set_hatch(H * int(i / n_col)) #edited part
                rect.set_width(1 / float(n_df + 1))
                overhead = 0
                base_total_time = base_simulation_data[app_index][0] + base_simulation_data[app_index][1] + \
                                  base_simulation_data[app_index][2]
                if j == 2:
                    if i == 0:
                        for k in range(0, n_col):
                            overhead += dfall[0].iloc[app_index][k] * base_total_time / 100
                    elif i == 3:

                        for k in range(0, n_col):
                            overhead += dfall[1].iloc[app_index][k] * base_total_time / 100
                    elif i == 6:
                        for k in range(0, n_col):
                            overhead += dfall[2].iloc[app_index][k] * base_total_time / 100
                    overhead = round(overhead, 2)
                    print(overhead)
                    axe.text(rect.get_x(), rect.get_y() + rect.get_width(), str(overhead) + ' hrs', fontsize=15,
                             fontname='Times New Roman', rotation=70, fontweight='normal')
                app_index += 1
                '''
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
                '''

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation = 0, fontsize=15, fontname='Times New Roman', fontweight='normal')
    axe.set_ylim(0,170)
    axe.set_yticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    #axe.set_yticks(fontsize=10, fontname ='Times New Roman')

    # Add invisible data to add another legend
    n=[]
    for i in range(n_df):
        if i == 2:
            H = '\\'
        else:
            H = '//'
        n.append(axe.bar(0, 0, color="gray", hatch= H * i))

    legend_properties = {'size': '15', 'family':'Times New Roman', 'weight':'normal'}
    l1 = axe.legend(h[:n_col], l[:n_col], prop=legend_properties, loc=1, borderaxespad=0, borderpad = 0.2)
    if labels is not None:
        l2 = plt.legend(n, labels, prop=legend_properties, loc=2, borderaxespad=0, borderpad = 0.2)
    axe.add_artist(l1)
    return axe

#print(base_simulation_df.head())

#print(lm_simulation_df.head())



plot_clustered_stacked([base_simulation_df, ckpt_simulation_df, lm_simulation_df],
                       ["Model B", "Model P1", "Model P2"])

plt.xlabel('Scientific Applications', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.ylabel('Overhead (percentage)', fontsize=15, fontname = 'Times New Roman', fontweight='normal')
plt.yticks(fontsize=15, fontname='Times New Roman', fontweight='normal')
plt.tight_layout()
plt.savefig('overhead_2.png',dpi=400)
