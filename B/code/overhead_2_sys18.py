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

base_simulation_data = [[4.99733214099707,6.754021235687005,0.5843951746032235,96.70983519252975,17.977,523.9,0.8983713210690776,5390.850315533829],
[1.633214741476168,1.917358085039512,0.06092992499995422,98.52351390605067,8.097,493.22,0.6305189384115164,1795.3055696435201],
[0.6003011577325775,0.6480718590393231,0.0027438730158567174,99.48280552979071,2.701,447.623,0.6948252153438814,222.25544207798498],
[0.0299920214987189,0.03371204820156261,0.0035218253968248613,99.94409888779884,0.355,571.384,0.26623336653842244,5.57125916826787],
[0.08115438609193802,0.09674716244180562,0.007571869488529908,99.96138947790378,1.321,2973.247,0.21216004851990464,3.7722248015654],
[0.020163591217111723,0.027146718607479928,0.0002273575268764798,99.99339859617392,1.019,11754.159,0.08106634071068088,0.3175354232923441]]

ckpt_simulation_data = [
[6.052620120757844,4.591010605530548,0.788935111111175,96.92658775176935,24.269,634.375,0.5698006798993283,6507.631481693286],
[2.0310492115273684,0.015504607763595059,0.08319639999993787,99.12115686672867,11.056,601.187,0.4043448419967271,2193.7095321133716],
[0.7357733773350028,0.0070078705616375145,0.0035972063491845167,99.69026583675507,3.541,545.16,0.44557050444404395,271.4805179803975],
[0.03626604906965609,0.0006484429747657135,0.0046527777777771355,99.96539885495287,0.469,689.951,0.17553948749237355,6.7304743852359765],
[0.09917347679856242,0.002390767300041369,0.009893298059956581,99.97678909902956,1.726,3624.712,0.13423400603669794,4.599827898636989],
[0.02473910093795811,0.0019141727391147267,0.0003085725806379218,99.99625559452889,1.383,14374.165,0.051247710291950174,0.38833388173095384]
]


ckpt_lm_simulation_data = [
[4.195551876903724,5.875615119241656,0.420360126984148,97.17626203099806,12.931,439.815,0.7875299163758609,4764.958813737627],
[1.4259247238603765,0.01560240651294847,0.046022899999966026,99.38479563435425,6.116,430.568,0.5590973748430248,1582.6694960283855],
[0.5319583791692741,0.0054171888458812885,0.0020530793650670506,99.77604039597698,2.021,394.66,0.6162032845273195,196.54055645682826],
[0.026299705729069322,0.00037050323236596924,0.002658730158729778,99.97559046526979,0.268,500.494,0.24235645235521233,4.880588775376693],
[0.07138871992715516,0.0014107925527801245,0.0058465608465563005,99.98362172859338,1.02,2610.292,0.1865310641763422,3.3122366980971],
[0.017872182460286386,0.0011069915192584775,0.0001791639784903256,99.99733934515925,0.803,10390.826,0.0707811801213128,0.28071155647110985]
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
                       ["Base C/R Model", "C/R Model P1", "C/R Model P2"])

plt.xlabel('Scientific Applications', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.ylabel('Overhead (percentage)', fontsize=15, fontname = 'Times New Roman', fontweight='normal')
plt.yticks(fontsize=15, fontname='Times New Roman', fontweight='normal')
plt.tight_layout()
plt.savefig('overhead_2_sys_18.png',dpi=400)
