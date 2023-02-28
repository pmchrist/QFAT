# 1.3

# Imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

# Reading Data
pairs_price = pd.read_csv("Pairs_Price.csv")
pairs_ri = pd.read_csv("Pairs_RI.csv")
print(pairs_price.head())
print(pairs_ri.head())

# Init Prices
days = pd.to_datetime(pairs_price["date"], dayfirst = True)
spread_APMOLLER = []
spread_INDUSTRIVARDEN = []
spread_INVESTOR = []
spread_SVENSKAHANDBKN = []
spread_VOLVO = []
spread_VW = []
spread_HYUNDAI = []
spread_STORAENSO = []
# Finding Spreads
for i in range(len(pairs_price)):
    spread_APMOLLER.append(pairs_price.iloc[i]["APMOLLER_B"] / pairs_price.iloc[i]["APMOLLER_A"] - 1)
    spread_INDUSTRIVARDEN.append(pairs_price.iloc[i]["INDUSTRIVARDEN_A"] / pairs_price.iloc[i]["INDUSTRIVARDEN_C"] - 1)
    spread_INVESTOR.append(pairs_price.iloc[i]["INVESTOR_B"] / pairs_price.iloc[i]["INVESTOR_A"] - 1)
    spread_SVENSKAHANDBKN.append(pairs_price.iloc[i]["SVENSKAHANDBKN_A"] / pairs_price.iloc[i]["SVENSKAHANDBKN_B"] - 1)
    spread_VOLVO.append(pairs_price.iloc[i]["VOLVO_B"] / pairs_price.iloc[i]["VOLVO_A"] - 1)
    spread_VW.append(pairs_price.iloc[i]["VW_PREF"] / pairs_price.iloc[i]["VW"] - 1)
    spread_HYUNDAI.append(pairs_price.iloc[i]["HYUNDAI"] / pairs_price.iloc[i]["HYUNDAI_PREF"] - 1)
    spread_STORAENSO.append(pairs_price.iloc[i]["STORAENSO_R"] / pairs_price.iloc[i]["STORAENSO_A"] - 1)

# Visualization
plt.title("Spread")
plt.ylabel("Spread in Percents")
plt.xlabel("Day")
plt.plot(days, spread_APMOLLER, label="spread_APMOLLER")
plt.plot(days, spread_INDUSTRIVARDEN, label="spread_INDUSTRIVARDEN")
plt.plot(days, spread_INVESTOR, label="spread_INVESTOR")
plt.plot(days, spread_SVENSKAHANDBKN, label="spread_SVENSKAHANDBKN")
plt.plot(days, spread_VOLVO, label="spread_VOLVO")
plt.plot(days, spread_VW, label="spread_VW")
plt.plot(days, spread_HYUNDAI, label="spread_HYUNDAI")
plt.plot(days, spread_STORAENSO, label="spread_STORAENSO")
plt.legend()
plt.show()