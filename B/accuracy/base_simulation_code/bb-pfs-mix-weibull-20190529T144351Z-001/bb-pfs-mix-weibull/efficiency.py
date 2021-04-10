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

from matplotlib import rcParams

#applications = ['CHIMERA(360)', 'S3D(240)', 'GTC(120)', 'POP(480)', 'VULCAN(720)', 'GYRO(120)']
applications = ['CHIMERA', 'S3D', 'GTC', 'POP', 'VULCAN', 'GYRO']
#col_list = ['computation time', 'checkpoint time', 'waste time', 'restart time', 'wallclock time', 'efficiency',
#             'no. of failures', 'no. of checkpoints', 'checkpoint interval', 'pct. of checkpoints to BB', 'daily write workloads to Burst Buffers']

col_list = ['Efficiency']

base_simulation_data = [[2.1445317832936066,14.863989629246133,0.056120415421906385,95.50644452955376,15.409,224.824,1.6721258139222577,2301.315607432555],
[0.38281313845533044,0.988460865786781,0.0012263626362485468,99.4334465191436,2.395,285.45,0.8796969788528468,141.65384847100484],
[0.3018034679661008,1.3010696291453694,0.0023800140013951784,98.69025638632198,3.486,168.783,0.743128982072775,664.5542705677414],
[0.012079289495970194,0.6104253251550887,1.1359628016193946e-05,99.8708724554469,1.09,442.548,1.1428015337621522,0.5602294879673734],
[0.0028736605723847005,0.18325035358622668,5.252998798543352e-07,99.97417788080355,0.802,1675.171,0.4634980705155723,0.04522871800144629],
[0.01598550222493338,0.056113003672485,6.012506012843755e-06,99.94015675651914,0.3,304.543,0.41166241842703377,2.9667412112914535]]

ckpt_simulation_data = [[2.1472312392888404,14.56296503725838,0.05658659837823031,95.58113857518138,15.537,225.107,1.6696073243252407,2304.503724413456],
[0.38414349625301925,0.019201039562444778,0.001138801880173808,99.83208737229995,2.224,286.442,0.8803278129039712,142.70738045025394],
[0.30162286831883406,1.2293289924721953,0.0017068373504011828,98.74778827969298,2.5,168.682,0.7438439326081843,677.6385213144969],
[0.012097577057911204,0.007892691075868766,1.1380471370296546e-05,99.99584155534852,1.092,443.218,1.14311145133475,0.5617421814647761],
[0.002872324242192833,0.0027397869933722323,5.547743118958434e-07,99.99922088012379,0.847,1674.392,0.4641675552893034,0.04521935142907015],
[0.015981093053860623,0.0009483939591001093,5.711880712204437e-06,99.98591612608027,0.285,304.459,0.41207092649156174,2.967534896741006]]

ckpt_lm_simulation_data = [[1.4999532006864715,11.23820865648803,0.03106308151946518,96.60668254388975,8.529,157.249,2.394162489200063,1621.181055638619],
[0.26960666352254564,0.01215970936390138,0.000646208620854236,99.88281462189535,1.262,201.036,1.2558613788985455,100.11549227370963],
[0.21445761084063025,1.0165116087042385,0.0013265539887296644,98.99394398449898,1.943,119.935,1.0493359493718961,480.35756076579355],
[0.008471317294019856,0.009978337302481119,6.305114633072845e-06,99.9961671456846,0.605,310.363,1.6303487505564682,0.39311669883938855],
[0.002024586559296885,0.0031881286254286474,2.705097883454431e-07,99.99927658559056,0.413,1180.212,0.6535887203108435,0.03186742387314736],
[0.011348418996772533,0.0008547552509978211,2.785794452593443e-06,99.98985755080597,0.139,216.201,0.5812265372514422,2.105752906651371]]


efficiency_base = []
efficiency_ckpt = []
efficiency_lm = []

index = 0
for app in applications:
    efficiency_base.append(base_simulation_data[index][3])
    efficiency_lm.append(ckpt_lm_simulation_data[index][3])
    efficiency_ckpt.append(ckpt_simulation_data[index][3])
    index += 1

data = pd.DataFrame({'Base Model': efficiency_base, 'Failure Prediction Integrated Model' : efficiency_ckpt,
                     'Failure Prediction and Live Migration Integrated Model': efficiency_lm}, index = applications)

ax = data.plot.bar(rot=0, figsize=(6.4, 5.8), width=0.75)

print(plt.rcParams.get('figure.figsize'))

plt.margins(y = 0.15)

plt.xlabel('Scientific Applications', fontsize=10, fontname='Times New Roman')
plt.ylabel('Efficiency (%)', fontsize=10, fontname='Times New Roman')

legend_properties = {'family':'Times New Roman', 'size':10}

plt.legend(loc=[0, 1.01], prop=legend_properties)

plt.xticks(fontname = 'Times New Roman', fontsize = 10)
plt.yticks(fontname = 'TImes New Roman', fontsize = 10)

print(len(ax.patches))
index = 0

for patch in ax.patches:
    if index <= 5:
        index += 1
        continue
    if index <=11:
        improvement = efficiency_ckpt[index - 6] - efficiency_base[index - 6]
    else:
        improvement = efficiency_lm[index - 12] - efficiency_base[index - 12]
    improvement = round(improvement, 2)
    if improvement >= 0:
        sign = '+'
    else:
        sign = ''
    ax.text(patch.get_x(), patch.get_y() + patch.get_height() + 1.0, sign + str(improvement) + '%', fontsize=10, fontname='Times New Roman', rotation=70)
    index += 1

#plt.show()
plt.savefig('efficiency.png', dpi=600)

