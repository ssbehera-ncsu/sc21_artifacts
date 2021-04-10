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
from matplotlib.lines import Line2D


#col_list = ['computation time', 'checkpoint time', 'waste time', 'restart time', 'wallclock time', 'efficiency',
#             'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'pct. of checkpoints to BB', 'daily write workloads to Burst Buffers']

base_simulation_data = [[11.66334334776059,22.27970177855433,0.35048017820480626,91.34025287404243,24.392,309.93,1.1917206930958053,12096.088965243478],
[3.850918801029999,5.406087261961279,0.056329795346651605,96.27861466925067,11.293,294.776,0.8360953565575328,4152.060573635537],
[1.4172102329621803,1.791977080827532,0.007763425767250589,98.68219992550961,3.843,267.86,0.9208692891823053,520.5987262626995],
[0.07086778699236125,0.08378470087181104,4.0166834687451584e-05,99.8715933336118,0.508,342.217,0.36071208366649493,13.147690451118716],
[0.18897506081349869,0.25179545236673395,7.64340073899965e-05,99.90829603731854,1.859,1754.906,0.28375550112558623,8.778098396131735],
[0.045078102758853586,0.07918580906827347,1.2154279080843988e-05,99.98274537817224,1.416,6660.697,0.11524480671938822,0.7097806223545494]]

pckpt_simulation_data_100 = [
[11.416277428771643,5.855953547339879,2.461130031154344,94.81716275473445,26.125,318.71,1.1887377698982449,12010.005202488308],
[3.8127756433574165,0.8201716128345485,0.2923675599771424,97.99353328034206,11.623,300.094,0.8346274891158644,4150.633129240187],
[1.4134710861167468,0.2629740270395255,0.026959297542271266,99.29689889799384,3.842,269.879,0.9193129528895084,521.2982022455964],
[0.07095440634869969,0.013216860104415704,0.00014244536707046086,99.92991983850438,0.51,342.965,0.36018986316464197,13.16722530980595],
[0.18789581057906887,0.038359352818988196,0.00035286385731381973,99.9528337944477,1.839,1745.958,0.285815747730592,8.729442222637118],
[0.04491759737954553,0.010138126087550527,5.86137110900411e-05,99.99234680276594,1.468,6636.638,0.1157009410912283,0.7071474858195385]
]

lm_simulation_data_100_1x = [
[5.522974853689591,12.324973082224023,0.11374225527506364,95.28730269356404,7.916,146.762,2.531154568144377,5930.737141339979],
[1.3026780306521264,2.3089346405967857,0.00882382077111723,98.52911484250782,1.769,99.716,2.492396352413131,1429.5675993494308],
[0.47480722585028323,0.8446451978317544,0.0011716853877192946,99.45859898842293,0.58,89.741,2.7738086620051847,175.0490033817969],
[0.023218712142176114,0.03611866657072042,4.665045760944508e-06,99.95100133271849,0.059,112.122,1.1103618864887865,4.29661592345725],
[0.06010837966283847,0.12789788414525066,1.184130937511263e-05,99.96092424501842,0.288,558.193,0.8918105490093915,2.7913158876969484],
[0.012038363611744811,0.025509866733708406,1.133026015917249e-06,99.99478834269136,0.132,1778.777,0.4255265336407898,0.1895235017177308]
]

lm_simulation_data_100_15x = [
[6.573402056174179,14.339613314291825,0.1551814498447061,94.50963573585052,10.8,174.675,2.123353503058577,7008.1123886411815],
[1.3470821646545545,2.3041617987955085,0.008998401736063017,98.51247659987648,1.804,103.115,2.406700796681769,1478.53252755399],
[0.488452358347895,0.7767458928113596,0.0011312824433152575,99.48059447752196,0.56,92.32,2.6910900414975,180.1314849736522],
[0.02368920779857661,0.03418881465938466,4.8231829053825285e-06,99.95219606820865,0.061,114.394,1.0878995523185626,4.385034100838373],
[0.06230749955409954,0.1125233252368654,1.0690070963645826e-05,99.9636581355527,0.26,578.615,0.8599975430577979,2.8936130058481617],
[0.012737407155345833,0.034054112255716446,1.4248660505429278e-06,99.99350542068149,0.166,1882.067,0.40334226328435163,0.200526226155481]
]

