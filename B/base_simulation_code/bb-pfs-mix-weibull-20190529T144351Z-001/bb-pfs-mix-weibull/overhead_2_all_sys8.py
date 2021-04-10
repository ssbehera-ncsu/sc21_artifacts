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
[3.8177099859438663,4.524004566260457,0.03232946871764859,97.75005812311555,2.25,101.448,3.6771902701191546,4153.972532041166],
[1.2711679479178444,1.3471044242604011,0.005362129637620716,98.92933048625392,1.075,97.304,2.5571746474966273,1398.5125631666604],
[0.46797143244704453,0.5429789830847503,0.0007737163853386995,99.5848205297142,0.383,88.449,2.8175719730618933,172.699419751432],
[0.024392673355271975,0.023984988219684023,4.111565755408497e-06,99.96001205702098,0.052,117.791,1.0555933719618658,4.511562863211909],
[0.06153357561634478,0.06408609203433,6.66073652350696e-06,99.97387606172613,0.162,571.428,0.8686176609252654,2.858222006196111],
[0.01525772679627513,0.02133153881035342,1.0214401205388412e-06,99.99492060430171,0.119,2254.467,0.33115372618347594,0.24023106856224988]
]

ckpt_simulation_data = [
[3.808414836049059,4.727836281095223,0.03601380929333114,97.69907410070815,2.415,101.213,3.6869026957081714,4142.145124132399],
[1.2715598643697643,1.2548549097104265,0.006540869352763717,98.96631104360951,1.055,97.386,2.555346699532823,1399.3769238831367],
[0.46800846847941313,0.21569641165982575,0.0020692079384065014,99.71749122317175,0.38,88.675,2.814851500414363,172.92911177425293],
[0.024443201938089514,0.005097084484362096,1.2736708561149834e-05,99.97553240851174,0.048,118.073,1.05280410394882,4.5226298547765715],
[0.06139304817252324,0.011016370064750309,3.416843773945194e-05,99.98492911676507,0.174,570.275,0.8706306593151197,2.8519547244907093],
[0.015238804095612523,0.0033680034251427626,4.599626401531998e-06,99.9974160203262,0.12,2251.771,0.3315391939835664,0.23993812400374212]
]

ckpt_lm_simulation_data = [
[2.5460431630886537,3.4855197582883686,0.01662453124725314,98.37440511018109,1.157,67.656,5.525859305797847,2776.615334970409],
[0.6837374420180466,0.8058652824644799,0.001626096987780794,99.39307914087603,0.326,52.338,4.765270570533486,753.643617697789],
[0.17570951928869818,0.22098798330282057,0.00010908794989111482,99.83918952265842,0.054,33.21,7.58323370459401,64.615316335536],
[0.008977935161808186,0.010874901887330174,7.11617149974586e-07,99.98381677106185,0.009,43.354,2.9114103812026997,1.6425146168611624],
[0.021617105165789904,0.023847210402941688,6.578505208381103e-07,99.99057184192564,0.016,200.746,2.469960955888941,1.0029637268301066],
[0.004791327962787168,0.007465396274762245,1.0300236511895377e-07,99.99830026077571,0.012,707.962,1.0493609885784454,0.0753909811442492]
]

pckpt_simulation_data = [
[3.805602651539957,1.3996693475007485,0.22705131053352706,98.52463168389451,2.44,102.58,3.667459863154252,4159.453934611092],
[1.2718964266314579,0.20420377309240062,0.02888131603312272,99.38083450922282,1.148,98.18,2.5460122222808974,1403.806998825857],
[0.46913730655269326,0.08246572144472125,0.0026805910649765775,99.7711697021627,0.381,88.941,2.8054343218285056,173.39422701533465],
[0.024484140214069743,0.004294071012364153,1.0850494428686242e-05,99.97615149311572,0.042,118.257,1.0512838359944323,4.529522935204092],
[0.06164164267836193,0.011291953741391714,2.763104818843809e-05,99.98482108789281,0.149,572.515,0.8671955659336436,2.8633700409110765],
[0.01527857880937447,0.0016888818317985406,5.819819427710593e-06,99.99764334645067,0.144,2257.514,0.330808906437881,0.24054945483927775]
]

pckpt_lm_simulation_data = [
[2.567355619338905,1.9961206849538367,0.0773233292491624,98.74389961813164,1.222,68.673,5.5036987891208735,2803.1925576431595],
[0.6872818107303813,0.41686850440408646,0.0064000607744852216,99.54622563552729,0.367,52.771,4.760445123909643,754.530764553795],
[0.17658333889521033,0.18541620094589706,0.00012106453698230468,99.85278482643275,0.057,33.376,7.576048910822404,64.69636909477151],
[0.008992480824476424,0.0036862409200921244,4.725061665167285e-07,99.98966322258232,0.003,43.425,2.907973872374632,1.644430809760109],
[0.021713051489506408,0.025650227486595293,7.811974934952559e-07,99.99017159695642,0.019,201.637,2.459902594944956,1.0069825601442055],
[0.004808937714965834,0.007800490376358752,3.876089643739533e-08,99.99825129316847,0.015,710.564,1.045644063728607,0.07566265224368346]
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
plt.savefig('overhead_2_all_sys8.png',dpi=400)
