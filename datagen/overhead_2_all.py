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

base_simulation_data = [[11.66334334776059,22.27970177855433,0.35048017820480626,91.34025287404243,24.392,309.93,1.1917206930958053,12096.088965243478],
[3.850918801029999,5.406087261961279,0.056329795346651605,96.27861466925067,11.293,294.776,0.8360953565575328,4152.060573635537],
[1.4172102329621803,1.791977080827532,0.007763425767250589,98.68219992550961,3.843,267.86,0.9208692891823053,520.5987262626995],
[0.07086778699236125,0.08378470087181104,4.0166834687451584e-05,99.8715933336118,0.508,342.217,0.36071208366649493,13.147690451118716],
[0.18897506081349869,0.25179545236673395,7.64340073899965e-05,99.90829603731854,1.859,1754.906,0.28375550112558623,8.778098396131735],
[0.045078102758853586,0.07918580906827347,1.2154279080843988e-05,99.98274537817224,1.416,6660.697,0.11524480671938822,0.7097806223545494]]

ckpt_simulation_data = [
[11.608099298993096,21.83397395411351,0.40474144321089606,91.44442698237295,27.079,308.584,1.1932023948632042,12039.77985601512],
[3.8464117618329263,5.23747178702085,0.0703759863829107,96.33968738884694,11.674,294.9,0.8366371311060413,4147.583705225446],
[1.4110675424504557,0.7277649188766672,0.021039833298398057,99.11060727562177,3.814,268.921,0.9213926828808923,520.3756726732136],
[0.07070232659207043,0.01431958547242002,0.00012703937972183087,99.92922115195398,0.458,341.803,0.3614119822996988,13.125307485941674],
[0.1886567473085511,0.044346896820652036,0.00037357553822946486,99.95142545902284,1.971,1753.594,0.28421246268409267,8.767097181703868],
[0.045081567860024915,0.01337832423917571,5.785141345524414e-05,99.99187427812039,1.505,6662.466,0.1151818224192784,0.7098985301507783]
]

ckpt_lm_simulation_data = [
[7.602378912747646,15.844405424700012,0.1817490888042295,93.8795463837635,12.649,202.018,1.8352637771747817,8064.016420850707],
[2.0014650644238534,3.2991675097781377,0.01848563017397426,97.84733734012049,3.706,153.206,1.6154357617935444,2186.417424125863],
[0.5107004320789706,0.7958901782787587,0.0012302696571052493,99.46357676564534,0.609,96.525,2.5697245217232694,188.39639774604655],
[0.024702264467199312,0.035462667385417666,4.744114333163796e-06,99.95025276334071,0.06,119.286,1.0418476871679825,4.573401390961334],
[0.0646064423882854,0.10945350094734159,1.0690070963640386e-05,99.96381583334387,0.26,599.964,0.8298657642754464,3.0005058546262893],
[0.013713415148182214,0.034621201040903986,1.5278684156676548e-06,99.99329099084999,0.178,2026.281,0.3761554483373362,0.2158966678762128]
]


pckpt_simulation_data = [
[11.416277428771643,5.855953547339879,2.461130031154344,94.81716275473445,26.125,318.71,1.1887377698982449,12010.005202488308],
[3.8127756433574165,0.8201716128345485,0.2923675599771424,97.99353328034206,11.623,300.094,0.8346274891158644,4150.633129240187],
[1.4134710861167468,0.2629740270395255,0.026959297542271266,99.29689889799384,3.842,269.879,0.9193129528895084,521.2982022455964],
[0.07095440634869969,0.013216860104415704,0.00014244536707046086,99.92991983850438,0.51,342.965,0.36018986316464197,13.16722530980595],
[0.18789581057906887,0.038359352818988196,0.00035286385731381973,99.9528337944477,1.839,1745.958,0.285815747730592,8.729442222637118],
[0.04491759737954553,0.010138126087550527,5.86137110900411e-05,99.99234680276594,1.468,6636.638,0.1157009410912283,0.7071474858195385]
]

pckpt_lm_simulation_data = [
[6.722018599513435,8.575442753988764,0.7354860687477467,95.7897882825459,11.825,182.718,1.8290483808494908,8057.418182586629],
[1.8873616829369295,1.4175635729415819,0.06454467255201282,98.62566299911563,3.537,146.092,1.6174942396166863,2183.6591865721534],
[0.5048206527944612,0.731101875089579,0.0013168473951134946,99.49262350356071,0.564,95.439,2.5768690719780043,187.97713277829772],
[0.02464241708836905,0.03608301578800316,5.692937199796048e-06,99.9498187425842,0.072,118.997,1.0457009328999938,4.556445251274958],
[0.06279332831982343,0.10726611439651626,1.0839944166968928e-05,99.96464586336458,0.255,583.128,0.8585652408036859,2.9153564572113826],
[0.013339143620354627,0.030617631495358212,3.97945203782335e-07,99.99389892402529,0.154,1970.979,0.3876808039345229,0.20997530715975973]
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

    tmp13 = (base_simulation_data[index][2] - pckpt_simulation_data[index][2]) / base_simulation_data[index][2]
    print('recovery:base to pckpt', tmp13)
    tmp14 = (base_simulation_data[index][2] - pckpt_lm_simulation_data[index][2]) / base_simulation_data[index][2]
    print('recovery:base to plm', tmp14)
    tmp15 = (tmp14 - tmp11)
    print('recomputation :pckpt to plm', tmp15)



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
plt.savefig('overhead_2_all.png',dpi=400)
