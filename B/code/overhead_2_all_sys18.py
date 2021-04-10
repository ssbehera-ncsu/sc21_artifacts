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

base_simulation_data = [
[12.02920345819501,19.839371870616937,0.3279213933662728,91.8206561240562,22.822,319.652,1.1362793992083455,12498.732492393718],
[3.9342402387079916,4.957715927271717,0.052823211965026144,96.41885998340092,10.59,301.154,0.8042595922277134,4245.713443343101],
[1.4471247653939328,1.7091749698957193,0.007468484273100821,98.70301854677656,3.697,273.514,0.885793715020266,531.6765681183481],
[0.07193220058122081,0.08033117437316076,3.645061179314102e-05,99.87355837596347,0.461,347.357,0.3488162416659073,13.346622440678377],
[0.19737181787104557,0.23974652128903148,7.561169423895855e-05,99.90904789337074,1.839,1832.882,0.26519339219542787,9.16880910679613],
[0.049176024740407887,0.0691641895318256,1.1604933134058415e-05,99.98356719696247,1.352,7266.202,0.1013417271079118,0.7743295090469344]
]

ckpt_simulation_data = [
[11.998984812990441,20.06224897851689,0.39434497973040267,91.76126406561487,26.165,318.997,1.1353927934056647,12451.694913047202],
[3.9328554672445497,4.764576409067613,0.06720852007565692,96.48776016269372,11.02,301.539,0.8037719549114126,4245.4787821742175],
[1.4421301918856897,0.6468762731198217,0.01959297500004378,99.13131403804098,3.54,274.659,0.8853449310586906,532.0243216440861],
[0.07197051118704575,0.01451647231071848,0.0001336430344522956,99.92799945176985,0.482,347.948,0.3484279028307678,13.36043200001265],
[0.1975254827464097,0.03755455301632352,0.00033691628742986353,99.95099838542579,1.771,1835.794,0.26485509522109885,9.179654648371555],
[0.049221206410474276,0.009494506358460865,5.353810087831116e-05,99.9918390636956,1.363,7274.044,0.10123417733158518,0.7751056538750478]
]

ckpt_lm_simulation_data = [
[8.102698823077345,14.214923196468144,0.18426360303782383,94.1484265173785,12.824,215.313,1.6911117416114845,8609.540754169026],
[2.1139842777698195,2.917636036974868,0.017592773238965773,97.9519447658697,3.527,161.819,1.501494540566258,2312.023063768083],
[0.5394509749219393,0.6641497916845265,0.0011070406766726137,99.50484328176555,0.548,101.959,2.388633472433237,199.15405176014755],
[0.025814721626607192,0.037766734394489944,5.9301429164546615e-06,99.94742610945296,0.075,124.658,0.97663551289693,4.780455000761572],
[0.06986367636181695,0.09622928784683091,1.0566723990978132e-05,99.96546089549146,0.257,648.785,0.7497482966461642,3.245401266210722],
[0.015483330597507552,0.024369504844350888,1.4076989897491288e-06,99.99446754227671,0.164,2287.802,0.3211242421231889,0.24378398960711528]
]


pckpt_simulation_data = [
[11.775480842831326,5.236278271327069,2.3519214128368056,94.90785991294968,25.015,327.754,1.1348106756008254,12398.878128684632],
[3.8960787916215764,0.764194730786057,0.26920195593596385,97.99151645015053,10.776,305.823,0.8033105894140211,4243.866877100268],
[1.4427044626964065,0.2515666638914412,0.025471892003283432,99.29015965465014,3.627,275.26,0.8849079268894818,532.1250263291848],
[0.07191692206746138,0.012595892414616611,0.00011925541220852942,99.92964568009867,0.428,347.559,0.34878703232699354,13.347608323221301],
[0.19683232396932812,0.03725460312303399,0.0003609185472605824,99.95119930077952,1.862,1828.974,0.2660015935235943,9.145104069684322],
[0.049033078106529925,0.007970357755316796,5.46978269055125e-05,99.99207666912942,1.347,7244.76,0.10168525570285439,0.7719820766581916]
]

