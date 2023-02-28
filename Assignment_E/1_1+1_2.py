import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime
from matplotlib import pyplot as plt
from plotnine import * 

#1.1

pp = pd.read_csv("Pairs_Price.csv", index_col=['date'])
pr = pd.read_csv("Pairs_RI.csv", index_col=['date'])

pr2 = pr.pct_change(1)
lis2 = list(pr)
lisx = lis2[::2]
lisy = lis2[1::2]

coef = list()
for i in range(len(lisx)):
    reg = sm.OLS(pr2[lisx[i]], pr2[lisy[i]], missing = 'drop').fit(cov_type = 'HAC', cov_kwds = {'maxlags': 11})
    coef.append(reg.params[0])

xvalues = np.arange(0,8,1) 
plt.bar(xvalues, coef) 
plt.xticks(xvalues, lisy) 
plt.show() 

#1.2