lm_simulation_data_100_2x = [
[7.516728057846552,15.954568966912378,0.19343080350087236,93.87106376076811,13.462,199.742,1.856274888169772,7970.592280167269],
[1.376345259731179,2.265808211716204,0.009023341873912426,98.51601968397921,1.809,105.355,2.353250270603658,1510.9992012692546],
[0.4989494280940204,0.839003245267659,0.0012545114237478396,99.45115773968,0.621,94.304,2.6314955527668826,183.9820907153548],
[0.024175234781662433,0.03912596655320817,5.851074344235485e-06,99.94770681660263,0.074,116.741,1.065110169544155,4.474679682623347],
[0.06373226477207192,0.11914497516433918,1.1923540690215285e-05,99.9619816191887,0.29,591.846,0.8410379524600008,2.9598507985482576],
[0.01321098225418328,0.027542910968320084,1.2102777896131344e-06,99.99434347302851,0.141,1952.042,0.3899133751249635,0.2079845727995266]
]

lm_simulation_data_100_25x = [
[7.567606773060209,16.162914949899303,0.19749713223291623,93.80571506150733,13.745,201.094,1.843310785810704,8023.015783136346],
[1.6762397287396662,2.746567079487289,0.013377889942417433,98.19917150036859,2.682,128.311,1.931249473577974,1836.6473933820628],
[0.5044201791613049,0.746791981871681,0.0011777458293799619,99.4859706693622,0.583,95.338,2.602157185765969,186.1013968823675],
[0.024494558858320966,0.030116815999695148,5.297594338699696e-06,99.9548526914566,0.067,118.283,1.0504786206087064,4.5342102883607],
[0.06421436543575805,0.1157005966579832,1.11834588542703e-05,99.96260120147286,0.272,596.323,0.8349624983090852,2.9821932271227483],
[0.013495797323207138,0.02953044982034259,1.2446119112965448e-06,99.99402790923033,0.145,1994.126,0.38213909197178897,0.21247066968190112]
]

lm_simulation_data_100_3x = [
[7.602378912747646,15.844405424700012,0.1817490888042295,93.8795463837635,12.649,202.018,1.8352637771747817,8064.016420850707],
[2.0014650644238534,3.2991675097781377,0.01848563017397426,97.84733734012049,3.706,153.206,1.6154357617935444,2186.417424125863],
[0.5107004320789706,0.7958901782787587,0.0012302696571052493,99.46357676564534,0.609,96.525,2.5697245217232694,188.39639774604655],
[0.024702264467199312,0.035462667385417666,4.744114333163796e-06,99.95025276334071,0.06,119.286,1.0418476871679825,4.573401390961334],
[0.0646064423882854,0.10945350094734159,1.0690070963640386e-05,99.96381583334387,0.26,599.964,0.8298657642754464,3.0005058546262893],
[0.013713415148182214,0.034621201040903986,1.5278684156676548e-06,99.99329099084999,0.178,2026.281,0.3761554483373362,0.2158966678762128]
]

lm_simulation_data_100_35x = [
[7.640425052600465,15.969118215698453,0.19539930892945584,93.83631050645437,13.599,203.029,1.82592637681015,8102.835187017039],
[2.238966434286822,3.6148375449788372,0.023024735262564777,97.6249838808323,4.616,171.386,1.4442597326375621,2441.897569634421],
[0.5154198807753114,0.835196348151724,0.0013231964292345954,99.44545148826435,0.655,97.417,2.5469683112441412,190.0471147010223],
[0.024970231623617476,0.03138617507424941,5.4557314831383816e-06,99.95338941376818,0.069,120.58,1.0297082218297553,4.6227328839204445],
[0.06493520122819746,0.10072502053989289,1.1183458854270966e-05,99.96555677470614,0.272,603.017,0.8263544194976763,3.015869129583279],
[0.013864593719829144,0.03040299115165927,1.4506166417200816e-06,99.99385544168487,0.169,2048.619,0.37262278039832386,0.2182772981035197]
]

lm_simulation_data_100_4x = [
[7.658827191461038,15.9712872546062,0.19692238612237772,93.83118829261065,13.705,203.518,1.8206295600461635,8119.584754895737],
[2.2453546724530966,3.70901619390937,0.02342377746815517,97.58479615953219,4.696,171.875,1.4400858930749258,2447.5023213085515],
[0.5164515988199179,0.7056169072639384,0.001157544357177791,99.49738861285759,0.573,97.612,2.5388590070609416,190.5899715846087],
[0.024950351525460133,0.033346142310924726,5.139457194260455e-06,99.95181721606166,0.065,120.484,1.0309791215327528,4.6193172468752755],
[0.06523402395360821,0.10791550286775849,1.1759078060014638e-05,99.96399895984212,0.286,605.792,0.822210471074515,3.029743230178562],
[0.01401382993999854,0.03015010422288014,1.519284885130645e-06,99.99386959440092,0.177,2070.67,0.3685695419237879,0.22062832572042904]
]


ckpt_time_base = []
recomputation_time_base = []
recovery_time_base = []

ckpt_time_pckpt = []
recovery_time_pckpt = []
recomputation_time_pckpt = []