pckpt_lm_simulation_data = [
[7.246382108655853,7.236062187419302,0.7233657633122652,95.98022967194161,11.629,196.662,1.682600957849399,8624.909645989028],
[2.0054557523711747,1.2683884966187502,0.06225162467785336,98.63770554964599,3.476,155.093,1.4971995422354643,2318.381741741329],
[0.5372060176714996,0.6952832104834503,0.0013954888404715004,99.49333866474167,0.6,101.56,2.3843067087594165,199.49659261860268],
[0.02587321893046884,0.032234951570021736,5.610058093978299e-06,99.95196275364246,0.065,124.942,0.9753608743814217,4.786044151640719],
[0.06893155741813377,0.09811977501536794,1.0606513337050317e-05,99.96526343384718,0.245,640.131,0.7614170714595094,3.2010267979110103],
[0.015274361989332241,0.020826796378323173,3.5401618797506476e-07,99.99498829026048,0.137,2256.925,0.3258636588318576,0.24046354706783601]
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

ckpt_time_pckpt = []
ckpt_time_plm = []
recomputation_time_pckpt = []
recomputation_time_plm = []
recovery_time_pckpt = []
recovery_time_plm = []

index = 0
for app in applications:
    base_total_time = base_simulation_data[index][0] + base_simulation_data[index][1] + base_simulation_data[index][2]
    ckpt_time_base.append(base_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_lm.append(ckpt_lm_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_ckpt.append(ckpt_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_plm.append(pckpt_lm_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_pckpt.append(pckpt_simulation_data[index][0] / base_total_time * 100)
    recomputation_time_base.append(base_simulation_data[index][1] / base_total_time * 100)
    recomputation_time_lm.append((ckpt_lm_simulation_data[index][1]) / base_total_time * 100)
    recomputation_time_ckpt.append(ckpt_simulation_data[index][1] / base_total_time * 100)
    recomputation_time_plm.append((pckpt_lm_simulation_data[index][1]) / base_total_time * 100)
    recomputation_time_pckpt.append(pckpt_simulation_data[index][1] / base_total_time * 100)
    recovery_time_base.append(base_simulation_data[index][2] / base_total_time * 100)
    recovery_time_lm.append(ckpt_lm_simulation_data[index][2] / base_total_time * 100)
    recovery_time_ckpt.append(ckpt_simulation_data[index][2] / base_total_time * 100)
    recovery_time_plm.append(pckpt_lm_simulation_data[index][2] / base_total_time * 100)
    recovery_time_pckpt.append(pckpt_simulation_data[index][2] / base_total_time * 100)
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

    tmp7 = (base_simulation_data[index][0] - pckpt_simulation_data[index][0]) / base_simulation_data[index][0]
    print('ckpt:base to pckpt', tmp7)
    tmp8 = (base_simulation_data[index][0] - pckpt_lm_simulation_data[index][0]) / base_simulation_data[index][0]
    print('ckpt:base to plm', tmp8)
    tmp9 = (tmp8 - tmp7)
    print('ckpt:pckpt to plm', tmp9)

    tmp10 = (base_simulation_data[index][1] - pckpt_simulation_data[index][1]) / base_simulation_data[index][1]
    print('recomputation:base to pckpt', tmp10)
    tmp11 = (base_simulation_data[index][1] - pckpt_lm_simulation_data[index][1]) / base_simulation_data[index][1]
    print('recomputation:base to plm', tmp11)
    tmp12 = (tmp11 - tmp10)
    print('recomputation :pckpt to plm', tmp12)

    print('total pckpt: ', ckpt_time_base[index] + recovery_time_base[index] + recomputation_time_base[index]
          - ckpt_time_pckpt[index] - recovery_time_pckpt[index] - recomputation_time_pckpt[index])

    print('total plm: ', ckpt_time_base[index] + recovery_time_base[index] + recomputation_time_base[index]
          - ckpt_time_plm[index] - recovery_time_plm[index] - recomputation_time_plm[index])

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


plm_simulation_df = pd.DataFrame()
plm_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_plm)
plm_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_plm)
plm_simulation_df['Recovery Time'] = pd.Series(recovery_time_plm)
plm_simulation_df['Applications'] = pd.Series(applications)

plm_simulation_df.set_index('Applications', inplace=True)

pckpt_simulation_df = pd.DataFrame()
pckpt_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_pckpt)
pckpt_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_pckpt)
pckpt_simulation_df['Recovery Time'] = pd.Series(recovery_time_pckpt)
pckpt_simulation_df['Applications'] = pd.Series(applications)

pckpt_simulation_df.set_index('Applications', inplace=True)

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
                    H = '\\\\'
                elif i == 6:
                    H = '/'
                elif i == 9:
                    H = '\\'
                elif i == 12:
                    H = '/'
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
                    elif i == 9:
                        for k in range(0, n_col):
                            overhead += dfall[3].iloc[app_index][k] * base_total_time / 100
                    elif i == 12:
                        for k in range(0, n_col):
                            overhead += dfall[4].iloc[app_index][k] * base_total_time / 100
                    overhead = round(overhead, 2)
                    print(overhead)
                    axe.text(rect.get_x(), rect.get_y() + rect.get_width() * 2, str(overhead) + ' hrs', fontsize=15,
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
        if i == 1:
            H = '\\\\'
        elif i == 2:
            H = '/'
        elif i == 3:
            H = '\\'
        elif i == 4:
            H = '/'
        n.append(axe.bar(0, 0, color="gray", hatch= H * i, width=2))

    legend_properties = {'size': '15', 'family':'Times New Roman', 'weight':'normal'}
    l1 = axe.legend(h[:n_col], l[:n_col], prop=legend_properties, loc=1, borderaxespad=0, borderpad = 0.2)
    if labels is not None:
        l2 = plt.legend(n, labels, prop=legend_properties, loc=2, borderaxespad=0, borderpad = 0.2, ncol=2)
    axe.add_artist(l1)
    return axe

#print(base_simulation_df.head())

#print(lm_simulation_df.head())



plot_clustered_stacked([base_simulation_df, ckpt_simulation_df, lm_simulation_df, pckpt_simulation_df, plm_simulation_df],
                       ["B", "M1", "M2", "P1", "P2"])

plt.xlabel('Scientific Applications', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.ylabel('Overhead (percentage)', fontsize=15, fontname = 'Times New Roman', fontweight='normal')
plt.yticks(fontsize=15, fontname='Times New Roman', fontweight='normal')
plt.tight_layout()
plt.savefig('overhead_2_all_sys18.png',dpi=400)
