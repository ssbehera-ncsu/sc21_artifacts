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

ckpt_lm_simulation_data_1x = [[1.5331383858716796,11.198570387752184,0.03160938967140658,96.60770683708841,8.679,160.728,2.33824485095873,1657.0938207777347],
[0.5624097249731803,2.9735188394263403,0.004962481248134216,98.5572817143829,3.925,169.844,1.4781284752823336,618.3339712438127],
[0.27648241395467094,0.017371795052095188,0.0006584978497769607,99.8777719321299,1.286,206.163,1.2217503444899473,102.69013633011345],
[0.011364900898174468,0.0015050771428579473,3.1866281868103696e-06,99.98930313045351,0.159,216.515,0.5803195073878339,2.108969089332156],
[0.008624113968291413,0.012907033765837506,6.617764945279606e-06,99.99552716140329,0.635,315.961,1.6022448531003686,0.4002676515043398],
[0.0020575796767972106,0.002560116592612136,3.340435646848605e-07,99.99935918925647,0.51,1199.445,0.6448138142851466,0.03238729909914322]]

ckpt_lm_simulation_data_2_4x = [[0.08221417393253232,1.3262119385558757,0.00017481860862177711,99.65740679350539,0.048,8.619,47.6317483697383,84.78305792579617],
[0.03179871287130817,0.2529191883235081,2.2757875787640104e-05,99.894378913559,0.018,9.603,29.015558067419832,32.79899511029427],
[0.015159641678403328,0.09358060730099693,4.096409640922616e-06,99.95840898093873,0.008,11.304,23.813206405560937,5.446406922506635],
[0.000683736457516396,0.0,0.0,99.99945593464241,0.0,13.026,10.33701438730702,0.12146604263813497],
[0,0.02153776549,0,99.98978315586169,0.004,17.03,32.26125770410599,0.020267440195005988],
[0,0.00461803031,0,99.998027617661,0.002,62.506,12.076596744418048,0.0016844657685869352]]

ckpt_lm_simulation_data_1_4x = [[0.08230002235640885,1.2885915832734125,0.00017117655427554724,99.67608819128519,0.047,8.628,47.6583424043397,84.88522528120723],
[0.03170268426844841,0.27377987202053805,1.8964896489698903e-05,99.88890769850724,0.015,9.574,29.02374342011959,32.75688152549408],
[0.015127455602652709,0.09995614942128124,3.584358435773538e-06,99.95614610862079,0.007,11.28,23.817996279225884,5.448360821336722],
[0.0006833165364615929,0.009078088589351666,4.008337342042978e-08,99.99262795594376,0.002,13.018,10.338856494264066,0.12142781437644225],
[0.0004642038297749398,0.01667880591659599,1.0421677075100888e-08,99.99666580058677,0.001,17.007,32.27570069369241,0.020260372205101053],
[0,0.00461803031,0,99.99882284251272,0.003,62.474,12.082271245313512,0.0016836244907865539]]

ckpt_lm_simulation_data_3_4x = [[0.0821187867948916,0.9739014272755472,0.00014204011950506157,99.74454493071781,0.039,8.609,47.662640796980746,84.83512574925362],
[0.031851694169437395,0.2516885082198674,2.1493549354975273e-05,99.89588842557343,0.017,9.619,29.03634710793146,32.810267586057805],
[0.015131478862121626,0.08313616395509839,2.5602560255890694e-06,99.9631485529315,0.005,11.283,23.8124804340707,5.450422475615283],
[0.0006837364575164173,0.010061077871660945,6.012506013064466e-08,99.99165511319812,0.003,13.026,10.33333706595524,0.12147426024832926],
[0,0.02153776549,0,99.99583463864607,0.001,17.011,32.299496676899196,0.020250977152944077],
[0,0.00461803031,0,99.99411862322923,0.008,62.431,12.089683755451848,0.0016825248855167445]]