ckpt_time_lm_1x = []
recovery_time_lm_1x = []
recomputation_time_lm_1x = []

ckpt_time_lm_15x = []
recovery_time_lm_15x = []
recomputation_time_lm_15x = []

ckpt_time_lm_2x = []
recovery_time_lm_2x = []
recomputation_time_lm_2x = []

ckpt_time_lm_25x = []
recovery_time_lm_25x = []
recomputation_time_lm_25x = []

ckpt_time_lm_3x = []
recovery_time_lm_3x = []
recomputation_time_lm_3x = []

ckpt_time_lm_35x = []
recovery_time_lm_35x = []
recomputation_time_lm_35x = []

ckpt_time_lm_4x = []
recovery_time_lm_4x = []
recomputation_time_lm_4x = []


applications = ['CHIMERA', 'XGC', 'POP']
indices = [0, 1, 4]

tmpindex = 0
for app in applications:
    index = indices [tmpindex]
    base_total_time = base_simulation_data[index][0] + base_simulation_data[index][1] + base_simulation_data[index][2]
    #print (base_total_time)
    ckpt_time_base.append(base_simulation_data[index][0] / base_total_time * 100)
    ckpt_time_pckpt.append(pckpt_simulation_data_100[index][0] / base_total_time * 100)
    ckpt_time_lm_1x.append(lm_simulation_data_100_1x[index][0] / base_total_time * 100)
    ckpt_time_lm_15x.append(lm_simulation_data_100_15x[index][0] / base_total_time * 100)
    ckpt_time_lm_2x.append(lm_simulation_data_100_2x[index][0] / base_total_time * 100)
    ckpt_time_lm_25x.append(lm_simulation_data_100_25x[index][0] / base_total_time * 100)
    ckpt_time_lm_3x.append(lm_simulation_data_100_3x[index][0] / base_total_time * 100)
    ckpt_time_lm_35x.append(lm_simulation_data_100_35x[index][0] / base_total_time * 100)
    ckpt_time_lm_4x.append(lm_simulation_data_100_4x[index][0] / base_total_time * 100)

    recomputation_time_base.append(base_simulation_data[index][1] / base_total_time * 100)
    recomputation_time_pckpt.append(pckpt_simulation_data_100[index][1] / base_total_time * 100)
    recomputation_time_lm_1x.append(lm_simulation_data_100_1x[index][1] / base_total_time * 100)
    recomputation_time_lm_15x.append(lm_simulation_data_100_15x[index][1] / base_total_time * 100)
    recomputation_time_lm_2x.append(lm_simulation_data_100_2x[index][1] / base_total_time * 100)
    recomputation_time_lm_25x.append(lm_simulation_data_100_25x[index][1] / base_total_time * 100)
    recomputation_time_lm_3x.append(lm_simulation_data_100_3x[index][1] / base_total_time * 100)
    recomputation_time_lm_35x.append(lm_simulation_data_100_35x[index][1] / base_total_time * 100)
    recomputation_time_lm_4x.append(lm_simulation_data_100_4x[index][1] / base_total_time * 100)

    recovery_time_base.append(base_simulation_data[index][2] / base_total_time * 100)
    recovery_time_pckpt.append(pckpt_simulation_data_100[index][2] / base_total_time * 100)
    recovery_time_lm_1x.append(lm_simulation_data_100_1x[index][2] / base_total_time * 100)
    recovery_time_lm_15x.append(lm_simulation_data_100_15x[index][2] / base_total_time * 100)
    recovery_time_lm_2x.append(lm_simulation_data_100_2x[index][2] / base_total_time * 100)
    recovery_time_lm_25x.append(lm_simulation_data_100_25x[index][2] / base_total_time * 100)
    recovery_time_lm_3x.append(lm_simulation_data_100_3x[index][2] / base_total_time * 100)
    recovery_time_lm_35x.append(lm_simulation_data_100_35x[index][2] / base_total_time * 100)
    recovery_time_lm_4x.append(lm_simulation_data_100_4x[index][2] / base_total_time * 100)

    tmpindex += 1


#print (ckpt_time_base, ckpt_time_pckpt, ckpt_time_lm_3x)
#print (recomputation_time_base, recomputation_time_pckpt, recomputation_time_lm_3x)
#print (recovery_time_base, recovery_time_pckpt, recovery_time_lm_3x)

base_simulation_df = pd.DataFrame()

base_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_base)
base_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_base)
base_simulation_df['Recovery Time'] = pd.Series(recovery_time_base)
base_simulation_df['Applications'] = pd.Series(applications)

base_simulation_df.set_index('Applications', inplace=True)

