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



data = [67.23, .78, .76, .80, .74, .70]

apps = ['CHIMERA', 'XGC', 'S3D', 'GYRO', 'POP', 'VULCAN']

plt.plot(apps, data)
plt.yscale('log')
plt.title('log')
plt.show()