ckpt_lm_simulation_data_1x_s = [[1.5331383858716796,11.198570387752184,0.03160938967140658,96.60770683708841,8.679,160.728,2.33824485095873,1657.0938207777347],
[0.5624097249731803,2.9735188394263403,0.004962481248134216,98.5572817143829,3.925,169.844,1.4781284752823336,618.3339712438127],
[0.27648241395467094,0.017371795052095188,0.0006584978497769607,99.8777719321299,1.286,206.163,1.2217503444899473,102.69013633011345],
[0.011364900898174468,0.0015050771428579473,3.1866281868103696e-06,99.98930313045351,0.159,216.515,0.5803195073878339,2.108969089332156],
[0.008624113968291413,0.012907033765837506,6.617764945279606e-06,99.99552716140329,0.635,315.961,1.6022448531003686,0.4002676515043398],
[0.0020575796767972106,0.002560116592612136,3.340435646848605e-07,99.99935918925647,0.51,1199.445,0.6448138142851466,0.03238729909914322]]

ckpt_lm_simulation_data_2_4x_s = [[0.08221417393253232,1.3262119385558757,0.00017481860862177711,99.65740679350539,0.048,8.619,47.6317483697383,84.78305792579617],
[0.03179871287130817,0.2529191883235081,2.2757875787640104e-05,99.894378913559,0.018,9.603,29.015558067419832,32.79899511029427],
[0.015159641678403328,0.09358060730099693,4.096409640922616e-06,99.95840898093873,0.008,11.304,23.813206405560937,5.446406922506635],
[0.000683736457516396,0.0,0.0,99.99945593464241,0.0,13.026,10.33701438730702,0.12146604263813497],
[0.0004648316117521638,0.05205187112921706,4.168670830040355e-08,99.98978315586169,0.004,17.03,32.26125770410599,0.020267440195005988],
[0.00010722548773476958,0.014340293014320707,1.3099747775413561e-09,99.998027617661,0.002,62.506,12.076596744418048,0.0016844657685869352]]

ckpt_lm_simulation_data_1_4x_s = [[0.08230002235640885,1.2885915832734125,0.00017117655427554724,99.67608819128519,0.047,8.628,47.6583424043397,84.88522528120723],
[0.03170268426844841,0.27377987202053805,1.8964896489698903e-05,99.88890769850724,0.015,9.574,29.02374342011959,32.75688152549408],
[0.015127455602652709,0.09995614942128124,3.584358435773538e-06,99.95614610862079,0.007,11.28,23.817996279225884,5.448360821336722],
[0.0006833165364615929,0.009078088589351666,4.008337342042978e-08,99.99262795594376,0.002,13.018,10.338856494264066,0.12142781437644225],
[0.0004642038297749398,0.01667880591659599,1.0421677075100888e-08,99.99666580058677,0.001,17.007,32.27570069369241,0.020260372205101053],
[0.00010717059355434344,0.008511972661831704,1.9649621512130013e-09,99.99882284251272,0.003,62.474,12.082271245313512,0.0016836244907865539]]

ckpt_lm_simulation_data_3_4x_s = [[0.0821187867948916,0.9739014272755472,0.00014204011950506157,99.74454493071781,0.039,8.609,47.662640796980746,84.83512574925362],
[0.031851694169437395,0.2516885082198674,2.1493549354975273e-05,99.89588842557343,0.017,9.619,29.03634710793146,32.810267586057805],
[0.015131478862121626,0.08313616395509839,2.5602560255890694e-06,99.9631485529315,0.005,11.283,23.8124804340707,5.450422475615283],
[0.0006837364575164173,0.010061077871660945,6.012506013064466e-08,99.99165511319812,0.003,13.026,10.33333706595524,0.12147426024832926],
[0.0004643130092491674,0.021867183495859022,1.0421677075100888e-08,99.99583463864607,0.001,17.011,32.299496676899196,0.020250977152944077],
[0.00010709682949916477,0.043069098475980026,5.239899024900296e-09,99.99411862322923,0.008,62.431,12.089683755451848,0.0016825248855167445]]