pckpt_simulation_df = pd.DataFrame()
pckpt_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_pckpt)
pckpt_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_pckpt)
pckpt_simulation_df['Recovery Time'] = pd.Series(recovery_time_pckpt)
pckpt_simulation_df['Applications'] = pd.Series(applications)

pckpt_simulation_df.set_index('Applications', inplace=True)


lm_1x_simulation_df = pd.DataFrame()
lm_1x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_1x)
lm_1x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_1x)
lm_1x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_1x)
lm_1x_simulation_df['Applications'] = pd.Series(applications)

lm_1x_simulation_df.set_index('Applications', inplace=True)


lm_15x_simulation_df = pd.DataFrame()
lm_15x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_15x)
lm_15x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_15x)
lm_15x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_15x)
lm_15x_simulation_df['Applications'] = pd.Series(applications)

lm_15x_simulation_df.set_index('Applications', inplace=True)


lm_2x_simulation_df = pd.DataFrame()
lm_2x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_2x)
lm_2x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_2x)
lm_2x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_2x)
lm_2x_simulation_df['Applications'] = pd.Series(applications)

lm_2x_simulation_df.set_index('Applications', inplace=True)


lm_25x_simulation_df = pd.DataFrame()
lm_25x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_25x)
lm_25x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_25x)
lm_25x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_25x)
lm_25x_simulation_df['Applications'] = pd.Series(applications)

lm_25x_simulation_df.set_index('Applications', inplace=True)


lm_3x_simulation_df = pd.DataFrame()
lm_3x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_3x)
lm_3x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_3x)
lm_3x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_3x)
lm_3x_simulation_df['Applications'] = pd.Series(applications)

lm_3x_simulation_df.set_index('Applications', inplace=True)


lm_35x_simulation_df = pd.DataFrame()
lm_35x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_35x)
lm_35x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_35x)
lm_35x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_35x)
lm_35x_simulation_df['Applications'] = pd.Series(applications)

lm_35x_simulation_df.set_index('Applications', inplace=True)


lm_4x_simulation_df = pd.DataFrame()
lm_4x_simulation_df['Recomputation Time'] = pd.Series(recomputation_time_lm_4x)
lm_4x_simulation_df['Checkpoint Time'] = pd.Series(ckpt_time_lm_4x)
lm_4x_simulation_df['Recovery Time'] = pd.Series(recovery_time_lm_4x)
lm_4x_simulation_df['Applications'] = pd.Series(applications)

lm_4x_simulation_df.set_index('Applications', inplace=True)

models_ann = ["B", "P1", "M2 - 1x", "M2 - 1.5x", "M2 - 2x", "M2 - 2.5x", "M2 - 3x", "M2 - 3.5x", "M2 - 4x"]


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
        axe = df.plot(kind="barh",
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
                rect.set_y (rect.get_y() + 1 / float(n_df + 1) * i / float(n_col) - 0.2)
                rect.set_hatch(H * int(i / n_col))  # edited part
                rect.set_height(1 / float(n_df + 1))

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
                    #print(overhead)
                    print (rect.get_x() + 1, rect.get_y(), rect.get_width(), rect.get_height())
                    axe.text(rect.get_x () + rect.get_width () + 0.3, rect.get_y(), models_ann[int(i / 3)], fontsize=15,
                             fontname='Times New Roman', rotation=0, fontweight='normal')

                app_index += 1
                '''
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
                    axe.text(rect.get_x(), rect.get_y() + 3 + rect.get_width(), models_ann[int(i/3)], fontsize=15,
                             fontname='Times New Roman', rotation=70, fontweight='normal')
                app_index += 1
                '''

    axe.set_yticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_yticklabels(df.index, rotation = 75, fontsize=15, fontname='Times New Roman', fontweight='normal')
    axe.set_xlim(0,130)
    axe.set_xticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    #axe.set_xticks(fontsize=15, fontname ='Times New Roman')


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
    axe.add_artist(l1)

    return axe

#print(base_simulation_df.head())

#print(lm_simulation_df.head())



plot_clustered_stacked([base_simulation_df, pckpt_simulation_df, lm_1x_simulation_df, lm_15x_simulation_df, lm_2x_simulation_df, lm_25x_simulation_df, lm_3x_simulation_df, lm_35x_simulation_df, lm_4x_simulation_df],
                       ["B", "P1", "M2", "P1", "P2"])

plt.ylabel('Scientific Applications', fontsize = 15, fontname = 'Times New Roman', fontweight='normal')
plt.xlabel('Overhead (percentage)', fontsize=15, fontname = 'Times New Roman', fontweight='normal')
plt.xticks(fontsize=15, fontname='Times New Roman', fontweight='normal')
plt.tight_layout()
plt.savefig('overhead_2_sizevar.png',dpi=400)



