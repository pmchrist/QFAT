# 1.5

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


# 1_5

df_spread_trade = pairs_price.copy()
# Find Relative Spread
df_spread_trade["spread_APMOLLER"] = (pairs_price["APMOLLER_B"] - pairs_price["APMOLLER_A"]) / pairs_price["APMOLLER_A"]
# Rolling 20-day, Spread Average and Volatility
window = 20
df_spread_trade["spread_APMOLLER_rolling_mean"] = df_spread_trade["spread_APMOLLER"].rolling(window).mean()
df_spread_trade["spread_APMOLLER_rolling_std"] = df_spread_trade["spread_APMOLLER"].rolling(window).std()
# Trading Based on Z-Score
df_spread_trade["spread_APMOLLER_rolling_z_score"] = (df_spread_trade["spread_APMOLLER"] - df_spread_trade["spread_APMOLLER_rolling_mean"]) / df_spread_trade["spread_APMOLLER_rolling_std"]

# Are we in trade?
df_spread_trade["Buy"] = df_spread_trade["spread_APMOLLER_rolling_z_score"] > 2 or df_spread_trade["spread_APMOLLER_rolling_z_score"] < -2

df_spread_trade.to_excel("output.xlsx") 