ckpt_time_lm_1x = []
recomputation_time_lm_1x = []
recovery_time_lm_1x = []

ckpt_time_lm_1_4x = []
recomputation_time_lm_1_4x = []
recovery_time_lm_1_4x = []

ckpt_time_lm_2_4x = []
recomputation_time_lm_2_4x = []
recovery_time_lm_2_4x = []

ckpt_time_lm_3_4x = []
recomputation_time_lm_3_4x = []
recovery_time_lm_3_4x = []

index = 0
for app in applications:
    base_total_time = ckpt_lm_simulation_data_1x[index][0] + ckpt_lm_simulation_data_1x[index][1] + ckpt_lm_simulation_data_1x[index][2]
    ckpt_time_lm_1x.append(ckpt_lm_simulation_data_1x[index][0] / base_total_time * 100)
    recomputation_time_lm_1x.append(ckpt_lm_simulation_data_1x[index][1] / base_total_time * 100)
    recovery_time_lm_1x.append(ckpt_lm_simulation_data_1x[index][2] / base_total_time * 100)
    ckpt_time_lm_1_4x.append(ckpt_lm_simulation_data_1_4x[index][0] / base_total_time * 100)
    recomputation_time_lm_1_4x.append(ckpt_lm_simulation_data_1_4x[index][1] / base_total_time * 100)
    recovery_time_lm_1_4x.append(ckpt_lm_simulation_data_1_4x[index][2] / base_total_time * 100)
    ckpt_time_lm_2_4x.append(ckpt_lm_simulation_data_2_4x[index][0] / base_total_time * 100)
    recomputation_time_lm_2_4x.append(ckpt_lm_simulation_data_2_4x[index][1] / base_total_time * 100)
    recovery_time_lm_2_4x.append(ckpt_lm_simulation_data_2_4x[index][2] / base_total_time * 100)
    ckpt_time_lm_3_4x.append(ckpt_lm_simulation_data_3_4x[index][0] / base_total_time * 100)
    recomputation_time_lm_3_4x.append(ckpt_lm_simulation_data_3_4x[index][1] / base_total_time * 100)
    recovery_time_lm_3_4x.append(ckpt_lm_simulation_data_3_4x[index][2] / base_total_time * 100)
    index += 1

lm_simulation_1x_df = pd.DataFrame()
lm_simulation_1x_df['Recomputation Time'] = pd.Series(recomputation_time_lm_1x)
lm_simulation_1x_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_1x)
lm_simulation_1x_df['Recovery Time'] = pd.Series(recovery_time_lm_1x)
lm_simulation_1x_df['Applications'] = pd.Series(applications)

lm_simulation_1x_df.set_index('Applications', inplace=True)


lm_simulation_1_4x_df = pd.DataFrame()
lm_simulation_1_4x_df['Recomputation Time'] = pd.Series(recomputation_time_lm_1_4x)
lm_simulation_1_4x_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_1_4x)
lm_simulation_1_4x_df['Recovery Time'] = pd.Series(recovery_time_lm_1_4x)
lm_simulation_1_4x_df['Applications'] = pd.Series(applications)

lm_simulation_1_4x_df.set_index('Applications', inplace=True)

lm_simulation_2_4x_df = pd.DataFrame()
lm_simulation_2_4x_df['Recomputation Time'] = pd.Series(recomputation_time_lm_2_4x)
lm_simulation_2_4x_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_2_4x)
lm_simulation_2_4x_df['Recovery Time'] = pd.Series(recovery_time_lm_2_4x)
lm_simulation_2_4x_df['Applications'] = pd.Series(applications)

lm_simulation_2_4x_df.set_index('Applications', inplace=True)

lm_simulation_3_4x_df = pd.DataFrame()
lm_simulation_3_4x_df['Recomputation Time'] = pd.Series(recomputation_time_lm_3_4x)
lm_simulation_3_4x_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_3_4x)
lm_simulation_3_4x_df['Recovery Time'] = pd.Series(recovery_time_lm_3_4x)
lm_simulation_3_4x_df['Applications'] = pd.Series(applications)

lm_simulation_3_4x_df.set_index('Applications', inplace=True)

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
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col) - 0.2)
                if i == 3:
                    H = '//'
                elif i == 6:
                    H = '\\'
                elif i == 9:
                    H = '-'
                rect.set_hatch(H * int(i / n_col)) #edited part
                rect.set_width(1 / float(n_df + 1))
                overhead = 0
                base_total_time = ckpt_lm_simulation_data_1x[app_index][0] + ckpt_lm_simulation_data_1x[app_index][1] + \
                                  ckpt_lm_simulation_data_1x[app_index][2]
                if j == 2:
                    if i == 0:
                        for k in range(0, n_col):
                            overhead += ckpt_lm_simulation_data_1x_s[app_index][k]
                            #overhead += dfall[0].iloc[app_index][k] * base_total_time / 100
                    if i == 3:
                        for k in range(0, n_col):
                            overhead += ckpt_lm_simulation_data_3_4x_s[app_index][k]
                            #overhead += dfall[1].iloc[app_index][k] * base_total_time / 100
                    if i == 6:
                        for k in range(0, n_col):
                            overhead += ckpt_lm_simulation_data_2_4x_s[app_index][k]
                            #overhead += dfall[2].iloc[app_index][k] * base_total_time / 100
                    if i == 9:
                        for k in range(0, n_col):
                            overhead += ckpt_lm_simulation_data_1_4x_s[app_index][k]
                            #overhead += dfall[3].iloc[app_index][k] * base_total_time / 100
                    overhead = round(overhead, 2)
                    if rect.get_y() == 0.0 and applications[app_index] == 'POP':
                        axe.text(rect.get_x(), 70, str(overhead) + ' hrs', fontsize=15,
                                 fontname='Times New Roman', rotation=70)
                    elif rect.get_y() == 0.0 :
                        axe.text(rect.get_x(), 100, str(overhead) + ' hrs', fontsize=15,
                                 fontname='Times New Roman', rotation=70)
                    else:
                        axe.text(rect.get_x(), rect.get_y() + rect.get_width(), str(overhead) +  ' hrs', fontsize=15, fontname='Times New Roman', rotation=75)
                    print(applications[app_index], i, overhead, rect.get_y())
                app_index += 1

    axe.set_xticklabels(df.index, rotation=0, fontsize=15, fontname='Times New Roman', fontweight='normal')
    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_ylim(0, 170)
    axe.set_yticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    # Add invisible data to add another legend
    n=[]
    for i in range(n_df):
        if i == 1:
            H = '//'
        elif i == 2:
            H = '\\'
        elif i == 3:
            H = '-'
        #else:
           # H = '--'
        n.append(axe.bar(0, 0, color="gray", hatch= H * i))

    legend_properties = {'size': '10', 'family':'Times New Roman'}
    l1 = axe.legend(h[:n_col], l[:n_col], prop=legend_properties, loc=1, borderaxespad=0, borderpad = 0.2)
    if labels is not None:
        l2 = plt.legend(n, labels, prop=legend_properties, loc=2, borderaxespad=0, borderpad = 0.2)
    axe.add_artist(l1)
    return axe
#
#,
#print(base_simulation_df.head())

#print(lm_simulation_df.head())

plot_clustered_stacked([lm_simulation_1x_df, lm_simulation_3_4x_df, lm_simulation_2_4x_df, lm_simulation_1_4x_df],
                       ["Transfer Size = 512GB", "Transfer Size = 384GB", "Transfer Size = 256GB", "Transfer Size = 128GB"])

plt.xlabel('Scientific Applications', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.ylabel('Overhead (percentage)', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.yticks(fontsize=15, fontname='Times New Roman', fontweight='normal')
#plt.yscale('log')
plt.tight_layout()
plt.savefig('overhead.png',dpi=400)
